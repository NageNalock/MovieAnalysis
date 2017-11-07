#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/11 21:27
# @Author  : Daisy
# @Site    : 
# @File    : 1_login_and_get_3.0.py
# @Software: PyCharm Community Edition


import requests
import re
import time
from bs4 import BeautifulSoup
from PIL import Image
import http.cookiejar as hc
import sys

sys.setrecursionlimit(1000000)

# 构造 Request headers
agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
headers = {
    "Host": "www.douban.com",
    "Referer": "https://www.douban.com/",
    'User-Agent': agent,
}

session = requests.session()  # 构建session
session.cookies = hc.LWPCookieJar(filename='cookies')


#################################################################################
# 获取验证码
# <img id="captcha_image" src="https://www.douban.com/misc/captcha?id=xD1BqQR6ggorCdW1ZPmFbIkr:en&amp;size=s" alt="captcha" class="captcha_image">
def get_captcha(url):
    # 获取验证码
    print('验证码地址', url)
    captcha = input("请输入验证码\n>")
    cap = session.get(url, headers=headers)
    f = open('captcha.jpg', 'wb')
    f.write(cap.content)
    f.close()
    cap_jpg = Image.open('captcha.jpg')
    cap_jpg.show()
    cap_jpg.close()
    return captcha


def isLogin():
    # 登录个人主页，查看是否登录成功
    url = 'https://www.douban.com/people/165842919/'
    login_code = session.get(url, headers=headers, allow_redirects=False).status_code  # 返回请求码
    if login_code == 200:  # 200代表请求成功
        return True
    else:
        return False


def login(acount='magekafka@gmail.com', secret='DaiSai999'):
    douban = "https://www.douban.com/"
    htmlcha = session.get(douban, headers=headers).text
    patterncha = r'id="captcha_image" src="(.*?)" alt="captcha"'
    httpcha = re.findall(patterncha, htmlcha)
    pattern2 = r'type="hidden" name="captcha-id" value="(.*?)"'
    hidden_value = re.findall(pattern2, htmlcha)
    print(hidden_value)

    post_data = {
        "source": "index_nav",
        'form_email': acount,
        'form_password': secret,
    }
    if len(httpcha) > 0:
        print('验证码连接', httpcha)
        capcha = get_captcha(httpcha[0])
        post_data['captcha-solution'] = capcha
        post_data['captcha-id'] = hidden_value[0]

    print(post_data)
    post_url = 'https://www.douban.com/accounts/login'
    session.post(post_url, data=post_data, headers=headers)
    # 保存cookies
    session.cookies.save()

    if isLogin():
        print('登录成功')
    else:
        print('登录失败')


# 判断评论情感
def emotion_judge(comment):
    info = comment
    judge = info.find('<span class="allstar40 rating" title="推荐"></span>')
    if judge > 0:
        return 1
    judge = info.find('<span class="allstar50 rating" title="力荐"></span>')
    if judge > 0:
        return 2
    judge = info.find('<span class="allstar20 rating" title="较差"></span>')
    if judge > 0:
        return -1
    judge = info.find('<span class="allstar10 rating" title="很差"></span>')
    if judge > 0:
        return -2
    return 0


# 爬取评论
def get_comment(page, n_url='?start=20&limit=20&sort=new_score&status=P'):  # filename为爬取得内容保存的文件
    # begin = 1

    # next_url = '?start=20&limit=20&sort=new_score&status=P'
    headers2 = {
        "Host": "movie.douban.com",
        "Referer": "https://www.douban.com/",
        'User-Agent': agent,
        'Connection': 'keep-alive',
    }
    # f = open(filename, 'w+', encoding='utf-8')
    time.sleep(6)
    if page % 6 == 0:
        print('休息...')
        time.sleep(40)
    time.sleep(6)
    html = session.get(comment_url + n_url, headers=headers2)
    soup = BeautifulSoup(html.text, 'html.parser')
    print('爬取第 %d 页' % (page))
    page += 1

    # 爬取当前页面的所有评论
    result = soup.find_all('div', {'class': 'comment'})  # 爬取得所有的短评
    for item in result:
        s = str(item)
        # print('########')
        # print(s)
        count2 = s.find('<p class="">')
        count3 = s.find('</p>')
        s2 = s[count2 + 12:count3]  # 抽取字符串中的评论
        judge = emotion_judge(s)
        # print('s2=', s2)
        if 'class' not in s2:
            if judge > 0:
                # f.write('test')
                f.write(s2)
                # print('积极评论')
            if judge < 0:
                # g.write('test')
                g.write(s2)
                # print('消极评论')
                # if judge == 0:
                # print('中立评论 不保存')

                # 获取下一页的链接
    next_url = soup.find_all('div', {'id': 'paginator'})
    pattern3 = r'href="(.*?)">后页'
    next_url_1 = re.findall(pattern3, str(next_url[0]))  # 得到后页的链接
    if len(next_url) == 0 and len(next_url_1):  # 如果没有后页的链接跳出循环
        print('已到最后一页')
        f.close()
        g.close()
    else:
        next_url = next_url_1[0]
        get_comment(page, next_url)


if isLogin():
    print('您已经登录')
else:
    # account = input('请输入你的用户名\n>  ')
    # secret = input("请输入你的密码\n>  ")
    # login(account, secret)
    login()

page = 1
file_name_pos = 'zl_pos.txt'
file_name_neg = 'zl_neg.txt'
comment_url = 'https://movie.douban.com/subject/26363254/comments'
f = open(file_name_pos, 'w+', encoding='utf-8')
g = open(file_name_neg, 'w+', encoding='utf-8')
get_comment(page)
