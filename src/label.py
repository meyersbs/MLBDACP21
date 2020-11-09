#!/usr/bin/env python3

#### PYTHON IMPORTS ################################################################################
import csv
import os
from collections import OrderedDict


#### THIRD-PARTY IMPORTS ###########################################################################
import nltk
import numpy as np


#### PACKAGE IMPORTS ###############################################################################


#### GLOBALS #######################################################################################


#### FUNCTIONS #####################################################################################
def _readDocuments(data_path):
    """
    Read documents from the given path.

    GIVEN:
      data_path (str)   path to read data from

    RETURN:
      documents (list)  list of lists, where each sublist contains a CVE ID, cluster number, and
                        the unique words in the description
    """
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


def _readDocuments2(data_path):
    documents = list()
    with open(data_path, newline="") as f:
        csv_reader = csv.reader(f, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)

        # Skip header row
        next(csv_reader)

        for row in csv_reader:
            new_row = list()
            new_row.append(row[0])
            new_row.append(row[1])
            new_row.append(row[2])
            documents.append(new_row)

    return documents


def _getClusters(documents):
    """
    Aggregate all of the words from the documents in each cluster together.

    GIVEN:
      documents (list)  list of lists, where each sublist contains a CVE ID, cluster number, and
                        the unique words in the description
    
    RETURN:
      clusters (dict)   OrderedDict where each key is a cluster number and each value is a list of
                        words from the document descriptions
    """
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
            new_v.append(word)

        new_clusters.update({k: new_v})

    return new_clusters


def _getClusters2(documents):
    """
    Read the clusters (and documents) from disk. Compute bigrams and frequencies for all documents
    within a cluster.

    GIVEN:
      documents (list)  list of lists, where each sublist contains a CVE ID, cluster number, and
                        the unique words in the description

    RETURN:
      clusters (dict)   OrderedDict where each key is a cluster number and each value is a nested
                        list of bigrams and their frequencies
    """
    clusters = OrderedDict()
    for doc in documents:
        bigrams = list(nltk.bigrams(nltk.word_tokenize(doc[2])))
        if doc[1] in clusters.keys():
            clusters[doc[1]].extend(bigrams)
        else:
            clusters.update({doc[1]: bigrams})

    new_clusters = OrderedDict()
    for k, v in clusters.items():
        new_v = nltk.FreqDist(v)
        new_clusters.update({k: new_v})

    return new_clusters


def _getNumDocsPerCluster(documents):
    """
    Count how many documents are assigned to each cluster.

    GIVEN:
      documents (list)  list of lists, where each sublist contains a CVE ID, cluster number, and
                        the unique words from the description

    RETURN:
      clusters (dict)   dictionary where each key is a cluster number and each value is the number
                        of documents in that cluster
    """
    clusters = dict()
    for doc in documents:
        if doc[1] in clusters.keys():
            clusters[doc[1]] += 1
        else:
            clusters.update({doc[1]: 1})

    return clusters


def _getWordCounts(words):
    """
    Helper function for _getClusterWords(...). Compute frequencies for words.

    GIVEN:
      words (list)  words in a cluster

    RETURN:
      d (dict)      OrderedDict where each key is a word and each value is its frequency
    """
    tokens, counts = np.unique(words, return_counts=True)
    d = dict(zip(tokens, counts))
    d = OrderedDict({k: v for k, v in sorted(d.items(), key=lambda item: item[1])})

    return d


def _getTopicWords(word_counts, num_docs):
    """
    Helper function for _getClusterWords(...). Select the words with high enough frequencies and
    put them in a list.

    GIVEN:
      word_counts (dict)    OrderedDict where each key is a word and each value is its frequency
      num_docs (int)        the number of documents in the cluster

    RETURN:
      topic_words (list)    list of words with their frequencies
    """
    topic_words = list()
    for word, count in word_counts.items():
        if count >= num_docs / 2:
            topic_words.append("{} ({})".format(word, count))

    return topic_words


def _getClusterWords(clusters, docs_per_cluster):
    """
    Compute word frequencies for the words in a cluster.

    GIVEN:
      clusters (dict)           OrderedDict where each key is a cluster number and each value is a
                                list of words from the document descriptions
      docs_per_cluster (dict)   dictionary where each key is a cluster number and each value is the
                                number of documents in that cluster

    RETURN:
      cluster_words (dict)      OrderedDict where each key is a cluster number and each value is
                                a list of words and their frequencies
    """
    cluster_words = OrderedDict()
    for k, v in clusters.items():
        num_docs = docs_per_cluster[k]
        word_counts = _getWordCounts(v)
        topic_words = _getTopicWords(word_counts, num_docs)
        cluster_words.update({k: topic_words})

    return cluster_words


def _printClusterWords(cluster_words):
    """
    Helper function to pretty print the clusters and their word frequencies.

    GIVEN:
      cluster_words (dict)  OrderedDict where each key is a cluster number and each value is a
                            list of words and their frequencies

    """
    num_clusters = len(cluster_words.keys())
    for i in range(num_clusters):
        words = cluster_words[str(i)]
        print("{}: {}".format(i, words))


def _printClusterBigrams(clusters):
    """
    Helper function to pretty print the clusters and their most frequent bigrams.

    GIVEN:
      clusters (dict)   OrderedDict where each key is a cluster number and each value is a nested
                        list of bigrams and their frequencies
    """
    num_clusters = len(clusters.keys())
    for i in range(num_clusters):
        cluster_bigrams = clusters[str(i)]
        temp = cluster_bigrams.most_common(15)
        bigrams = ""
        for b in temp:
            bigram = "{} {} ({})".format(
                b[0][0],
                b[0][1],
                b[1]
            )
            bigrams = bigrams + bigram + ", "

        print("{}: {}".format(i, bigrams))


#### MAIN ##########################################################################################
def label(args, RESULTS_PATH):
    print("Most Frequent Words:")
    documents = _readDocuments(args.clusters)
    docs_per_cluster = _getNumDocsPerCluster(documents)
    clusters = _getClusters(documents)
    cluster_words = _getClusterWords(clusters, docs_per_cluster)
    _printClusterWords(cluster_words)

    print("\nMost Frequent Bigrams:")
    documents = _readDocuments2(args.clusters)
    clusters = _getClusters2(documents)
    _printClusterBigrams(clusters)
