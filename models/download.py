#!/usr/bin/env python3

#### PYTHON IMPORTS ################################################################################
import os
import urllib.request


#### THIRD-PARTY IMPORTS ###########################################################################


#### PACKAGE IMPORTS ###############################################################################


#### GLOBALS #######################################################################################
MODELS_PATH = os.path.dirname(os.path.realpath(__file__))
SecVuln_WE_URL = "https://github.com/unsw-cse-soc/Vul_Word2Vec/blob/master/vulner_embedding.bin?raw=true"


#### FUNCTIONS #####################################################################################
def downloadSecVulnModel():
    """
    Download the SecVuln_WE model from the paper's repo.
    """
    print("Downloading file: {}".format(SecVuln_WE_URL))
    download_path = os.path.join(MODELS_PATH, "SecVuln_WE.bin")
    urllib.request.urlretrieve(SecVuln_WE_URL, download_path)
    print("Download complete: {}".format(download_path))


#### MAIN ##########################################################################################
if __name__ == "__main__":
    downloadSecVulnModel()
