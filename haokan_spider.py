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
class haokan_spider():
     def __init__(self,Executable_path,options,infile,outfile,num):
        self.driver=webdriver.Chrome(options=options,executable_path=Executable_path)
        self.driver.get("https://www.haokan.com/")
        time.sleep(1)
        self.driver.refresh()
        self.cookie = self.driver.get_cookies()
        self.infile=infile
        self.outfile=outfile
        self.num=num
        self.log='./'+infile.split('/')[-1].split('.')[0]+'_log.txt'
        self.urls=[]
        self.headers = {
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
               'cookie': 'BAIDUID=299CB9BD602F22B0730A5281C20D9EC4:FG=1; PC_TAB_LOG=haokan_website_page; Hm_lvt_4aadd610dfd2f5972f1efee2653a2bc5=1591580053; Hm_lpvt_4aadd610dfd2f5972f1efee2653a2bc5=1591580666; reptileData=%7B%22data%22%3A%224cd27d27f185868320f5411f2d4cfe3479b733f92b71a0951d1ace8d6a8b3364d3df57480dd3f8b33797642388fa12b072f17bab14773aa8667aadfddeb45c783a31c4faa4bb5d5f2fb49d9fe0ae5086cbafcd3b1b523a5324f6691406506e3b6a55a235369a74138fd201fb609c6c712379d27e1ce4857e172a4d3d47804c97%22%2C%22key_id%22%3A%2230%22%2C%22sign%22%3A%22b98d33e1%22%7D',
               }
     def get_url(self,home_url):#获取单个页面的所有图片地址
        try:
                r = requests.get(home_url,headers = self.headers,timeout = (5,50))
                r.raise_for_status()
                s = re.compile(r'"hoverURL":"(https://img.*?)"')
                urls = s.findall(r.text)
                scaption = re.findall(r'"fromPageTitle":"(.*?)",', r.text, re.S)
                new_scaption=[]
                for item in scaption:
                        new_scaption.append(item.replace('<strong>','').replace('<\\/strong>',''))
                print(urls)
                
        except:
                pass
        else:#无异常发生
                pic_urls.extend(urls)#添加图片地址
                text_captions.extend(new_scaption)
              
                print(f'请耐心等待,搜索到{len(pic_urls):>4}个图片',end = '\r',flush = True)
     def get_real_url(self,url):
         resp = requests.get(url,headers=self.headers).text
         real_url=re.search(r'https:\\/\\/vd[^&]*mp4',resp)
         real_url=real_url.group()
         real_url =real_url.replace('\\', '')
         #print(real_url)
         return real_url
     def update_log(self,last_task):
           log=open(self.log,'w',encoding='utf-8')
           log.write(last_task)
           print(last_task)
           log.close()
     
     def search_oneTerm(self,line,query_url):
         self.driver.get(query_url)
         count = 0
         attemp=20
         id_={}
         oneTerm=[]
         last=''
         js = "var q=document.documentElement.scrollTop=100000000000"
         while(count<self.num and attemp>0):
             ########### 模拟鼠标向下滑n次（提前拉可以减少重复处理同一链接的次数）
             for i in range(5):
                 self.driver.execute_script(js)
                 time.sleep(0.3)  # 等待页面刷新
             ########### 解析html ############
             html = self.driver.page_source
             soup = BeautifulSoup(html, 'lxml')
             #print('yes')
             if soup.find('div', class_="msg-empty-list"):break#没有结果
             zzr = soup.find_all('a', class_="list-container videolist clearfix")
             if zzr:
                 if(zzr[-1].get("href")==last):
                      if soup.find('p', class_="message-list-footer"):break #没有更多结果
                      else:continue#未加载完
                 last=zzr[-1].get("href")
                 #print(last)
             ########### 获取video_path ############
             flag=True   
             for item in zzr:
                 video = item.get("href")
                 timeBar=item.find('span',class_="list-header-avatar-videotime")#获取时长
                 if timeBar is None:continue
                 if self.less5min(timeBar.string)==False:continue
                 if video is not None and "v?vid=" in video:
                     try:
                         if id_[video]==1:continue
                     except:
                         vid_path=self.get_real_url(video)#获取真正的视频链接
                         oneTerm.append([line,line+str(count),vid_path])
                         #oneTerm.append(video)
                         count=count+1
                         id_[video]=1
                         flag=False
                         #print(vid_path)
                 if count>=self.num: break
             if flag==True:
                 attemp=attemp-1
         '''#多进程获取真实链接
         pool=multiprocessing.Pool(10)
         result_list=[]
         for url in oneTerm:
            result_list.append(pool.apply_async(self.get_real_url(url)))
         pool.close()
         pool.join()
          
         for res in result_list:
             print(res.get())'''
         return oneTerm
      
     def run(self):
         outfile=open(self.outfile,"a",encoding='utf-8',newline = "")
         writer = csv.writer(outfile)
         cnt=0
         with open(self.infile, 'r', encoding='utf-8') as f:
               lines = f.readlines()
               if os.path.exists(self.log):#从上次中断处（附近）开始
                    log=open(self.log,'r',encoding='utf-8')
                    last_task=log.readline().strip()
                    log.close()
                    flag=True
                    for line in lines:
                       line=line.strip("\n").split("\t")[1]
                       if flag and line==last_task:
                           flag=False
                           continue
                       elif flag:continue
                       cnt+=1
                        
                       if line is None: continue
                       url = 'https://haokan.baidu.com/web/search/page?query='+line
                       oneterm=self.search_oneTerm(line,url)
                       writer.writerows(oneterm)
                       if cnt==5:
                           outfile.close()
                           outfile=open(self.outfile,"a",encoding='utf-8',newline = "")
                           writer = csv.writer(outfile)
                           self.update_log(line)
                           cnt=0
               else:
                    writer.writerow(['label','videoname','video_path'])#第一次运行，添加表头
                    for line in lines:
                        cnt+=1
                        line=line.strip("\n").split("\t")[1]
                        if line is None: continue
                        url = 'https://haokan.baidu.com/web/search/page?query='+line
                        oneterm=self.search_oneTerm(line,url)
                        writer.writerows(oneterm)
                        if cnt==5:
                             outfile.close()
                             outfile=open(self.outfile,"a",encoding='utf-8',newline = "")
                             writer = csv.writer(outfile)
                             self.update_log(line)
                             cnt=0
                        
         outfile.close()
 
 

if __name__=='__main__':
   infile="D:/haokan/howto100m_all1.txt"
   outfile="D:/haokan/output.csv"
   spider1=haokan_spider(Executable_path,options,infile,outfile,50)
   spider1.run()
   
     

      
             
         
                         
                         
