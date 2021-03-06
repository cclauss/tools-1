# coding=utf-8
import urllib.request
from urllib.parse import urljoin, urlencode
import http.cookiejar
import socket
import os
from hashlib import md5
from base64 import b64encode, b64decode
import sys
import time
import re
from bs4 import BeautifulSoup
socket.setdefaulttimeout(10)

# html源码获取, 其实用requests更方便, 但
def crawl(url, referer='https://jandan.net/', host='jandan.net'):
    cookie_support = urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
    # proxy_support = urllib.request.ProxyHandler({"http":"115.159.50.56:8080"})
    opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)
    opener.addheaders = [('User-agent', 'Mozilla/5.0'), ('Accept', '*/*'), ('Referer', referer), ('Host', host)]
    try:
        urlop = opener.open(url)
        html = urlop.read().decode('utf-8')
        urlop.close()
        return html
    except Exception as e:
        print(e, url)
        sys.exit(0)

# 组装绝对路径
def destFile(url, store_dir):
    if not os.path.isdir(store_dir):
        os.mkdir(store_dir)
    pos = url.rindex('/')
    return os.path.join(store_dir, url[pos+1:])

# 递归遍历
def start_request(url):
    global store_dir
    html = crawl(url)
    print("now crawling : {0}".format(url))
    soup = bs(html, "html.parser")
    next_page = soup.find('a', class_='next-comment-page')
    extractPic(soup)
    if next_page is not None:
        start_request(urljoin(url, next_page.get('href')))

# md5 hash
def md5_hash(strs):
    return md5(strs.encode('utf-8')).hexdigest()
        
# 由图片hash获取真实地址
def getUrl(n, x):
    k = 'DECODE'
    f = 0
    x = md5_hash(x)
    w = md5_hash(x[0:16])
    u = md5_hash(x[16:32])
    t = n[0:4]
    r = w + md5_hash(w + t)
    n = n[4:]
    m = b64decode(n)
    h = [i for i in range(256)]
    q = [ord(r[j%len(r)]) for j in range(256)]
    o = 0
    for i in range(256):
        o = (o + h[i] + q[i]) % 256
        tmp = h[i]
        h[i] = h[o]
        h[o] = tmp
    v = o = 0
    l = ''
    for i in range(len(m)):
        v = (v + 1) % 256
        o = (o + h[v]) % 256
        tmp = h[v]
        h[v] = h[o]
        h[o] = tmp
        l += chr(ord(chr(m[i])) ^ (h[(h[v] + h[o]) % 256]))
    return l[26:]
          
# 图片下载
def extractPic(soup):
    global store_dir, app_secret
    #aaa = soup.find_all("a", text="[查看原图]")
    spans = soup.find_all('span', class_='img-hash')
    for span in spans:
        img_hash = span.text
        href = getUrl(img_hash + '==', app_secret)
        if href.startswith('//'):
            href = "http:{0}".format(href)
        elif href.startswith('http'):
            pass
        try:
            file = destFile(href, store_dir)
            if os.path.exists(file):
                print('%s has been crawled' % file)
                continue
            urllib.request.urlretrieve(href, file)
            print(href)
        except Exception as e:
            print(e, href)
            urllib.request.urlretrieve(href, destFile(href, store_dir))

# 妹子图下载
if __name__ == '__main__':
    html = crawl('http://jandan.net/ooxx')  #可以改成 无聊图(pic)/ 画廊(drawings) / 妹子图(ooxx) 版块的首页
    js_reg = re.findall(r'src="//cdn.jandan.net/static/min/[\w\d\.]+.js"', html)
    js_url = 'https:' + js_reg[0][5:-1]
    js_html = crawl(js_url)
    
    app_secret = re.findall(r'c=[\w\d\_]+\(e,"[\w\d]+"\);', js_html)
    app_secret = app_secret[0].split('"')[1]

    store_dir = r'F:\ooxx'  #保存路径
    from_page = input('请输入开始页:')
    if from_page.isdigit() and from_page != '0':
        url = 'http://jandan.net/ooxx/page-{0}#comments'.format(from_page)
        try:
            start_request(url)
            print('finished')
        except KeyboardInterrupt as e:
            print('now quit')
            sys.exit(0)
    else:
        print('开始页必须为正整数')
