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
import pdb


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
    content=open('htmlcode.txt').read()
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
    ss = unicode.join(u'\n',map(unicode,product))    
    f = codecs.open(fn, encoding = 'utf-8', mode = 'w')
    f.write(ss)
    f.close()

       
product_url='http://www.next.co.uk/x57396s1'

content = phantom_loadpage(product_url)
soup = Bea utifulSoup (content)

#find all the images
data=soup.findAll('div',"ThumbNailNavClip")
img_links=[]
for child in data[0].ul.children:
    if type(child)==bs4.element.Tag:
        img_links.append(child.a['rel'][0])

pdts=[]
department=soup.findAll('li','Breadcrumb')[3].text
if 'girl' in department.lower():
    sex='girl'
else:
    sex='boy'
products=soup.findAll('article','Style')    
for product in products:
    ExportSoup(product, 'soup.html')
    
    title = unicode(product.findAll('div','Title')[0].findAll(re.compile('^h'))[0].string)
    description=product.findAll('div','Composition')[0].a['data-description']
    overall_price_str=product.findAll('div','Price')[0].contents[0].string
    if '-' in overall_price_str:
        overall_price=float(overall_price_str[1:overall_price_str.find('-')-1])
    else:
        overall_price=float(overall_price_str[1:])
    dropdowns=product.findAll('select','SizeSelector')[0].findAll('option')
    sizes=[]
    for dropdown in dropdowns[1:]:
        size_str,individual_price=size_string_parser(dropdown.text)
        if individual_price==-1:
            individual_price=overall_price
        sizes.append({'size':size_str,'price':individual_price,'instock':dropdown['class'][0]==u'InStock'})
    try:
        title_chinese = translate(title)
    except ValueError:
        title_chinese = title
    pdts.append({'department':department,'sex':sex,'title':title,'chinese_title':title_chinese,'description':translate(description),'overall_price':overall_price,'sizes':sizes})
