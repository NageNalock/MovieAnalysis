#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/12 10:17
# @Author  : Daisy
# @Site    : 
# @File    : 3_analysis_test_2.0.py
# @Software: PyCharm Community Edition


import jieba
from random import shuffle
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk.metrics import BigramAssocMeasures
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression
from nltk.collocations import BigramCollocationFinder
import pickle


num_pos = 0
num_neg = 0
f = open('zl_pos.txt', 'r', encoding='utf-8')
g = open('zl_neg.txt', 'r', encoding='utf-8')

line_pos = f.readlines()
for line_1 in line_pos:
    num_pos += 1

line_neg = g.readlines()
for line_2 in line_neg:
    num_neg += 1

print(num_pos, num_neg)

f.close()
g.close()