#!/usr/bin/env python3

#### PYTHON IMPORTS ################################################################################
import csv
import os


#### THIRD-PARTY IMPORTS ###########################################################################
import gensim
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import nltk
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import AgglomerativeClustering, DBSCAN, OPTICS, KMeans
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler


#### PACKAGE IMPORTS ###############################################################################


#### GLOBALS #######################################################################################
from src.lemmatizer import MPLemmatizer


#### FUNCTIONS #####################################################################################
def _loadDocuments(data_path):
    """
    Read documents from the provided data_path into a nested list of documents.

    GIVEN:
      data_path (str)   path to load data from

    RETURN:
      documents (list)  list of lists, where each sublist contains an ID and a description
    """
    documents = list()
    with open(data_path, newline="") as f:
        csv_reader = csv.reader(f, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)

        # Skip header row
        next(csv_reader)

        # Load dataset from disk
        for row in csv_reader:
            documents.append(row)

    return documents


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


def _getDocumentVectors(documents, model):
    """
    Compute document vectors for each document using the given model.

    GIVEN:
      documents (list)  list of lists, where each sublist is a tokenized (or lemmatized) document
      model (object)    a trained gensim.models.Word2Vec model

    RETURN:
      vectors (list)    list of lists, where each sublist is a fixed-length document vector
    """
    vectors = list()
    size = len(model.wv["first"])
    for doc in documents:
        vec = np.zeros(size)
        for tok in doc:
            if tok in model.wv:
                vec = vec + model.wv[tok]
        vectors.append(vec)

    return vectors


#### MAIN ##########################################################################################
def cluster(args, DATA_FILES_PREPARED, MODELS_PATH, RESULTS_PATH):

    #### Load Data from Disk
    data_path = DATA_FILES_PREPARED[args.dataset]
    print("Loading documents from: {}".format(data_path))
    documents = _loadDocuments(data_path)
    descriptions = _getDescriptions(documents)

    #### Lemmatize Documents
    if args.lemmatize:
        print("Lemmatizing documents (this might take a while)...")
        descriptions, _ = _lemmatizeDescriptions(descriptions)

    #### Load Model from Disk
    model_path = os.path.abspath(args.model_path)
    print("Loading model from: {}".format(model_path))
    model = gensim.models.Word2Vec.load(model_path)

    #### Compute Document Vectors
    print("Computing document vectors...")
    vectors = _getDocumentVectors(descriptions, model)
    vectors_path = "{}_docVectors_{}_{}.csv".format(
        args.results_prefix,
        "_".join(model_path.split("_")[1:])[:-4],
        args.dataset
    )
    vectors_path = os.path.join(RESULTS_PATH, vectors_path)
    pd.DataFrame(vectors).to_csv(vectors_path, header=None, index=None)
    print("Document Vectors saved to: {}".format(vectors_path))

    #### Convert to Pandas DataFrame
    vectors_frame = pd.DataFrame(vectors)

    #### Normalize Column Values Between [-1, 1]
    print("Normalizing document vector values...")
    scaler = MinMaxScaler(feature_range=(-1, 1))
    vectors_frame = scaler.fit_transform(vectors_frame[vectors_frame.columns.values.tolist()])

    #### Determine Optimal K
    print("Computing optimal number of clusters (K)...")
    fig, axs = plt.subplots(5, 5)
    curr_row = 0
    curr_col = 0
    optimal_k = len(vectors)
    for i in range(3, 28):
        print(i)
        # Do clustering
        model = AgglomerativeClustering(n_clusters=i, affinity="euclidean", linkage="ward").fit(vectors_frame)

        # Reduce dimensionality to 2 for plotting
        lda = LDA(n_components=2)
        vectors_trans = pd.DataFrame(lda.fit_transform(vectors_frame, model.labels_))
       
        # Scatter plot
        axs[curr_row, curr_col].scatter(vectors_trans.iloc[:,0].values, vectors_trans.iloc[:,1].values, s=1, c=model.labels_, cmap="hsv") 
        axs[curr_row, curr_col].title.set_text("{} clusters".format(i))
        axs[curr_row, curr_col].set_xticks([])
        axs[curr_row, curr_col].set_yticks([])

        # Update optimal K
        values, counts = np.unique(model.labels_, return_counts=True)
        if min(counts) == 1:
            optimal_k = min(optimal_k, i-1)
        d = dict(zip(values, counts))
        print(d)

        if curr_col < 4:
            curr_col += 1
        else:
            curr_col = 0
            curr_row += 1
    fig.suptitle("K Number of Clusters (CVE Model)")
    if args.plot:
        plt.show()
    print("Optimal K: {}".format(optimal_k))

    #### Plot Dendrogram
    if args.plot:
        links = linkage(vectors_frame, method="ward")
        dendro = dendrogram(links)
        plt.title("Dendrogram")
        plt.ylabel("Euclidean Distance")
        plt.xlabel("Cluster Sizes")
        plt.show()

    #### Clustering with Optimal K
    model = AgglomerativeClustering(n_clusters=optimal_k, affinity="euclidean", linkage="ward").fit(vectors_frame)
    clusters = model.labels_

    #### Format Cluster Results
    final_data = list()
    header_row = ["ID", "Cluster Number", "Description"]
    final_data.append(header_row)
    for i in range(0, len(clusters)):
        data_row = [
            documents[i][0],    # ID
            clusters[i],        # Cluster Number
            documents[i][1]     # Description
        ]
        final_data.append(data_row)

    #### Save Clusters to Disk
    clusters_path = "{}_docClusters_{}_{}_K_{}.csv".format(
        args.results_prefix,
        "_".join(model_path.split("_")[1:])[:-4],
        args.dataset,
        optimal_k
    )
    clusters_path = os.path.join(RESULTS_PATH, clusters_path)
    pd.DataFrame(final_data).to_csv(clusters_path, header=None, index=None)
    print("Document Clusters saved to: {}".format(clusters_path))


