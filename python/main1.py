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
import subprocess
import re, urlparse

def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    parts= urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )

def translate(to_translate, to_langage="zh", langage="en"):
    '''Return the translation using google translate
    you must shortcut the langage you define (French = fr, English = en, Spanish = es, etc...)
    if you don't define anything it will detect it or use english by default
    Example:
    print(translate("salut tu vas bien?", "en"))
    hello you alright?'''
    agents = {'User-Agent':"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)"}
    before_trans = 'class="t0">'
    link = u"http://translate.google.com/m?hl=%s&sl=%s&q=%s" % (to_langage, langage, to_translate.replace(" ", "+"))
    urlLink = link.encode('utf-8')
    #urlLink = iriToUri
    #print urlLink
    request = urllib2.Request(urlLink, headers=agents)
    page = urllib2.urlopen(request).read()
    result = page[page.find(before_trans)+len(before_trans):]
    result = result.split("<")[0]
    print 'translation done'
    result = unicode(result,'utf-8')
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
    subprocess.call('phantomjs loadpage.js>htmlcode.html', shell=True)
    #os.system('phantomjs loadpage.js>htmlcode.html')
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
    print product['title']
    product['Chinese Title'] = translate(product['title'])
    print product['description']
    ChineseDescription = []    
    for sentence in product['description'].split('\n'):
        ChineseDescription.append(translate(sentence))
    product['Chinese Description'] = u'\n'.join(ChineseDescription)
    print product['material']
    product['Chinese Material'] = translate(product['material'])
    return product

def save_url_image(url,fn):
    data = urllib2.urlopen(url)
    f=open(fn,'wb')
    f.write(data.read())
    f.close()

def ParseNextProductListPage(soup):
    productList = soup.find('div','defaultView').findAll('div','Price')
    print 'Total of %d products in the page' % len(productList)
    products = []
    for product in productList:
        product_url = home_url + product.a['href']
        print product_url
        products.append(ParseNextProductPage(product_url))

def CleanUp(ss):
    ss = ss.replace(',',';')
    ss = ss.replace('\n',' ')
    ss = ss.replace('\r',' ')
    return ss
    
def CleanUpStringForCSV(product):
    product['description'] = CleanUp(product['description'])
    product['title'] = CleanUp(product['title'])
    product['material'] = CleanUp(product['material'])
    ss = []
    for size in product['sizes']:
        ss.append(CleanUp(size))
    product['sizes'] = ss
    
    return product
    
def ParseMamaProductPage(product_url):
    data = urllib2.urlopen(product_url)
    soup = BeautifulSoup (data)
    productID = soup.findAll('span',id = 'itemCode')[0].text.strip()
    breadCrumbs = soup.findAll('div',id = 'Breadcrumbs')[0].text.strip()
    if 'girls' in breadCrumbs.lower():
        sex = 'girl'
    else:
        sex = 'boy'
    department = breadCrumbs.replace('\n','/')
    title = soup.findAll('div',id = 'ProductSummary')[0].h1.text.strip()
    description = soup.findAll('div',id = 'ProductDescriptionBody')[0].text.strip()
    priceString = soup.findAll('strong','itemPrice')[0].text.strip()
    price = float(priceString.split(u'£')[-1])
    priceRange = [price, price]
    sizesSoup = soup.findAll('select',id = 'size')[0]
    sizesString = []
    for sizeSoup in sizesSoup.children:
        if type(sizeSoup) == bs4.element.Tag:
            sizesString.append(sizeSoup.text.strip())
    sizes = sizesString[1:]
    instock = soup.findAll('input', id = 'outofstock')[0]['value'] == 'false'
    instocks = [instock] * len(sizesString)
    prices = [price] * len(sizesString)
    material = u''
    
    img_links = []
    for linkSoup in soup.findAll('li', 'productThumbnails'):
        img_links.append(linkSoup['data-imageurl'])
    pdt = collections.OrderedDict([('productID', productID),\
           ('brand', 'Mamas & Papas'),\
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
    return pdt

def ParseNextProductPage(product_url):
    print '\tLoad the NEXT product page'
    content = phantom_loadpage(product_url)    
    soup = BeautifulSoup (content)
    
    print '\tFind all the image links'    
    data=soup.findAll('div',"ThumbNailNavClip")
    img_links=[]
    for child in data[0].ul.children:
        if type(child) == bs4.element.Tag:
            img_link = child.a['rel'][0]
            img_links.append(img_link)
    
    print '\tParse all the details'''    
    department=soup.findAll('li','Breadcrumb')[2].text.strip()
    if 'girl' in department.lower():
        sex='girl'
    else:
        sex='boy'
    
    products=soup.findAll('article','Style')
    product = products[0]
    productID = product.findAll('div','ItemNumber')[0].text
    title = product.findAll('div','Title')[0].text.strip()
    contents = product.findAll('div','StyleContent')[0]
    description = contents.div.text.strip()
    description = description.replace(',',';')
    material = contents.contents[-2].text.strip()
    material = material.replace(',',';')
    priceStr = product.findAll('div','Price')[0].contents[0]
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
    print '\tTranslation'
    pdt = AddTranslation(pdt)
    print '\tObtain stylewiths'
    stylewiths = []
    if len(products) > 1:
        for product in products[1:]:
            productID = product.findAll('div','ItemNumber')[0].text            
            stylewiths.append(productID)
    pdt['stylewith'] = ';'.join(stylewiths)
    return pdt;

def ExportToDatabase(products, fn):
    f = codecs.open(fn,encoding = 'utf-8', mode = 'w')
    f.write(u'ID,Brand,Department,Sex,Title,Description,Material,Price,Sizes, Prices,Availability,ImageLinks,TitleChinese,DescriptionChinese,MaterialChinese,StyleWith\n')
    ids = []
    for product in products:
        if product['productID'] not in ids:
            ids.append(product['productID'])
            for i, key in enumerate(product.keys()):
                ss = product[key]
                if type(ss) == list:
                    f.write(';'.join(map(str, ss)))
                else:
                    f.write(ss)
                if i < len(product.keys()) - 1:
                    f.write(',')
            f.write('\n')
    f.close()

home_url = 'http://www.next.co.uk'
product_list_url = home_url +'/shop/gender-oldergirls-gender-youngergirls-category-dresses#1'

home_url = 'http://www.mamasandpapas.com'
product_list_url = home_url + '/range/all-girls/10084/'
#data = urllib2.urlopen(product_list_url)

#f = open('temp.html','w')
#f.write(data.read())
#f.close()

f = open('temp.html','r')
data = f.read()
f.close()

soup = BeautifulSoup (data)
#products = ParseNextProductListPage(soup)
products = soup.findAll('div',id = 'rangePageContainer')[0].findAll('div','genericProduct')
pdts = []
for i, product in enumerate(products):
    print i, len(products)
    ss = product.findAll('div','genericProductImages')[0]
    product_url = home_url + ss.a['href']
    pdt = ParseMamaProductPage(product_url)
    pdt = CleanUpStringForCSV(pdt)
    pdt = AddTranslation(pdt)
    pdt['stylewith'] = ''    
    pdts.append(pdt)

ExportToDatabase(pdts, 'c:\\temp\\database.csv')
