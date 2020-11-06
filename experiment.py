#!/usr/bin/env python3

#### PYTHON IMPORTS ################################################################################
import argparse


#### THIRD-PARTY IMPORTS ###########################################################################


#### PACKAGE IMPORTS ###############################################################################
from src.cluster import cluster
from src.info import info
from src.label import label
from src.prepare import prepare
from src.train import train
from data import DATA_FILES_RAW, DATA_FILES_PREPARED
from models import MODELS_PATH
from results import RESULTS_PATH

#### GLOBALS #######################################################################################


#### FUNCTIONS #####################################################################################
def _strToBool(v):
    """
    Helper function for argparse. Convert string representations of booleans to actual booleans.
    """
    if v == "True":
        return True
    else:
        return False


def prepareCommand(args):
    """
    When the 'prepare' command is issued, 'args.func(args)' passes this function the user-supplied
    command line arguments. This function passes the arguments to src/prepare.prepare().
    """
    prepare(args, DATA_FILES_RAW, DATA_FILES_PREPARED)


def trainCommand(args):
    """
    When the 'train' command is issued, 'args.func(args)' passes this function the user-supplied
    command line arguments. This function passes the arguments to src/train.train().
    """
    train(args, DATA_FILES_PREPARED, MODELS_PATH)


def clusterCommand(args):
    """
    When the 'cluster' command is issued, 'args.func(args)' passes this function the user-supplied
    command line arguments. This function passes the arguments to src/cluster.cluster().
    """
    cluster(args, DATA_FILES_PREPARED, MODELS_PATH, RESULTS_PATH)


def infoCommand(args):
    """
    When the 'info' command is issued, 'args.func(args)' passes this function the user-supplied
    command line arguments. This function passes the arguments to src/info.info().
    """
    info(args, DATA_FILES_RAW, DATA_FILES_PREPARED)


def labelCommand(args):
    """
    When the 'label' command is issued, 'args.func(args)' passes this function the user-supplied
    command line arguments. This function passes the arguments to src/label.label().
    """
    label(args, RESULTS_PATH)


#### MAIN ##########################################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Code that facilitates training the Word Embeddings models and performing the "
        "clustering experiment explained in the MLBDACP21 publication."
    )

    command_parsers = parser.add_subparsers(
        help="Available commands."
    )

    #### PREPARE COMMAND
    prepare_parser = command_parsers.add_parser(
        "prepare", help="Extract fields of interest from the raw data files and create the prepared "
        "(ready for training) data files. See 'prepare --help' for details."
    )
    prepare_parser.add_argument(
        "dataset", type=str, choices=["cve", "vhp", "vhp_human"], help="The dataset to prepare."
    )
    prepare_parser.set_defaults(func=prepareCommand)

    #### TRAIN COMMAND
    train_parser = command_parsers.add_parser(
        "train", help="Train a Word Embeddings model. See 'train --help' for details."
    )
    train_parser.add_argument(
        "dataset", type=str, choices=["cve", "vhp", "vhp_human"],
        help="The dataset to use for training the Word Embeddings model."
    )
    train_parser.add_argument(
        "lemmatize", type=_strToBool, choices=[False, True],
        help="Whether or not to lemmatize the dataset before training."
    )
    train_parser.add_argument(
        "algorithm", type=str, choices=["cbow", "csg"], help="The type of algorithm to use for "
        "training. Continuous Bag-of-Words (cbow) or Continuous Skip-Gram (csg)."
    )
    train_parser.add_argument(
        "dimensionality", type=int, help="The size of the word vectors to compute. Normally "
        "intervals of 100, with 100 for small corpora and 300 for large corpora."
    )
    train_parser.add_argument(
        "window", type=int, help="The maximum distance between the current and the predicted word; "
        "used for context when computing word vectors. Large windows tend to produce more topical "
        "similarities; smaller windows tend to produce more functional/syntactic similarities. "
        "Recommendation: 5."
    )
    train_parser.add_argument(
        "min_count", type=int, help="Words appearing less than 'min_count' times in the corpus will"
        " be ignored. Used to prevent uncommon words from throwing off word vector computation. "
        "Recommendation: 5."
    )
    train_parser.add_argument(
        "workers", type=int, help="Number of CPU's to use when computing word vectors."
    )
    train_parser.add_argument(
        "negative_sampling", type=int,
        help="How many noise words should be drawn for netative sampling."
    )
    train_parser.add_argument(
        "alpha", type=float, help="Initial learning rate for training. Recommendation: 0.025."
    )
    train_parser.add_argument(
        "seed", type=int, help="Seed for random number generator; helps with reproducibility."
    )
    train_parser.add_argument(
        "model_prefix", type=str, help="Model will be saved to disk with 'model_prefix' "
        "prepended to the file name."
    )
    train_parser.set_defaults(func=trainCommand)

    #### CLUSTER COMMAND
    cluster_parser = command_parsers.add_parser(
        "cluster", help="Cluster documents using document vectors."
    )
    cluster_parser.add_argument(
        "dataset", type=str, choices=["vhp"], help="The dataset containing documents to cluster."
    )
    cluster_parser.add_argument(
        "model_path", type=str, help="Path to model file to use for computing document vectors."
    )
    cluster_parser.add_argument(
        "lemmatize", type=_strToBool, choices=[False, True],
        help="Whether or not to lemmatize the dataset before clustering."
    )
    cluster_parser.add_argument(
        "algorithm", type=str, choices=["agglomerative"], help="The algorithm to use for "
        "clustering. Currently, only 'agglomerative' clustering is implemented."
    )
    cluster_parser.add_argument(
        "plot", type=_strToBool, choices=[False, True],
        help="Whether or not to generate scatter plots for clusters and dendrograms."
    )
    cluster_parser.add_argument(
        "results_prefix", type=str, help="Results will be saved to disk with 'results_prefix' "
        "prepended to the file name."
    )
    cluster_parser.set_defaults(func=clusterCommand)

    #### INFO COMMAND
    info_parser = command_parsers.add_parser(
        "info", help="Display info about the datasets."
    )
    info_parser.add_argument(
        "dataset", type=str, choices=["cve", "vhp"], help="The dataset to display info for."
    )
    info_parser.set_defaults(func=infoCommand)

    #### LABEL COMMAND
    label_parser = command_parsers.add_parser(
        "label", help="Label clusters with the most frequent words."
    )
    label_parser.add_argument(
        "clusters", type=str, help="Path to CSV containing clusters."
    )
    label_parser.add_argument(
        "num_words", type=int, help="Number of most frequent words to assign to each cluster."
    )
    label_parser.add_argument(
        "results_prefix", type=str, help="Results will be saved to disk with 'results_prefix' "
        "prepended to the file name."
    )
    label_parser.set_defaults(func=labelCommand)

    #### PARSE ARGUMENTS
    args = parser.parse_args()
    print(args)
    args.func(args)


