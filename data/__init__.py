#!/usr/bin/env python3

#### PYTHON IMPORTS ################################################################################
import os


#### THIRD-PARTY IMPORTS ###########################################################################


#### PACKAGE IMPORTS ###############################################################################


#### GLOBALS #######################################################################################
DATA_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_FILES_RAW = {
    "cve": os.path.join(DATA_PATH, "cve.csv"),
    "vhp": os.path.join(DATA_PATH, "vhp.csv"),
    "vhp_human": os.path.join(DATA_PATH, "vhp_human.csv")
}
DATA_FILES_PREPARED = {
    "cve": os.path.join(DATA_PATH, "cve_prepared.csv"),
    "vhp": os.path.join(DATA_PATH, "vhp_prepared.csv"),
    "vhp_human": os.path.join(DATA_PATH, "vhp_human_prepared.csv")
}


#### FUNCTIONS #####################################################################################


#### MAIN ##########################################################################################
