#!/usr/bin/env python3

#### PYTHON IMPORTS ################################################################################
import csv
import json
import re
import sys


#### THIRD-PARTY IMPORTS ###########################################################################
import nltk
from nltk.corpus import stopwords


#### PACKAGE IMPORTS ###############################################################################


#### GLOBALS #######################################################################################
RE_NEWLINES = re.compile(r"\n")
RE_MULTISPACE = re.compile(r"\s+")
RE_NONALPHANUMERIC = re.compile(r"[^a-zA-Z0-9 ]+")
RE_VER_01 = re.compile(r"\sv\s*[0-9\._]+,\s")
RE_VER_02 = re.compile(r"\sv\s*[0-9\._]+\s")
RE_VER_03 = re.compile(r"\sver\.\s[0-9]\._]+,\s")
RE_VER_04 = re.compile(r"\sver\.\s[0-9]\._]+\s")
RE_VER_05 = re.compile(r"\s[0-9\._]+,\s")
RE_VER_06 = re.compile(r"\s[0-9\._]+\s")
RE_VER_07 = re.compile(r"\s[0-9]+\.[0-9]+[rx][0-9]+\-[ds][0-9]+,\s")
RE_VER_08 = re.compile(r"\s[0-9]+\.[0-9]+[rx][0-9]+\-[ds][0-9]+\s")
RE_VER_09 = re.compile(r"\s[0-9]+\.[0-9]+[rx][0-9]+,\s")
RE_VER_10 = re.compile(r"\s[0-9]+\.[0-9]+[rx][0-9]+\s")
RE_NUM_1 = re.compile(r"\s[0-9]+,\s")
RE_NUM_2 = re.compile(r"\s[0-9]+\s")
RE_HEX_1 = re.compile(r"\s0x[0-9a-z]+,\s")
RE_HEX_2 = re.compile(r"\s0x[0-9a-z]+\s")
RE_VERS = [
    RE_VER_01, RE_VER_02, RE_VER_03, RE_VER_04, RE_VER_05,
    RE_VER_06, RE_VER_07, RE_VER_08, RE_VER_09, RE_VER_10
]
RE_NUMS = [RE_NUM_1, RE_NUM_2]
RE_HEXS = [RE_HEX_1, RE_HEX_2]
RESERVED_CVE_DESCRIPTION = "** RESERVED ** This candidate has been reserved by an organization or individual that will use it when announcing a new security problem. When the candidate has been publicized, the details for this candidate will be provided."
VHP_PROJECT_MAP = {
    "1": "Chromium",
    "2": "HTTPD",
    "3": "Tomcat",
    "4": "Struts"
}
STOPWORDS = stopwords.words("english")
STOPWORDS.extend(["do", "does", "to"])
STOPWORDS.remove("which")


#### FUNCTIONS #####################################################################################
def _cleanDescription(description):
    """
    Clean up the provided description by:
        (1) Lowercasing all characters
        (2) Replacing version numbers, numerical values, and hex codes with special tokens (VERVER,
            NUMNUM, and HEXHEX, respectively)
        (3) Removing stopwords, punctuation, and special characters

    GIVEN:
      description (str)     the description text to be cleaned

    RETURN:
      new_description (str) the cleaned up description text
    """
    # Remove newlines and trailing whitespace
    new_description = RE_NEWLINES.sub(" ", description)
    new_description = new_description.rstrip()

    # Lowercase all characters
    new_description = new_description.lower()

    # Clean version numbers
    for i, regex in enumerate(RE_VERS):
        if i % 2 == 0:
            replace_token = " VERVER "
        else:
            replace_token = " VERVER, "

        # Running twice is not an accident. running only once results in strange behavior when there
        # is a big list of version numbers; it only matches every other one:
        #    IN: 18.2x75-d41, 19.1r2-s1, 17.3r3-s8, 18.4r1-s6
        #    OUT: VERVER, 19.1r2-s1, VERVER, 18.4r1-s6
        # Calling twice fixes this issue.
        new_description = regex.sub(replace_token, new_description)
        new_description = regex.sub(replace_token, new_description)

    # Clean numerical values
    for i, regex in enumerate(RE_NUMS):
        if i % 2 == 0:
            replace_token = " NUMNUM "
        else:
            replace_token = " NUMNUM, "

        new_description = regex.sub(replace_token, new_description)
        new_description = regex.sub(replace_token, new_description)

    # Clean hex values
    for i, regex in enumerate(RE_NUMS):
        if i % 2 == 0:
            replace_token = " HEXHEX "
        else:
            replace_token = " HEXHEX, "

        new_description = regex.sub(replace_token, new_description)
        new_description = regex.sub(replace_token, new_description)

    # Remove punctuation and special characters
    new_description = RE_NONALPHANUMERIC.sub(" ", new_description)

    # Remove stopwords
    tokens_pre = nltk.word_tokenize(new_description)
    tokens = list()
    for tok in tokens_pre:
        if tok.lower() not in STOPWORDS:
            tokens.append(tok)
    new_description = " ".join(tokens)

    # Clean up duplicate whitespace
    new_description = RE_MULTISPACE.sub(" ", new_description)

    # Return cleaned description
    return new_description


def _prepareCVE(raw, prepared):
    """
    Prepare the CVE dataset.
    """
    print("PREPARING: {}".format(raw))

    # Open file to save prepared dataset to
    out_file = open(prepared, "w", newline="")
    csv_writer = csv.writer(out_file, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)

    # Write header to prepared dataset file
    header = ["ID", "Description"]
    csv_writer.writerow(header)

    with open(raw, newline="") as f:
        csv_reader = csv.reader(f, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)

        # Skip header row and metadata
        for i in range(0, 10):
            next(csv_reader)

        count = 0
        for row in csv_reader:
            # Get the CVE ID and description
            cve_id = row[0]
            cve_desc = row[2]
            cve_desc = _cleanDescription(cve_desc)

            # Create new row to be written to the prepared dataset file
            new_row = list()
            new_row.append(cve_id)
            new_row.append(cve_desc)

            # Only write rows if the description is not empty or meaningless
            if cve_desc not in ["", " ", RESERVED_CVE_DESCRIPTION]:
                count += 1
                csv_writer.writerow(new_row)

    # Clean up
    out_file.close()
    print("PREPARED {} descriptions: {}".format(count, prepared))


def _getMistakesMade(row):
    """
    Parse the notes column of the VHP dataset to extract the mistakes made section.

    GIVEN:
      row (str)         a str representation of a JSON dictionary

    RETURN
      mistakes (str)    the mistakes made section
    """
    notes = json.loads(row)
    mistakes = notes["mistakes"]

    if type(mistakes) == dict:
        mistakes = mistakes["answer"]
    elif type(mistakes) == str:
        mistakes = mistakes.split("\nanswer: |")[1]

    if mistakes is None:
        return ""

    return mistakes


def _prepareVHP(raw, prepared):
    """
    Prepare the VHP dataset.
    """
    print("PREPARING: {}".format(raw))

    # Open file to save prepared dataset to
    out_file = open(prepared, "w", newline="")
    csv_writer = csv.writer(out_file, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)

    # Write header to prepared dataset file
    header = ["ID", "Description"]
    csv_writer.writerow(header)

    with open(raw, newline="") as f:
        csv_reader = csv.reader(f, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)

        # Skip header row
        next(csv_reader)

        count = 0
        for row in csv_reader:
            # Get the VHP ID, description, and mistakes made
            vhp_id = row[1]
            vhp_mistakes = _getMistakesMade(row[8])
            vhp_desc = row[4] + " " + vhp_mistakes
            vhp_desc = _cleanDescription(vhp_desc)

            # Create new row to be written to the prepared dataset file
            new_row = list()
            new_row.append(vhp_id)
            new_row.append(vhp_desc)

            # Only write rows if the description is not empty
            if vhp_desc not in ["", " "] and vhp_id != "This-is-a-Test":
                count += 1
                csv_writer.writerow(new_row)

    # Clean up
    out_file.close()
    print("PREPARED {} descriptions: {}".format(count, prepared))


#### MAIN ##########################################################################################
def prepare(args, DATA_FILES_RAW, DATA_FILES_PREPARED):
    dataset = args.dataset

    raw = DATA_FILES_RAW[dataset]
    prepared = DATA_FILES_PREPARED[dataset]
    if dataset == "cve":
        _prepareCVE(raw, prepared)
    elif dataset == "vhp":
        _prepareVHP(raw, prepared)
    else:
        # This should never happen
        sys.exit("src/prepare.prepare(): Received invalid dataset ('{}').".format(dataset))
