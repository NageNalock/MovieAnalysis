#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/25 14:42
# @Author  : Daisy
# @Site    : 
# @File    : 1_ogin_douban.py
# @Software: PyCharm Community Edition

import requests
import http.cookiejar as hc
import re
import time
from bs4 import BeautifulSoup

try:
    from PIL import Image
except:
    pass

# 构造 Request headers
agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
headers = {
    "Host": "www.douban.com",
    "Referer": "https://www.douban.com/",
    'User-Agent': agent,
}

# 使用cookie登录信息
session = requests.session()  # 构建session
session.cookies = hc.LWPCookieJar(filename='cookies')  # 从文件加载cookie

try:
    session.cookies.load(ignore_discard=True)
    print('成功加载cookie')
except:
    print("未能加载cookie")


#################################################################################
# 获取验证码
def get_captcha(url):
    # 获取验证码
    print('获取验证码', url)
    captcha_url = url
    r = session.get(captcha_url, headers=headers)
    f = open('captcha.jpg', 'wb')
    f.write(r.content)
    f.close()
    # 用pillow 的 Image 显示验证码
    # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
    im = Image.open('captcha.jpg')
    im.show()
    im.close()
    captcha = input("请输入验证码\n>")
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
    login_age = session.post(post_url, data=post_data, headers=headers)
    # 保存cookies
    # session.cookies.save()

    if isLogin():
        print('登录成功')
    else:
        print('登录失败')




# 爬取评论
def get_comment(filename):  # filename为爬取得内容保存的文件
    begin = 1
    comment_url = 'https://movie.douban.com/subject/26363254/comments'
    next_url = '?start=20&limit=20&sort=new_score&status=P'
    headers2 = {
        "Host": "movie.douban.com",
        "Referer": "https://www.douban.com/",
        'User-Agent': agent,
        'Connection': 'keep-alive',
    }
    f = open(filename, 'w+', encoding='utf-8')
    while True:
        time.sleep(6)
        html = session.get(url=comment_url + next_url, headers=headers2)
        soup = BeautifulSoup(html.text, 'html.parser')

        # 爬取当前页面的所有评论
        result = soup.find_all('div', {'class': 'comment'})  # 爬取得所有的短评
        for item in result:
            s = str(item)
            count2 = s.find('<p class="">')
            count3 = s.find('</p>')
            s2 = s[count2 + 12:count3]  # 抽取字符串中的评论
            if 'class' not in s2:
                f.write(s2)

        # 获取下一页的链接
        next_url = soup.find_all('div', {'id': 'paginator'})
        pattern3 = r'href="(.*?)">后页'
        if len(next_url) == 0:
            break
        next_url = re.findall(pattern3, str(next_url[0]))  # 得到后页的链接
        if len(next_url) == 0:  # 如果没有后页的链接跳出循环
            break
        next_url = next_url[0]
        print('%d爬取下一页评论...' % begin)
        begin = begin + 1
        # 如果爬取了5次则多休息2秒
        if begin % 6 == 0:
            time.sleep(40)
            print('休息...')
        print(next_url)
    f.close()


if isLogin():
    print('您已经登录')
else:
    # account = input('请输入你的用户名\n>  ')
    # secret = input("请输入你的密码\n>  ")
    # login(account, secret)
    login()

file_name = 'key3.txt'
get_comment(file_name)
