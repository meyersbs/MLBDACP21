#!/usr/bin/env python3

#### PYTHON IMPORTS ################################################################################
import csv
import os

#### THIRD-PARTY IMPORTS ###########################################################################

#### PACKAGE IMPORTS ###############################################################################

#### GLOBALS #######################################################################################

#### FUNCTIONS #####################################################################################
def _loadData(data_path):
    """
    Load the dataset from the given path.

    GIVEN:
      data_path (str)   path to load dataset from

    RETURN:
      dataset (list)    list of lists, where each sublist is a document
    """
    dataset = list()
    with open(data_path, newline="") as f:
        csv_reader = csv.reader(f, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)

        # Skip header row
        next(csv_reader)
        
        for row in csv_reader:
            dataset.append(row)

    return dataset


def _totalWords(dataset, index):
    """
    Given a dataset, compute the total number of words at the given index.

    GIVEN:
      dataset (list)    list of lists, where each sublist is a document
      index (int)       index in dataset to count words

    RETURN:
      total_words (int) total number of words in the dataset
    """
    total_words = 0
    for d in dataset:
        words = d[index].split(" ")
        total_words += len(words)

    return total_words


def _totalUniqueWords(dataset, index):
    """
    Given a dataset, compute the total number of unique words at the given index.

    GIVEN:
      dataset (list)        list of lists, where each sublist is a document
      index (int)           index in dataset to count unique words

    RETURN:
      unique_words (int)    total number of unique words in dataset
    """
    all_words = list()
    for d in dataset:
        words = d[index].split(" ")
        all_words.extend(words)

    unique_words = len(set(all_words))
    return unique_words


#### MAIN ##########################################################################################
def info(args, DATA_FILES_RAW, DATA_FILES_PREPARED):
    if args.dataset == "cve":
        print("== INFO FOR CVE DATASET ==")
        print("==== PREPARED DATASET ====")
        prep = DATA_FILES_PREPARED[args.dataset]
        prep_docs = _loadData(prep)
        num_docs = len(prep_docs)
        total_words = _totalWords(prep_docs, 1)
        unique_words = _totalUniqueWords(prep_docs, 1)
        avg_words = total_words / num_docs
        print("         # Docs: {}".format(num_docs))
        print("    Total Words: {}".format(total_words))
        print("   Unique Words: {}".format(unique_words))
        print("    Avg Doc Len: {}".format(avg_words))

    elif args.dataset == "vhp":
        print("== INFO FOR VHP DATASET ==")
        print("==== PREPARED DATASET ====")
        prep = DATA_FILES_PREPARED[args.dataset]
        prep_docs = _loadData(prep)
        num_docs = len(prep_docs)
        total_words = _totalWords(prep_docs, 1)
        unique_words = _totalUniqueWords(prep_docs, 1)
        avg_words = total_words / num_docs
        print("         # Docs: {}".format(num_docs))
        print("    Total Words: {}".format(total_words))
        print("   Unique Words: {}".format(unique_words))
        print("    Avg Doc Len: {}".format(avg_words))


