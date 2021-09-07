#! /usr/bin/env python3

# coding: utf-8
 
########### load packages ############
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#import time
#from bs4 import BeautifulSoup
import csv
#import lxml
#import requests
#import re
import os
from pyquery import PyQuery as pq
########### Chrome浏览器驱动设置 ############
options = Options()
options.add_argument('--no-sandbox')#解决DevToolsActivePort文件不存在的报错
options.add_argument('window-size=1920x3000') #指定浏览器分辨率
options.add_argument('--disable-gpu') #谷歌文档提到需要加上这个属性来规避bug
options.add_argument('--hide-scrollbars') #隐藏滚动条, 应对一些特殊页面
#options.add_argument('blink-settings=imagesEnabled=false') #不加载图片, 提升速度
#options.add_argument('--headless') #浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
#options.binary_location = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" #手动指定使用的浏览器位置
Executable_path="C:\\Users\\17914\\Downloads\\chromedriver_win32\\chromedriver.exe"
browser=webdriver.Chrome(options=options,executable_path=Executable_path)
browser.get('https://www.jd.com/?cu=true')
cookie =browser.get_cookies()
def get_products():
    #wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-itemlist.items.item')))#加载宝贝信息并等待
    html=browser.page_source
    doc=pq(html)
    items=doc('#J_goodsList .gl-item').items()
    item_list=[]
    for item in items:
        detail=item.find('.p-name a em').text()
        detail=detail.replace('\n','，')
        pic_url=item.find('.p-img a img').attr('src')
        if pic_url==None:
            pic_url=item.find('.p-img a img').attr('data-lazy-img')
        product=(pic_url,detail)#商品描述
        item_list.append(product)
    return item_list
    
def search_oneTerm(keyword,outfile):
    keyword=keyword.strip()
    page_num=100
    print(keyword)
    flag=False
    if os.path.exists(outfile):
        flag=True
    with open(outfile,'a',encoding='utf-8',newline='') as f:
       writer = csv.writer(f)
       if not flag:
           writer.writerow(['keyword','url','caption'])
       for i in range(page_num):
          url='https://search.jd.com/Search?keyword='+keyword+'&page='+str(2*i+1)
          try:
              browser.get(url)
              item_list=get_products()
          except:
              browser.get(url)
              item_list=get_products()
          for item in item_list:
              writer.writerow([keyword,item[0],item[1]])
def search_all(keywords,outfile,start=0):
    for i, key in enumerate(keywords):
        if i<start:continue
        search_oneTerm(key,outfile)
if __name__=='__main__':
    infile='./taobao.txt'
    outfile='./taobao_out.csv'
    start=0
    with open(infile,'r',encoding='utf-8') as f:
        keys=f.readlines()
    search_all(keys,outfile,start)
        
    
