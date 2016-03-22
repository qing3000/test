# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 07:39:55 2016

@author: zhangq
"""

import bs4
from bs4 import BeautifulSoup
import urllib2
import codecs


#product_list_url = 'test.html'
#data = urllib2.urlopen(product_list_url)
f = codecs.open('test.html', encoding='gb2312', errors = 'ignore')
data = f.read()

soup = BeautifulSoup (data)
txt = soup.find_all('pre')[0].text
txts = txt.split('\r\n')
newtxt = u''
for oneline in txts:
    if oneline == u'':
        newtxt += '\r\n'
    else:
        newtxt += oneline

f = codecs.open('wenmian.txt','w', encoding = 'utf-8')
f.write(newtxt)
f.close()

