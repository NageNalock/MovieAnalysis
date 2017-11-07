#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/22 22:00
# @Author  : Daisy
# @Site    : 
# @File    : test1.py
# @Software: PyCharm Community Edition

import jieba
import numpy as np


# 打开词典文件，返回列表
def open_dict(Dict='char', path=r'/Textming/'):
    path = path + '%s.txt' % Dict
    dictionary = open(path, 'r', encoding='utf-8')
    dict = []
    for word in dictionary:
        word = word.strip('\n')
        dict.append(word)
    return dict


def judge_odd(num):  # 判断奇偶数,否定之否定
    if (num % 2) == 0:
        return 'even'
    else:
        return 'odd'


# 全局变量
deny_word = open_dict(Dict='deny')
posdict = open_dict(Dict='positive')
negdict = open_dict(Dict='negative')

# 设置程度词权重
degree_word = open_dict(Dict='degree')
degree_4 = degree_word[degree_word.index('extreme') + 1:degree_word.index('very')]  # 权重4，即在情感词前乘以4
degree_3 = degree_word[degree_word.index('very') + 1:degree_word.index('more')]  # 权重3
degree_2 = degree_word[degree_word.index('more') + 1:degree_word.index('ish')]  # 权重2
degree_h = degree_word[degree_word.index('ish') + 1:degree_word.index('last')]  # 权重0.5


def sentiment_score_list(dataset):
    seg_sentence = dataset.split('\n')

    count1 = []
    count2 = []
    for sen in seg_sentence:  # 循环遍历每一个评论
        segtmp = jieba.lcut(sen, cut_all=False)  # 把句子进行分词，以列表的形式返回
        i = 0  # 记录扫描到的词的位置
        a = 0  # 记录情感词的位置
        poscount = 0  # 积极词的第一次分值
        poscount_f = 0  # 积极词的最后分值
        negcount = 0
        negcount_f = 0
        for word in segtmp:
            if word in posdict:  # 判断词语是否是情感词
                poscount += 1
                c = 0
                for w in segtmp[a:i]:  # 扫描情感词前的程度词
                    if w in degree_4:
                        poscount *= 4.0
                    elif w in degree_3:
                        poscount *= 3.0
                    elif w in degree_2:
                        poscount *= 2.0
                    elif w in degree_h:
                        poscount *= 0.5
                    elif w in deny_word:
                        c += 1
                if judge_odd(c) == 'odd':  # 扫描情感词前的否定词数
                    poscount *= -1.0
                    poscount_f += poscount
                    poscount = 0
                else:
                    poscount_f += poscount
                    poscount = 0
                a = i + 1  # 情感词的位置变化

            elif word in negdict:  # 消极情感的分析
                negcount += 1
                d = 0
                for w in segtmp[a:i]:
                    if w in degree_4:
                        negcount *= 4.0
                    elif w in degree_3:
                        negcount *= 3.0
                    elif w in degree_2:
                        negcount *= 2.0
                    elif w in degree_h:
                        negcount *= 0.5
                    elif w in degree_word:
                        d += 1
                if judge_odd(d) == 'odd':
                    negcount *= -1.0
                    negcount_f += negcount
                    negcount = 0
                else:
                    negcount_f += negcount
                    negcount = 0
                a = i + 1
            elif word == '！' or word == '!':  ##判断句子是否有感叹号
                for w2 in segtmp[::-1]:  # 扫描感叹号前的情感词，发现后权值+2，然后退出循环
                    if w2 in posdict or negdict:
                        poscount_f += 2
                        negcount_f += 2
                        break
            i += 1  # 扫描词位置前移

            # 防止出现负数
            pos_count = 0
            neg_count = 0
            if poscount_f < 0 and negcount_f > 0:
                neg_count += negcount_f - poscount_f
                pos_count = 0
            elif negcount_f < 0 and poscount_f > 0:
                pos_count = poscount_f - negcount_f
                neg_count = 0
            elif poscount_f < 0 and negcount_f < 0:
                neg_count = -poscount_f
                pos_count = -negcount_f
            else:
                pos_count = poscount_f
                neg_count = negcount_f

            count1.append([pos_count, neg_count])
        count2.append(count1)
        count1 = []

    score = []
    print(count2)
    score_array = np.array(count2[0])  # 建立矩阵
    Pos = np.sum(score_array[:, 0])
    Neg = np.sum(score_array[:, 1])
    score.append([Pos, Neg])
    '''
    score = []
    for review in count2:
        score_array = np.array(review)#建立矩阵
        Pos = np.sum(score_array[:, 0])
        Neg = np.sum(score_array[:, 1])
        score.append([Pos, Neg])
    '''
    return score[0]



data = '你就是个王八蛋，混账玩意!你们的手机真不好用！非常生气，我非常郁闷！！！！'
data2 = '我好开心啊，非常非常非常高兴！今天我得了一百分，我很兴奋开心，愉快，开心'

score1 = sentiment_score_list(data)
print('积分分数:%s 消极分数:%s' % (score1[0], score1[1]))
