#! /usr/bin/env python3

# coding: utf-8
 
########### load packages ############
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
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
browser.get('https://cn.bing.com/images/')
cookie =browser.get_cookies()
js = "var q=document.documentElement.scrollTop=100000000000"
def get_info():
    item_list=[]
    html=browser.page_source
    doc=pq(html)
    rows=doc('#mmComponent_images_1')
    row_list=rows.children()
    for raw in row_list:
        raw=pq(raw)
        imgs=raw.children()
        for img in imgs:
            img=pq(img)
            try:
              m=img('.iuscp .imgpt a').attr('m')
              m=eval(m)
              item_list.append((m['murl'],m['t'].replace('','').replace('','')))
            except:
                print(m)
    return item_list

def search_one(keyword,outfile=None):
    keyword=keyword.strip()
    url='https://cn.bing.com/images/search?q='+keyword
    browser.get(url)
    ########### 模拟鼠标向下滑n次（提前拉可以减少重复处理同一链接的次数）
    for i in range(30):
        browser.execute_script(js)
        time.sleep(0.5)  # 等待页面刷新
    time.sleep(1)
    item_list=get_info()
    flag=False
    if os.path.exists(outfile):
        flag=True
    with open(outfile,'a',encoding='utf-8',newline='') as f:
       writer = csv.writer(f)
       if not flag:
           writer.writerow(['keyword','url','caption'])
       for item in item_list:
           writer.writerow([keyword,item[0],item[1]])
           
def search_all(keywords,outfile,start=0):
    for i, key in enumerate(keywords):
        if i<start:continue
        search_one(key,outfile)
        
if __name__=='__main__':
    infile='./taobao.txt'
    outfile='./bing_out.csv'
    start=0
    with open(infile,'r',encoding='utf-8') as f:
        keys=f.readlines()
    search_all(keys,outfile,start)
    browser.close()
