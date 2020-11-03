#!/bin/sh

## Prepare the datasets
./experiment.py prepare cve
./experiment.py prepare vhp

## Train the word embedding models
# Model saved to: models/trial01_cve_True_csg_150_5_20_10_0.025_11.bin
./experiment.py train cve True csg 150 5 20 4 10 0.025 11 trial01
# Model saved to: models/trial01_vhp_True_csg_150_5_20_10_0.025_11.bin
./experiment.py train vhp True csg 150 5 20 4 10 0.025 11 trial01

## Perform clustering
# Results saved to: results/trial01_docClusters_cve_True_csg_150_5_20_10_0.025_11_vhp.csv
./experiment.py cluster vhp models/trial01_cve_True_csg_150_5_20_10_0.025_11.bin True agglomerative True trial01
# Results saved to: results/trial01_docClusters_vhp_True_csg_150_5_20_10_0.025_11_vhp.csv
./experiment.py cluster vhp models/trial01_vhp_True_csg_150_5_20_10_0.025_11.bin True agglomerative True trial01
