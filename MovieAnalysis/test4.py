#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/29 11:39
# @Author  : Daisy
# @Site    : 
# @File    : test4.py
# @Software: PyCharm Community Edition

import jieba
from random import shuffle
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk.metrics import BigramAssocMeasures
from nltk.classify.scikitlearn import SklearnClassifier

def read_file1(filename):
    stop = [line.strip() for line in open('stopwords.txt', 'r', encoding='utf-8').readlines()]  # 停用词

    f = open(filename, 'r', encoding='utf-8')
    g = open('cleaned_zhanlang.txt', 'w+', encoding='utf-8')
    line = f.readline()

    # str = []

    while line:
        s = line.split('\t')
        # comments=''
        fenci = jieba.cut(s[0], cut_all=False)  # False默认值：精准模式

        comments = str((list(set(fenci) - set(stop))))
        comments = comments.replace('\\n', '')

        print(comments)
        g.write(comments)
        line = f.readline()

    g.close()
    f.close()
    return str

# read_file('zhanlang.txt')


def read_file(filename):
    stop = [line.strip() for line in open('stopwords.txt', 'r', encoding='utf-8').readlines()]  # 停用词

    f = open(filename, 'r', encoding='utf-8')

    line = f.readline()

    str = []

    while line:
        s = line.split('\t')

        fenci = jieba.cut(s[0], cut_all=False)  # False默认值：精准模式

        str.append(list(set(fenci) - set(stop)))

        line = f.readline()

    return str

# 获取信息量最高(前number个)的特征(卡方统计)

def jieba_feature(number):
    posWords = []

    negWords = []

    for items in read_file('zl_pos.txt'):  # 把集合的集合变成集合

        for item in items:
            posWords.append(item)

    for items in read_file('zl_neg.txt'):

        for item in items:
            negWords.append(item)

    word_fd = FreqDist()  # 词为key，词频为value，结果按词频由大到小排序
    # print(word_fd)
    cond_word_fd = ConditionalFreqDist()  # 可统计积极文本中的词频和消极文本中的词频
    # print(cond_word_fd)
    for word in posWords:
        word_fd[word] += 1
        # print('pos:', word_fd[word])
        cond_word_fd['pos'][word] += 1
    # print(cond_word_fd.N())
    for word in negWords:
        word_fd[word] += 1
        # print('neg', word_fd)
        cond_word_fd['neg'][word] += 1
    # print(word_fd.items())
    # print(cond_word_fd.N())
    pos_word_count = cond_word_fd['pos'].N()  # 积极词的数量

    neg_word_count = cond_word_fd['neg'].N()  # 消极词的数量

    total_word_count = pos_word_count + neg_word_count

    word_scores = {}  # 包括了每个词和这个词的信息量

    for word, freq in word_fd.items():
        pos_score = BigramAssocMeasures.chi_sq(cond_word_fd['pos'][word], (freq, pos_word_count),
                                               total_word_count)  # 计算积极词的卡方统计量，这里也可以计算互信息等其它统计量
        # print('pos:', pos_score)
        neg_score = BigramAssocMeasures.chi_sq(cond_word_fd['neg'][word], (freq, neg_word_count),
                                               total_word_count)  # 同理
        # print('neg:', neg_score)
        word_scores[word] = pos_score + neg_score  # 一个词的信息量等于积极卡方统计量加上消极卡方统计量

    best_vals = sorted(word_scores.items(), key=lambda item: item[1], reverse=True)[
                :number]  # 把词按信息量倒序排序。number是特征的维度，是可以不断调整直至最优的
    # print(best_vals)
    best_words = set([w for w, s in best_vals])
    # print(best_words)
    # print('1')
    return dict([(word, True) for word in best_words])


def build_features():

    # feature = bag_of_words(text())#单个词

    # feature = bigram(text(),score_fn=BigramAssocMeasures.chi_sq,n=500)#双个词

    # feature =  bigram_words(text(),score_fn=BigramAssocMeasures.chi_sq,n=500)#单个词和双个词

    feature = jieba_feature(300)  # 结巴分词

    posFeatures = []

    for items in read_file('zl_pos.txt'):

        a = {}

        for item in items:

            if item in feature.keys():
                a[item] = 'True'

        posWords = [a, 'pos']  # 为积极文本赋予"pos"

        posFeatures.append(posWords)

    negFeatures = []

    for items in read_file('zl_neg.txt'):

        a = {}

        for item in items:

            if item in feature.keys():
                a[item] = 'True'

        negWords = [a, 'neg']  # 为消极文本赋予"neg"

        negFeatures.append(negWords)

    return posFeatures, negFeatures

posFeatures, negFeatures = build_features()  # 获得训练数据

shuffle(posFeatures)  # 把文本的排列随机化

shuffle(negFeatures)  # 把文本的排列随机化

train = posFeatures[200:] + negFeatures[200:]  # 训练集(80%)

test = posFeatures[:200] + negFeatures[:200]  # 预测集(验证集)(20%)

data, tag = zip(*test)  # 分离测试集合的数据和标签，便于验证和测试
print('data:',data)
print(tag)

def score(classifier):
    classifier = SklearnClassifier(classifier)  # 在nltk中使用scikit-learn的接口

    classifier.train(train)  # 训练分类器
    # print(classifier)
    pred = classifier.classify_many(data)  # 对测试集的数据进行分类，给出预测的标签
    # print(pred)
    n = 0

    s = len(pred)

    for i in range(0, s):

        if pred [i] == tag [i]:
            n = n + 1

    return n / s  # 对比分类预测结果和人工标注的正确结果，给出分类器准确度

from sklearn.naive_bayes import MultinomialNB, BernoulliNB
a, b = build_features()
# k=read_file('zl_neg.txt')
k = jieba_feature(10)
#print(k)
print('BernoulliNB`s accuracy is %f' % score(BernoulliNB()))