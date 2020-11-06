#!/usr/bin/env python3

#### PYTHON IMPORTS ################################################################################
import csv
import os
from collections import OrderedDict


#### THIRD-PARTY IMPORTS ###########################################################################
import numpy as np


#### PACKAGE IMPORTS ###############################################################################

#### GLOBALS #######################################################################################
IGNORE_WORDS = [
    "vulnerability", "embargoed", "would", "could", "also", "every", "bug", "which", "cause",
    "used", "using", "VERVER", "NUMNUM", "HEXHEX", "another", "well", "even", "led", "however",
    "lead", "many", "much", "like", "one", "via", "sure", "caused", "secure", "security", "fix",
    "fixed", "made", "code", "issue", "coding", "mistake", "really", "possible", "given", "change",
    "changed", "given", "give", "may", "consider", "ensure", "something", "attacker", "attackers",
    "attack", "implement", "implementing", "interesting", "large", "due", "found", "simple",
    "seems", "able", "example", "system", "might", "occur", "developers", "add", "added",
    "implementation", "original", "first", "last", "add", "added", "introduce", "introduced",
    "still", "two", "allow", "allows", "result", "results", "user", "causes", "attempt", "attempts",
    "since", "malicious", "new", "information", "second", "allowed", "proper", "properly", "way",
    "use", "appear", "appears", "specific", "specifically", "write", "writing", "written", "done",
    "certain", "within", "whether", "users", "application", "applications", "typically", "run",
    "solution", "around", "causing", "exploit", "exploited"
]


#### FUNCTIONS #####################################################################################
def _readDocuments(data_path):
    documents = list()
    with open(data_path, newline="") as f:
        csv_reader = csv.reader(f, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)

        # Skip header row
        next(csv_reader)

        for row in csv_reader:
            new_row = list()
            new_row.append(row[0])              # CVE ID
            new_row.append(row[1])              # Cluster Number
            words_set = list(set(row[2].split(" ")))
            new_row.append(words_set)           # Unique Words
            documents.append(new_row)

    return documents


def _getClusters(documents):
    clusters = OrderedDict()
    for doc in documents:
        if doc[1] in clusters.keys():
            # Append words from each document to the cluster
            clusters[doc[1]].extend(doc[2])
        else:
            clusters.update({doc[1]: doc[2]})

    new_clusters = OrderedDict()
    for k, v in clusters.items():
        new_v = list()
        for word in v:
            if word not in IGNORE_WORDS:
                new_v.append(word)

        new_clusters.update({k: new_v})

    return new_clusters


def _getNumDocsPerCluster(documents):
    clusters = dict()
    for doc in documents:
        if doc[1] in clusters.keys():
            clusters[doc[1]] += 1
        else:
            clusters.update({doc[1]: 1})

    return clusters


def _getWordCounts(words):
    tokens, counts = np.unique(words, return_counts=True)
    d = dict(zip(tokens, counts))
    d = OrderedDict({k: v for k, v in sorted(d.items(), key=lambda item: item[1])})

    return d


def _getTopicWords(word_counts, num_docs):
    topic_words = list()
    for word, count in word_counts.items():
        if count >= num_docs / 3: # and count > 1
            topic_words.append("{} ({})".format(word, count))

    return topic_words


def _getClusterWords(clusters, docs_per_cluster):
    cluster_words = OrderedDict()
    for k, v in clusters.items():
        num_docs = docs_per_cluster[k]
        word_counts = _getWordCounts(v)
        topic_words = _getTopicWords(word_counts, num_docs)
        cluster_words.update({k: topic_words})

    return cluster_words


def _printClusterWords(cluster_words):
    num_clusters = len(cluster_words.keys())
    for i in range(num_clusters):
        words = cluster_words[str(i)]
        print("{}: {}".format(i, words))


#### MAIN ##########################################################################################
def label(args, RESULTS_PATH):
   documents = _readDocuments(args.clusters)
   docs_per_cluster = _getNumDocsPerCluster(documents)
   clusters = _getClusters(documents)
   cluster_words = _getClusterWords(clusters, docs_per_cluster)
   _printClusterWords(cluster_words)
