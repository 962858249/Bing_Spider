#! /usr/bin/env python3

# coding: utf-8
 
########### load packages ############
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import csv
import lxml
import requests
import re
import multiprocessing
from multiprocessing import Lock
import time
import os
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
#key caption url
class baidu_image_spider():
    def __init__(self,outfile='./out.csv'):
        self.driver=webdriver.Chrome(options=options,executable_path=Executable_path)
        self.driver.get("https://image.baidu.com/")
        time.sleep(1)
        self.driver.refresh()
        self.cookie = self.driver.get_cookies()
        #self.infile=infile
        self.outfile=outfile
    def search_oneTerm(self,keyword):
         page=0
         query_url = 'http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word='+ keyword +'&pn='+str(page)
         self.driver.get(query_url)
         html = self.driver.page_source
         soup = BeautifulSoup(html, 'lxml')
         nxt=True if soup.find('a',class_='n',string='下一页') else False
         #print()
         img_items=soup.find_all('li',class_='imgitem')
         img_list=[]
         caption_list=[]
         for img in img_items:
             img_list.append(img.find('img').get('src'))
             caption_list.append(img.find('div',class_='hover').get('title').replace('<strong>','').replace('</strong>',''))
         while(nxt):
             page+=20
             query_url = 'http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word='+ keyword +'&pn='+str(page)
             self.driver.get(query_url)
             html = self.driver.page_source
             soup = BeautifulSoup(html, 'lxml')
             nxt=True if soup.find('a',class_='n',string='下一页') else False
             img_items=soup.find_all('li',class_='imgitem')
             for img in img_items:
                img_list.append(img.find('img').get('src'))
                caption_list.append(img.find('div',class_='hover').get('title').replace('<strong>','').replace('</strong>',''))
         #print(caption_list)
         #print(img_list)
         return img_list,caption_list
    def search_all(self,key_list):
        if not os.path.exists(self.outfile):
            fout=open(self.outfile,"a",encoding='utf-8',newline = "")
            writer = csv.writer(fout)
            writer.writerow(['keyword','url','caption'])
        else:
            fout=open(self.outfile,"a",encoding='utf-8',newline = "")
            writer = csv.writer(fout)
        for key in key_list:
            print(key)
            urls,captions=self.search_oneTerm(key)
            for i in range(len(urls)):
                 writer.writerow([key,urls[i],captions[i]])


if __name__=='__main__':
    keywords_path = './aic_all_zh.txt' #'THUOCL_food_8974.txt'
    keywords=[]
    with open(keywords_path,"r",encoding='utf-8') as f:
       for line in f.readlines():
          try:
             line = line.strip('\n').split('\t')[1].replace("/"," ")
          except:
             print(line)
             continue
          keywords.append(line)

               
         
    s=baidu_image_spider('./out1.csv')
    s2=baidu_image_spider('./out2.csv')
    l=len(keywords)
    s.search_all(keywords[:l//2])
    s2.search_all(keywords[l//2:])
    
        
