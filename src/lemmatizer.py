#!/usr/bin/env python3

#### PYTHON IMPORTS ################################################################################
import multiprocessing as mp


#### THIRD-PARTY IMPORTS ###########################################################################
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer


#### PACKAGE IMPORTS ###############################################################################


#### GLOBALS #######################################################################################
WORDNET_POS = {"N": wordnet.NOUN, "V": wordnet.VERB, "J": wordnet.ADJ, "R": wordnet.ADV}


#### FUNCTIONS #####################################################################################


#### CLASSES #######################################################################################
class MPLemmatizer():
    def __init__(self, sents):
        self.lemmatizer = WordNetLemmatizer()
        self.sents = sents
        self.pos_sents = list()
        self.lemma_sents = list()
        self.lemma_dict = dict()

    def _posTagMP(self, sent):
        return nltk.pos_tag(sent)

    def _posTag(self):
        pos_sents = list()
        with mp.Pool(mp.cpu_count()) as pool:
            pos_sents = pool.map(self._posTagMP, self.sents)
            
        self.pos_sents = pos_sents

    def _lemmatizeMP(self, sent):
        temp_sent = list()
        for tok, pos in sent:
            p = WORDNET_POS.get(pos, wordnet.NOUN)
            lemma = self.lemmatizer.lemmatize(tok, p)
            temp_sent.append(lemma)

            if lemma in list(self.lemma_dict.keys()):
                if tok not in self.lemma_dict[lemma]:
                    self.lemma_dict[lemma].append(tok)
            else:
                self.lemma_dict.update({lemma: [tok]})

        return temp_sent

    def _lemmatize(self):
        lemma_sents = list()
        with mp.Pool(mp.cpu_count()) as pool:
            lemma_sents = pool.map(self._lemmatizeMP, self.pos_sents)

        self.lemma_sents = lemma_sents

    def execute(self):
        self._posTag()
        self._lemmatize()
        return self.lemma_sents, self.lemma_dict


class Lemmatizer():
    def __init__(self, sents):
        self.lemmatizer = WordNetLemmatizer()
        self.sents = sents
        self.pos_sents = list()
        self.lemma_sents = list()
        self.lemma_dict = dict()

    def _posTag(self):
        for sent in self.sents:
            self.pos_sents.append(nltk.pos_tag(sent))

    def _lemmatize(self):
        tot = len(self.pos_sents)
        char = str(len(str(tot)))
        curr = 0
        formstr = "    {0:0" + char +"d}"
        for sent in self.pos_sents:
            print("{}/{}".format(formstr.format(curr), tot), end="\r")
            curr += 1
            temp_sent = list()
            for tok, pos in sent:
                p = WORDNET_POS.get(pos, wordnet.NOUN)
                lemma = self.lemmatizer.lemmatize(tok, p)
                temp_sent.append(lemma)

                if lemma in list(self.lemma_dict.keys()):
                    if tok not in self.lemma_dict[lemma]:
                        self.lemma_dict[lemma].append(tok)
                else:
                    self.lemma_dict.update({lemma: [tok]})

            self.lemma_sents.append(temp_sent)

    def execute(self):
        self._posTag()
        self._lemmatize()
        print("\n")
        return self.lemma_sents, self.lemma_dict
