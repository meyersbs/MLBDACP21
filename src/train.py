#!/usr/bin/env python3

#### PYTHON IMPORTS ################################################################################
import csv
import os
import sys


#### THIRD-PARTY IMPORTS ###########################################################################
import gensim
import nltk
from gensim.models.keyedvectors import KeyedVectors


#### PACKAGE IMPORTS ###############################################################################
from src.lemmatizer import MPLemmatizer


#### GLOBALS #######################################################################################
ALGORITHM_MAP = {"cbow": 0, "csg": 1}


#### FUNCTIONS #####################################################################################
def _loadDataset(data_path):
    """
    Read data from the provided data_path into a nested list of datapoints.

    GIVEN:
      data_path (str)   path to load data from

    RETURN:
      dataset (list)    list of lists, where each sublist contains an ID and a description
    """
    dataset = list()
    with open(data_path, newline="") as f:
        csv_reader = csv.reader(f, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)

        # Skip header row
        next(csv_reader)

        # Load dataset from disk
        for row in csv_reader:
            dataset.append(row)

    return dataset


def _getDescriptions(dataset):
    """
    Extract and tokenize the descriptions column from the given dataset.

    GIVEN:
      dataset (list)      list of lists, where each sublist contains an ID and a description

    RETURN:
      descriptions (list) list of tokenized descriptions
    """
    descriptions = list()

    for row in dataset:
        desc = nltk.word_tokenize(row[1])
        descriptions.append(desc)

    return descriptions


def _lemmatizeDescriptions(descriptions):
    """
    Lemmatize the provided tokenized descriptions.

    GIVEN:
      descriptions (list) list of tokenized descriptions

    RETURN:
      lemmas (list)       list of lists, where each sublist is a lemmatized description
      lemmas_dict (dict)  dictionary where each key is a lemma that points to a list of tokens that
                          were mapped to that lemma
    """
    lemmatizer = MPLemmatizer(descriptions)
    lemmas, lemmas_dict = lemmatizer.execute()

    return lemmas, lemmas_dict


#### MAIN ##########################################################################################
def train(args, DATA_FILES_PREPARED, MODELS_PATH):
    algorithm = ALGORITHM_MAP[args.algorithm]
    model_prefix = args.model_prefix

    #### Load and format data
    data_path = DATA_FILES_PREPARED[args.dataset]
    print("Reading data from: {}".format(data_path))
    dataset = _loadDataset(data_path)
    descriptions = _getDescriptions(dataset)

    # Lemmatize
    if args.lemmatize == True:
        print("Lemmatizing descriptions (this might take a while)...")
        descriptions, _ = _lemmatizeDescriptions(descriptions)

    #### Train models
    print("Training cve model (this might take a while)...")
    model = gensim.models.Word2Vec(
        descriptions, size=args.dimensionality, window=args.window, min_count=args.min_count,
        workers=args.workers, negative=args.negative_sampling, alpha=args.alpha,
        seed=args.seed, sg=algorithm
    )

    #### Save models
    model_name = "{}_{}_{}_{}_{}_{}_{}_{}_{}_{}.bin"
    model_name = model_name.format(
        args.model_prefix, args.dataset, args.lemmatize, args.algorithm, args.dimensionality,
        args.window, args.min_count, args.negative_sampling, args.alpha, args.seed
    )
    model_path = os.path.join(MODELS_PATH, model_name)
    model.save(model_path)
    print("Model saved to disk: {}".format(model_path))
        
        

