#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/29 18:15
# @Author  : Daisy
# @Site    : 
# @File    : 3_analysis_test.py
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


def text():
    f1 = open('zl_pos.txt', 'r', encoding='utf-8')
    f2 = open('zl_neg.txt', 'r', encoding='utf-8')

    line1 = f1.readline()
    line2 = f2.readline()

    str = ''
    while line1:
        str += line1
        line1 = f1.readline()
    while line2:
        str += line2
        line2 = f2.readline()

    f1.close()
    f2.close()

    return str


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


# read_text('zhanlang.txt')

def single_words_feature(words):
    # print('所有词作为特征')
    return dict([(word, True) for word in words])


def double_words_feature(words, score_fn=BigramAssocMeasures.chi_sq, num=1000):
    # print('双词作为特征')
    double_finder = BigramCollocationFinder.from_words(words)  # 把文本变成双词搭配的形式
    double_words = double_finder.nbest(score_fn, num)  # 使用卡方统计的方法，选择排名前1000的双词
    new_double_words = [u + v for (u, v) in double_words]

    return single_words_feature(new_double_words)


def mix_words_feature(words, score_fn=BigramAssocMeasures.chi_sq, num=1000):
    # print('单双词搭配作为特征')
    double_finder = BigramCollocationFinder.from_words(words)  # 把文本变成双词搭配的形式
    double_words = double_finder.nbest(score_fn, num)  # 使用卡方统计的方法，选择排名前1000的双词
    new_double_words = [u + v for (u, v) in double_words]

    a = single_words_feature(words)
    b = single_words_feature(new_double_words)
    a.update(b)  # 把字典b合并到字典a中

    return a  # 所有单个词和双个词一起作为特征


def jieba_words_feature(num=2400):  # num为特征维度
    # print('结巴分词')
    pos_words = []
    neg_words = []
    # 将分词完成后的词语分类存进集合
    for words in read_text('zl_pos.txt'):
        for word in words:
            pos_words.append(word)
    for words in read_text('zl_neg.txt'):
        for word in words:
            neg_words.append(word)

    # 用FreqDist来表示单词的整体频率，ConditionalFreqDist的条件是类别标签
    word_f = FreqDist()  # FreDist()构建出一个词为key,词频为value,按词频由大到小排列
    both_word_f = ConditionalFreqDist()
    for word in pos_words:
        word_f[word] += 1
        both_word_f['pos'][word] += 1
        # print('pos:', word_f[word])
    # print(both_word_f.N())
    for word in neg_words:
        word_f[word] += 1
        both_word_f['neg'][word] += 1
        # print('neg:', word_f[word])
    # print(word_f.items())
    # print(both_word_f.N())

    pos_words_num = both_word_f['pos'].N()
    neg_words_num = both_word_f['neg'].N()
    words_num = pos_words_num + neg_words_num

    # 用BigramAssocMeasures.chi_sq函数(卡方)为词汇计算评分，然后按分数排序，放入一个集合里
    word_scores = {}
    for word, freq in word_f.items():
        pos_score = BigramAssocMeasures.chi_sq(both_word_f['pos'][word], (freq, pos_words_num), words_num)
        # print('pos:', pos_score)
        neg_score = BigramAssocMeasures.chi_sq(both_word_f['neg'][word], (freq, neg_words_num), words_num)
        word_scores[word] = pos_score + neg_score  # 该词语总信息量

    best_vals = sorted(word_scores.items(), key=lambda item: item[1], reverse=True)[:num]  # 倒叙排序
    best_words = set([w for w, s in best_vals])
    print(best_words)

    h = open('zl_best_words.txt', 'w+', encoding='utf-8')
    h.write(str(best_words))
    h.close()

    # print(dict([(word, True) for word in best_words]))
    return dict([(word, True) for word in best_words])


def build_features(i):  # i为特征维度
    # feature = single_words_feature(text())
    # feature = double_words_feature(text(), score_fn=BigramAssocMeasures.chi_sq, num=i)
    # feature = mix_words_feature(text(), score_fn=BigramAssocMeasures.chi_sq, num=i)
    feature = jieba_words_feature(i)  # 结巴分词
    # print(feature)

    pos_features = []
    for items in read_text('zl_pos.txt'):
        a = {}
        for item in items:
            if item in feature.keys():
                a[item] = 'True'
        pos_words = [a, 'pos']  # 为积极文本赋予"pos"
        pos_features.append(pos_words)

    neg_features = []
    for items in read_text('zl_neg.txt'):
        a = {}
        for item in items:
            if item in feature.keys():
                a[item] = 'True'
        neg_words = [a, 'neg']  # 为消极文本赋予"neg"
        neg_features.append(neg_words)

    return pos_features, neg_features


def train_and_test(num):
    posFeatures, negFeatures = build_features(num)  # 获得训练数据
    # print(posFeatures)
    # print(negFeatures)

    shuffle(posFeatures)  # 把文本的排列随机化
    shuffle(negFeatures)  # 把文本的排列随机化
    train = posFeatures[9000:] + negFeatures[3000:]  # 训练集(80%)

    test = posFeatures[:9000] + negFeatures[:3000]  # 预测集(验证集)(20%)
    data, tag = zip(*test)  # 分离测试集合的数据和标签，便于验证和测试

    return train, data, tag


def score(classifier, num):
    classifier = SklearnClassifier(classifier)  # 在nltk中使用scikit-learn的接口
    train, data, tag = train_and_test(num)
    classifier.train(train)  # 训练分类器
    pred = classifier.classify_many(data)  # 对测试集的数据进行分类，给出预测的标签
    # print(pred)

    n = 0
    s = len(pred)
    for i in range(0, s):
        if pred[i] == tag[i]:
            n = n + 1

    return n / s  # 对比分类预测结果和人工标注的正确结果，给出分类器准确度

'''
def test():
    k = 200
    while k <= 10000:
        print('when k is %d' % k)
        print('BernoulliNB`s accuracy is %f' % score(BernoulliNB(), k))
        print('MultinomiaNB`s accuracy is %f' % score(MultinomialNB(), k))
        print('LogisticRegression`s accuracy is  %f' % score(LogisticRegression(), k))
        # print('SVC`s accuracy is %f' % score(SVC(), k))
        print('LinearSVC`s accuracy is %f' % score(LinearSVC(), k))
        # print('NuSVC`s accuracy is %f' % score(NuSVC(), k))
        print('**********************************************************************')
        k += 1000
        # break
    while k <= 10000000:
        print('when k is %d' % k)
        print('BernoulliNB`s accuracy is %f' % score(BernoulliNB(), k))
        print('MultinomiaNB`s accuracy is %f' % score(MultinomialNB(), k))
        print('LogisticRegression`s accuracy is  %f' % score(LogisticRegression(), k))
        # print('SVC`s accuracy is %f' % score(SVC(), k))
        print('LinearSVC`s accuracy is %f' % score(LinearSVC(), k))
        # print('NuSVC`s accuracy is %f' % score(NuSVC(), k))
        print('**********************************************************************')
        k *= 2
'''
jieba_words_feature()
# test()
def save(i):
    # best_words = jieba_words_feature(i)

    posFeatures, negFeatures = build_features(i)
    shuffle(posFeatures)  # 把文本的排列随机化
    shuffle(negFeatures)  # 把文本的排列随机化
    train = posFeatures + negFeatures

    BernoulliNB_classifier = SklearnClassifier(BernoulliNB())
    BernoulliNB_classifier.train(train)
    pickle.dump(BernoulliNB_classifier, open('classifier.pkl', 'wb'))

# save(600)