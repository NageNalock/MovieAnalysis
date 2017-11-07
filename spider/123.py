__author__ = 'jason'
import requests
import time
import re
from bs4 import BeautifulSoup
import http.cookiejar as hc

s = requests.session()
print("session1 :",s)

url_login = 'https://accounts.douban.com/login'
agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'

formdata = {
    'redir': 'https://www.douban.com',
    'form_email': 'magekafka@gmail.com',
    'form_password': 'DaiSai999',
    'login': u'登陆'
}
headers = {'User-Agent': agent}
######################################################################
session = requests.session()  # 若之前cookie登陆成功则采用上次的cookie
print("session1 :",session)
session.cookies = hc.LWPCookieJar(filename='cookies')  # 从文件加载cookie
print("session2 :",session)

try:
    session.cookies.load(ignore_discard=True)
    print('成功加载cookie')
except:
    print("未能加载cookie")
print("session3 :",session)
#####################################################################
r = s.post(url_login, data = formdata, headers = headers)
content = r.text
soup = BeautifulSoup(content, 'html.parser')
captcha = soup.find('img', id = 'captcha_image')#当登陆需要验证码的时候
if captcha:
    captcha_url = captcha['src']
    re_captcha_id = r'<input type="hidden" name="captcha-id" value="(.*?)"/'
    captcha_id = re.findall(re_captcha_id, content)
    print(captcha_id)
    print(captcha_url)
    captcha_text = input('Please input the captcha:')
    formdata['captcha-solution'] = captcha_text
    formdata['captcha-id'] = captcha_id
    r = s.post(url_login, data = formdata, headers = headers)
with open('contacts.txt', 'w+', encoding = 'utf-8') as f:
    f.write(r.text)

def get_movie_sort():
    time.sleep(1)
    movie_url = 'https://movie.douban.com/chart'
    html = session.get(movie_url, headers=headers)
    soup = BeautifulSoup(html.text, 'html.parser')
    result = soup.find_all('a', {'class': 'nbg'})
    print(result)


# 爬取评论
def get_comment(filename):  # filename为爬取得内容保存的文件
    begin = 1
    comment_url = 'https://movie.douban.com/subject/11600078/comments'
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
file_name = 'key3.txt'
get_comment(file_name)