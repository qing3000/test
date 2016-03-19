# -*- coding: utf-8 -*-
"""
Created on Tue Mar 01 08:58:01 2016

@author: zhangq
"""
import bs4
from bs4 import BeautifulSoup
import urllib2
import codecs
import pdb

def ExportSoup(soup, fn):
    ss = map(unicode,soup)    
    f = codecs.open(fn, encoding = 'utf-8', mode = 'w')
    f.write(ss)
    f.close()

def ExportUnicode(txt, fn):
    txts = txt.split('\r\n')
    newtxt = u''
    for oneline in txts:
        if oneline == u'':
            newtxt += '\r\n'
        else:
            newtxt += oneline

    f = codecs.open(fn,'w', encoding = 'utf-8')
    f.write(newtxt)
    f.close()

    
url = 'http://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=13930093'
data = urllib2.urlopen(url).read().decode('gb2312',errors='ignore')

soup = BeautifulSoup (data)
sec = soup.find('pre')
ExportUnicode(sec.text, '000.txt')
links = sec.findAll('a',href=True)
for i,link in enumerate(links[::-1]):
    print link['href']
    link['href']
    data = urllib2.urlopen(link['href']).read().decode('gb2312',errors='ignore')
    soup = BeautifulSoup (data)
    ExportUnicode(soup.find('pre').text, '%03d.txt' % (i + 1))


