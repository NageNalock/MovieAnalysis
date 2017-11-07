#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/23 18:57
# @Author  : Daisy
# @Site    : 
# @File    : spider_cookie_test.py
# @Software: PyCharm Community Edition

import re
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36',
    'Referer': 'https://www.douban.com/accounts/login?source=movie'}
s = requests.Session()
# 获取验证码
imgdata = s.get("https://www.douban.com/accounts/login?source=movie", headers=headers, verify=False).text
print(imgdata)
pa = re.compile(r'<img id="captcha_image" src="(.*?)" alt="captcha" class="captcha_image"/>')
img_url = re.findall(pa, imgdata)[0]
# print(img_url)
picdata = s.get(img_url).content
with open("douban.jpg", 'wb') as f:
    f.write(picdata)

pa_id = re.compile(r'<input type="hidden" name="captcha-id" value="(.*?)"/>')
capid = re.findall(pa_id, imgdata)[0]
print(capid)

capimg = input("输入验证码：")
payload = {
    "source": "movie",
    "redir": "https://movie.douban.com/",
    "form_email": "magekafka@gmail.com",
    "form_password": "DaiSai999",
    "captcha-solution": capimg,
    "captcha-id": capid,
    "login": "登录"
}

log_url = "https://accounts.douban.com/login"
data1 = s.post(log_url, data=payload, verify=False)  # 绕过了SSL验证
print(data1.status_code)

data2 = s.get('https://www.douban.com/people/146448257/')
print(data2.status_code)
print(data2.text)