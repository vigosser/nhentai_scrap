import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import datetime
import random
import sqlite3
import json
import re
import datetime
import os
import vthread
url='https://nhentai.net/search/?q=chinese&page={}'
def log(str):
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + '======' + str)

class Getfile(object):  # 下载文件

    def __init__(self, url):
        self.url = url

    def getheaders(self):
        try:
            r = requests.head(self.url)
            headers = r.headers
            return headers
        except:
            print('无法获取下载文件大小')
            exit()

    def getfilename(self):  # 获取默认下载文件名
        if 'Content-Disposition' in self.getheaders():
            file = self.getheaders().get('Content-Disposition')
            filename = re.findall('filename="(.*)"', file)
            if filename:
                return filename[0]

    def downfile(self, filename,name):  # 下载文件
        self.r = requests.get(self.url, stream=True)
        with open('data/{}/'.format(name)+filename, "wb") as code:
            for chunk in self.r.iter_content(chunk_size=1024):  # 边下载边存硬盘
                if chunk:
                    code.write(chunk)
        time.sleep(1)

def request_until_success(url):
    payload = {}
    headers = {}
    flag = True
    res = ''
    while flag:
        try:
            res = requests.request("GET", url, headers=headers,
                                   data=payload, timeout=5).text.strip()
        except BaseException:
            log('blocked by website')
            time.sleep(2)
        else:
            flag = False
    return res

@vthread.pool(30)
def download_pic(j,_count,_name):
    u = j.a.img['data-src']
    u = u.replace('t.jpg', '.jpg').replace('t.nhentai.net', 'i.nhentai.net')
    Getfile(u).downfile(str(_count) + '.jpg', _name)
    log(str(_count))


# @vthread.pool(8)
def get_singl(k):
    link = 'https://nhentai.net' + k.a['href']
    code=k.a['href'].split('/')[-2]
    name = k.find('div', class_='caption').text
    name=name.replace('\\','').replace('/','').replace(':','').replace('！','').replace('\"','').\
        replace('*','').replace('<','').replace('>','').replace('|','').replace('?','')\
        .replace(' ','_')
    # if len(name)>30:
    #     name=name[0:30]
    rsp = request_until_success(link)
    if os.path.exists('data/' + name):
        return
    else:
        os.mkdir('data/' + name)
        log('mkdir:{}'.format(name))

    sp = BeautifulSoup(rsp.strip(), 'html.parser')
    count = 0
    for _j in sp.findAll('div', class_='thumb-container'):
        download_pic(_j, count, name)
        count = count + 1
    vthread.pool.waitall()
    log('complete:{} page on {}'.format(str(count), name))

for i in range(1,100):
    response = request_until_success(url.format(i))
    soup = BeautifulSoup(response.strip(), 'html.parser')
    lists= soup.findAll('div',class_='gallery')
    for _k in lists:
        get_singl(_k)
