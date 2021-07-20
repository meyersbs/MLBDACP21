# MLBDACP21

This repository accompanies a paper submitted to The 3rd International Symposium on Machine Learning and Big Data Analytics For Cybersecurity and Privacy (MLBDACP 2021). It contains all of the code used in the experiment.

```
Meyers, B.S. and Meneely, A. (2021). An Automated Post-Mortem Analysis of Vulnerability Relationships
using Natural Language Word Embeddings. Proceedings of the 3rd International Symposium on Machine
Learning and Big Data Analytics for Cybersecurity and Privacy (MLBDACP).
https://www.sciencedirect.com/science/article/pii/S1877050921007948
```

## Dependencies

This code requires Python 3 and the following python libraries: `gensim`, `matplotlib`, `nltk`, `numpy`, `pandas`, `scikit-learn`, `scipy`. You may install these libraries in one of the following ways:

- `pip3 install gensim matplotlib nltk numpy pandas scikit-learn scipy`
- `pip3 install -r requirements.txt`

Additionally, you will need to download the stopwords corpus for NLTK: `python3 -m nltk.downloader stopwords`

## Environment

The exact environment used in this study is as follows:

- Ubuntu 18.04.5 LTS
- Python 3.6.9
- Python libraries:
    - gensim (3.8.1)
    - matplotlib (3.2.1)
    - nltk (3.4.5)
    - numpy (1.18.2)
    - pandas (0.25.3)
    - scikit-learn (0.22.2.post1)
    - scipy (1.4.1)

## Experiment

To repeat the experiment with exactly the same parameters as used in the above paper, run `./run_experiment.sh`. Note: you may need to make this file executable: `chmod +x run_experiment.sh`.

## Directory Organization

### data/

The `data/` directory contains the corpora used in our experiment (`cve.csv.zip` and `vhp.csv.zip`) -- you must unzip these files before running the experiment. It also contains `vhp_human.csv`, which contains the manual human annotations described in the above paper. Preprocessed corpora are also saved in this directory (`cve_prepared.csv` and `vhp_prepared.csv`).

### models/

The `models/` directory is where the serialized word embedding models will be saved.

### release/

The `release/` directory contains the final data, models, and results from this experiment.

### results/

The `results/` directory is where computed document vectors and assigned clusters will be saved.

### src/

The `src/` directory contains the majority of the source code used in this project:

- `cluster.py`: functionality to perform hierarchical agglomerative clustering
- `info.py`: functionality to compute and display basic corpora statistics
- `label.py`: functionality to compute and display most frequent words and bigrams for documents within clusters
- `lemmatizer.py`: functionality to lemmatize words in the corpora
- `prepare.py`: functionality for preprocessing the corpora
- `train.py`: functionality to train word embedding models

## Usage

### Step 1: Prepare Data

Unzip the datasets by running `unzip *.zip` in the `data/` directory. Then, run the following commands to preprocess the data (steps described in the above paper):

- `./experiment.py prepare cve`
- `./experiment.py prepare vhp`

For details on parameters for the `prepare` command, run: `./experiment.py prepare --help`.

### Step 2: Train Word Embedding Models

Train a word embedding model on each dataset by running:

- `./experiment.py train cve True csg 150 5 20 4 10 0.025 11 trial01`
- `./experiment.py train vhp True csg 150 5 20 4 10 0.025 11 trial01`

Models will be saved to disk in the `models/` directory.

For details on parameters for the `train` command, run: `./experiment.py train --help`.

### Step 3: Clustering

Run the following commands to perform hierarchical agglomerative clustering and compute the number of cluster (K):

- `./experiment.py cluster vhp models/trial01_cve_True_csg_150_5_20_10_0.025_11.bin True agglomerative True trial01`
- `./experiment.py cluster vhp models/trial01_vhp_True_csg_150_5_20_10_0.025_11.bin True agglomerative True trial01`

Computed document vectors and clusters will be saved to disk in the `results/` directory.

For details on parameters for the `cluster` command, run: `./experiment.py cluster --help`.

### Step 4: Labeling

Run the following commands to compute the most frequent words and most frequent bigrams for each of the documents within a cluster:

- `./experiment.py label results/trial01_docClusters_cve_True_csg_150_5_20_10_0.025_11_vhp_K_14.csv trial01`
- `./experiment.py label results/trial01_docClusters_vhp_True_csg_150_5_20_10_0.025_11_vhp_K_11.csv trial01`

For details on parameters for the `label` command, run: `./experiment.py label --help`.

### Miscellaneous

The `info` command can be used to compute and display information about the corpora after you have run the `prepare` command:

- `./experiment.py info cve`
- `./experiment.py info vhp`

For details on parameters for the `info` command, run: `./experiment.py info --help`.

## Contact

For general questions, please contact Benjamin S. Meyers ([email](mailto:bsm9339@rit.edu)). For specific questions about the Vulnerability History Project, please contact Andrew Meneely ([email](mailto:axmvse@rit.edu)).
