#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/21 22:43
# @Author  : Daisy
# @Site    : Suzhou
# @File    : spider.py
# @Software: PyCharm Community Edition

from urllib import request
from bs4 import BeautifulSoup as bs
import re
import jieba
import urllib.request
import pandas as pd
import numpy as np
import requests
import time
import http.cookiejar as hc
import
try:
    from PIL import Image
except:
    pass
import requests


agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
headers = {
    "Host": "www.douban.com",
    "Referer": "https://www.douban.com/",
    'User-Agent': agent,
}

#使用cookie登录信息
session=requests.session()
session.cookies=hc.LWPCookieJar(filename='cookies')

try:
    session.cookies.load(ignore_discard=True)
    print('成功加载cookie')
except:
    print("cookie 未能加载")

# 获取验证码
def get_captcha(url):
    #获取验证码
    print('获取验证码',url)
    captcha_url = url
    r = session.get(captcha_url, headers=headers)
    print('test')
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()
    # 用pillow 的 Image 显示验证码
    # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
    captcha = input("please input the captcha\n>")
    return captcha

def isLogin():
    #登录个人主页，查看是否登录成功
    url='https://www.douban.com/people/151607908/'
    login_code=session.get(url,headers=headers,allow_redirects=False).status_code
    if login_code==200:
        return True
    else:
        return False


def login(acount='magekafka@gmail.com', secret='DaiSai999'):
    douban="https://www.douban.com/"
    htmlcha=session.get(douban,headers=headers).text
    patterncha=r'id="captcha_image" src="(.*?)" alt="captcha"'
    httpcha=re.findall(patterncha,htmlcha)
    pattern2=r'type="hidden" name="captcha-id" value="(.*?)"'
    hidden_value=re.findall(pattern2,htmlcha)
    print(hidden_value)

    post_data = {
        "source": "index_nav",
        'form_email': acount,
        'form_password': secret
    }
    if len(httpcha)>0:
        print('验证码连接',httpcha)
        capcha=get_captcha(httpcha[0])
        post_data['captcha-solution']=capcha
        post_data['captcha-id']=hidden_value[0]

    print (post_data)
    post_url='https://www.douban.com/accounts/login'
    login_page=session.post(post_url,data=post_data,headers=headers)
    #保存cookies
    session.cookies.save()

    if isLogin():
        print('登录成功')
    else:
        print('登录失败')


#################################################################
# 获取电影ID和电影名
def get_movie_name_and_id():
    response = request.urlopen('https://movie.douban.com/cinema/nowplaying/suzhou/')
    html_data = response.read().decode('utf-8')  # 读取数据并解做utf-8
    # print(html_data)

    soup = bs(html_data, "html.parser")  # 字符串
    nowplaying_movie = soup.find_all('div', id='nowplaying')  # <div id='nowplaying'>
    # print(nowplaying_movie[0])
    nowplaying_movie_list = nowplaying_movie[0].find_all('li', class_='list-item')
    # print(nowplaying_movie_list[1])

    # 两层循环获取电影ID和名字
    nowplaying_list = []
    for item in nowplaying_movie_list:
        nowplaying_dict = {}  # 制作词典
        nowplaying_dict['id'] = item['data-subject']
        for tag_img_item in item.find_all('img'):  # 电影名字在img的alt中
            nowplaying_dict['name'] = tag_img_item['alt']
            nowplaying_list.append(nowplaying_dict)
    return nowplaying_list


# print(nowplaying_list)

def get_comments(movie_id, page_num):  # 获取评论
    # 例如:https://movie.douban.com/subject/26363254/comments?start=0&limit=20
    # id为26363254的电影,start=0表示第0条评论
    # 解析
    start = (page_num - 1) * 20  # 一页20个评论
    requrl = 'https://movie.douban.com/subject/' + movie_id + '/comments' + '?' + 'start=' + str(start) + '&limit=20'
    headers2 = {
        "Host": "movie.douban.com",
        "Referer": "https://www.douban.com/",
        'User-Agent': agent,
        'Connection': 'keep-alive',
    }
    html_data = session.get(url=requrl, headers=headers2)

    response = request.urlopen(requrl)
    # html_data = response.read().decode('utf-8')
    soup = bs(html_data.text, 'html.parser')
    comment_div_list = soup.find_all('div', class_='comment')
    # print(comment_div_list)
    each_comment_list = []  # 存放影评
    for item in comment_div_list:
        if item.find_all('p')[0].string is not None:  # p标签(即影评)非空
            each_comment_list.append(item.find_all('p')[0].string)
    return each_comment_list


# print(each_comment_list)

# 数据清洗
if isLogin():
    print('您已经登录')
else:
    # account = input('请输入你的用户名\n>  ')
    # secret = input("请输入你的密码\n>  ")
    # login(account, secret)
    login()

file_name='zhanlang.txt'
commentList = []
# name_and_id = get_movie_name_and_id()
for i in range(20):
    num = i + 1
    print('正在获取第 %s 页' % num)
    commentList_temp = get_comments('11502973', num)
    commentList.append(commentList_temp)
    time.sleep(6)
    if num % 5 == 0:
        print('休息...')
        time.sleep(40)

# print(commentList)
# 将列表中的数据转换为字符串
comments = ''
for k in range(len(commentList)):
    comments = comments + (str(commentList[k])).strip()
# print(comments[3])
cleaned_comments = comments.replace('\\n', '').replace('[', '').replace(']', '').replace(' ', '').replace('\'', '')
print(cleaned_comments)
