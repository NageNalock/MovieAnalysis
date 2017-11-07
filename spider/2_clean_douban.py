#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/26 12:07
# @Author  : Daisy
# @Site    : 
# @File    : 2_clean_douban.py
# @Software: PyCharm Community Edition
import re

txt = open('zhanlang.txt', encoding='utf-8')
print('读入成功')
g = open('cleaned_zhanlang.txt', 'w+', encoding='utf-8')

line = txt.readline()  # 调用文件的 readline()方法
while line:
    comments = ''
    comments = str(line).strip()
    # comments = comments.replace('\\n', '').replace('[', '').replace(']', '').replace(' ', '').replace('\'', '')
    pattern = re.compile(r'[\u4e00-\u9fa5]+')
    filterdata = re.findall(pattern, comments)
    cleaned_comments = ''.join(filterdata)
    g.write(cleaned_comments)
    print('doing', cleaned_comments)

    line = txt.readline()

txt.close()

g.close()