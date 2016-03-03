# -*- coding: utf-8 -*-
"""
Created on Tue Mar 01 08:58:01 2016

@author: zhangq
"""
import bs4
from bs4 import BeautifulSoup
import re
import urllib2
import codecs
import os
import codecs
import pdb
import collections


def translate(to_translate, to_langage="zh", langage="en"):
    '''Return the translation using google translate
    you must shortcut the langage you define (French = fr, English = en, Spanish = es, etc...)
    if you don't define anything it will detect it or use english by default
    Example:
    print(translate("salut tu vas bien?", "en"))
    hello you alright?'''
    agents = {'User-Agent':"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)"}
    before_trans = 'class="t0">'
    link = "http://translate.google.com/m?hl=%s&sl=%s&q=%s" % (to_langage, langage, to_translate.replace(" ", "+"))
    request = urllib2.Request(link, headers=agents)
    page = urllib2.urlopen(request).read()
    result = page[page.find(before_trans)+len(before_trans):]
    result = result.split("<")[0]
    result=unicode(result,'utf-8')
    return result

def phantom_loadpage(url):
    f=open('loadpage.js','w')
    f.write("var page = require('webpage').create();\n")
    f.write("page.open('"+url+"');\n")
    f.write("page.settings.javascriptEnabled=true;\n")
    f.write("page.onLoadFinished=function(status){\n")
    f.write("setTimeout(function(){console.log(page.content);phantom.exit()},2000);\n");
    f.write("};\n")
    f.close()
    #os.system('phantomjs loadpage.js>htmlcode.txt')
    content=open('htmlcode.html').read()
    return content

def size_string_parser(ss):
    if u'£' in ss:#containing price information
        size_str=ss[:ss.find(' ')]
        price=float(ss[ss.rfind(u'£')+1:ss.rfind(u'.')+2])
    else:#no price information
        price=-1
        size_str=ss.split('-')[0].strip()
    return size_str,price

def ExportSoup(soup, fn):
    ss = unicode.join(u'\n',map(unicode,soup))    
    f = codecs.open(fn, encoding = 'utf-8', mode = 'w')
    f.write(ss)
    f.close()

def AddTranslation(product):
    product['Chinese Title'] = translate(product['title'])
    product['Chinese Description'] = translate(product['description'])
    product['Chinese Material'] = translate(product['material'])
    return product

def save_url_image(url,fn):
    data = urllib2.urlopen(url)
    f=open(fn,'wb')
    f.write(data.read())
    f.close()
    
def ParseNextProductPage(product_url):
    print 'Load the NEXT product page'
    content = phantom_loadpage(product_url)    
    soup = BeautifulSoup (content)
    
    print 'Find all the image links'    
    data=soup.findAll('div',"ThumbNailNavClip")
    img_links=[]
    for child in data[0].ul.children:
        if type(child) == bs4.element.Tag:
            img_link = child.a['rel'][0]
            img_links.append(img_link)
    
    print 'Parse all the details'''    
    department=soup.findAll('li','Breadcrumb')[2].text.strip()
    if 'girl' in department.lower():
        sex='girl'
    else:
        sex='boy'
    
    pdts=[]
    products=soup.findAll('article','Style')    
    for product in products:
        productID = product.findAll('div','ItemNumber')[0].text
        title = product.findAll('div','Title')[0].text.strip()
        contents = product.findAll('div','StyleContent')[0]
        description = contents.div.text.strip()
        description = description.replace(',',';')
        material = contents.contents[3].text.strip()
        material = material.replace(',',';')
        priceStr = product.findAll('div','Price')[0].text
        if ' - ' in priceStr:
            ss = priceStr.split(' - ')
            priceRange = [float(ss[0].strip()[1:]), float(ss[1].strip()[1:])]
        else:
            priceRange = [float(priceStr[1:])] * 2
        options = product.findAll('div','SizeSelector')[0].div('ul')[0].contents[1:]
        prices = []
        sizes = []
        instocks = []
        for option in options:
            instocks.append(option.attrs['class'][0] == 'InStock')
            if ' - ' in option.text:
                ss = option.text.split(' - ')
                sizes.append(ss[0].strip())
                prices.append(float(ss[1].strip()[1:]))
            else:
                sizes.append(option.text.strip())
                prices.append(priceRange[0])
        pdt = collections.OrderedDict([('productID', productID),\
               ('brand', 'Next'),\
               ('department', department),\
               ('sex',sex),\
               ('title',title),\
               ('description', description),\
               ('material' , material),\
               ('price',priceRange),\
               ('sizes',sizes),\
               ('prices', prices),\
               ('instocks' , instocks),\
               ('ImageLinks', img_links)])
        pdt = AddTranslation(pdt)                 
        pdts.append(pdt)
    
    for i, pdt in enumerate(pdts):
        stylewiths = []
        for j, otherPdt in enumerate(pdts):
            if j != i:
                stylewiths.append(otherPdt['productID'])
        pdt['stylewith'] = ';'.join(stylewiths)
    return pdts;

product_list_url = 'http://www.next.co.uk/shop/gender-oldergirls-gender-youngergirls-category-dresses-0#2_2455'
data = urllib2.urlopen(product_list_url)
soup = BeautifulSoup (data)
ExportSoup(soup, 'list.html')

#product_url='http://www.next.co.uk/x57794s9'
#products = ParseNextProductPage(product_url)
#
#f = codecs.open('c:\\temp\\database.csv',encoding = 'utf-8', mode = 'w')
#f.write(u'ID,Brand,Department,Sex,Title,Description,Material,Price,Sizes, Prices,Availability,ImageLinks,TitleChinese,DescriptionChinese,MaterialChinese,StyleWith\n')
#for product in pdts:
#    for i, key in enumerate(product.keys()):
#        ss = product[key]
#        if type(ss) == list:
#            f.write(';'.join(map(str, ss)))
#        else:
#            f.write(ss)
#        if i < len(product.keys()) - 1:
#            f.write(',')
#    f.write('\n')
#f.close()