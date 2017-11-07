#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/31 21:25
# @Author  : Daisy
# @Site    : 
# @File    : 3_analysis.py
# @Software: PyCharm Community Edition
import pickle
import jieba
import sklearn


def read_text(name):
    stop_words = [line.strip() for line in open('stopwords.txt', 'r', encoding='utf-8').readlines()]
    f = open(name, 'r', encoding='utf-8')
    str = []

    line = f.readline()
    while line:
        s = line.split('\t')
        seg = jieba.cut(s[0], cut_all=False)  # 精准模式
        # seg = seg.replace('\\n', '')
        str.append((list(set(seg) - set(stop_words) - set('\n'))))
        line = f.readline()
    f.close()

    return str


moto = read_text('zhanlang.txt')
clf = pickle.load(open('classifier.pkl', 'rb'))  # 载入分类器

pred = clf.batch_prob_classify(moto)  # 该方法是计算分类概率值的
p_file = open('socre.txt', encoding='utf-8')  # 把结果写入文档
for i in pred:
    p_file.write(str(i.prob('pos')) + ' ' + str(i.prob('neg')) + '\n')
p_file.close()
