#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/26 13:10
# @Author  : Daisy
# @Site    : 
# @File    : 3_analysis_douban.py
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

                    if w in deny_word:
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
                    if w in deny_word:
                        d += 1
                if judge_odd(d) == 'odd':
                    negcount *= -1.0
                    negcount_f += negcount
                    negcount = 0
                else:
                    negcount_f += negcount
                    negcount = 0
                a = i + 1

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
    # print(count2)
    score_array = np.array(count2[0])  # 建立矩阵
    Pos = np.sum(score_array[:, 0])
    Neg = np.sum(score_array[:, 1])
    AvgPos = np.mean(score_array[:, 0])
    AvgPos = float('%.1f' % AvgPos)
    AvgNeg = np.mean(score_array[:, 1])
    AvgNeg = float('%.1f' % AvgNeg)
    StdPos = np.std(score_array[:, 0])
    StdPos = float('%.1f' % StdPos)
    StdNeg = np.std(score_array[:, 1])
    StdNeg = float('%.1f' % StdNeg)
    score.append([Pos, Neg, AvgPos, AvgNeg, StdPos, StdNeg])
    return score[0]


# test1 = '你们的手机真不好用！非常生气，我非常郁闷！！！！'
# test2= '我好开心啊，非常非常非常高兴！今天我得了一百分，我很兴奋开心，愉快，开心'

txt = open('zhanlang.txt', encoding='utf-8')
text = txt.readlines()
text = str(text)
txt.close()
print('读入成功')
score = sentiment_score_list(text)
# print('%s的评价情况:' % (name_and_id[0]['name']))
# print('积分分数:%s 消极分数:%s' % (score[0],score[1]))
print('积极分数:%s,消极分数:%s,平均积极分数:%s,平均消极分数:%s,积极分数标准差:%s,消极分数标准差:%s' % (
score[0], score[1], score[2], score[3], score[4], score[5]))
