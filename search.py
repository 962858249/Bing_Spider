#! /usr/bin/env python3
# author: Qi Shao
111
########### load packages ############
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import csv
import lxml
########check duration 10min####
def smaller7min(time):
    l=len(time)
    total=0
    tmp=0
    for i in range(l):
        if time[i]<='9' and time[i]>='0':
            if i==0: tmp=int(time[0])
            else:
                if time[i-1]>='0' and time[i-1]<='9':
                    tmp=10*tmp+int(time[i])
                else:
                    tmp=int(time[i])
        elif time[i-1]<='9' and time[i-1]>='0':
            total=total*60+tmp
    return total<=420
####################################################
########### 无窗口打开Chrome浏览器 ############
options = Options()
options.add_argument('--no-sandbox')#解决DevToolsActivePort文件不存在的报错
options.add_argument('window-size=1920x3000') #指定浏览器分辨率
options.add_argument('--disable-gpu') #谷歌文档提到需要加上这个属性来规避bug
options.add_argument('--hide-scrollbars') #隐藏滚动条, 应对一些特殊页面
options.add_argument('blink-settings=imagesEnabled=false') #不加载图片, 提升速度
#options.add_argument('--headless') #浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
#options.binary_location = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" #手动指定使用的浏览器位置
driver=webdriver.Chrome(options=options,executable_path="C:\\Users\\17914\\Downloads\\chromedriver_win32\\chromedriver.exe")



#driver = webdriver.Chrome(executable_path="D:\\pythonprojet\\youtube\\youtube\\chromedriver.exe")
driver.get("https://www.youtube.com/")


########### 窗口最大化 ############
driver.maximize_window()
time.sleep(1)
driver.refresh()


########### 获取cookie ############
cookie = driver.get_cookies()
###########打开输出文件############
'''label,videoname,video_id'''
output="C:\\Users\\17914\\Downloads\\YouTube全链条视频获取\\YouTube全链条视频获取\\results1.csv"
outfile=open(output,"a",encoding='utf-8',newline = "")
writer = csv.writer(outfile)
#writer.writerow(['label','videoname','video_id'])


########### 查询query ############
inputtxt = "C:\\Users\\17914\\Downloads\\YouTube全链条视频获取\\YouTube全链条视频获取\\THUOCL_food_8974.txt"
#inputtxt = "D:\\Pycharm\\pycharmprojets\\youtube1\\input.txt"
with open(inputtxt, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        oneTerm=[]
        line=line.strip("\n").split("\t")[0]
        if line is None: continue
        query =line+" 食用"
        print(query)
        ########### 查询query，限制video时长在6分钟以内 ############
        url = 'https://www.youtube.com/results?search_query=' + query #+ '&sp=EgQQARgB'
        driver.get(url)

        def execute_times(num):
            count = 0
            attemp=20
            id={}
            while(count<num and attemp>0):
                ########### 解析html ############
                html = driver.page_source
                soup = BeautifulSoup(html, 'lxml')
                zzr = soup.find_all('a', id="thumbnail")

                ########### 获取video_id ############
                flag=True
                for item in zzr:
                    video = item.get("href")
                    timeBar=item.find('span',class_="style-scope ytd-thumbnail-overlay-time-status-renderer")
                    if timeBar is None:continue
                    duration=timeBar.get("aria-label")
                    if smaller7min(duration)==False:continue
                    if video is not None and "/watch?v=" in video:
                       video_id = video.replace('/watch?v=', '')
                       try:
                           if id[video_id]==1:continue
                       except:
                            oneTerm.append([line,line+str(count),video_id])
                            count=count+1
                            id[video_id]=1
                            flag=False
                    if count>=num: break
                if flag==True:
                    attemp=attemp-1
                ########### 模拟鼠标向下滑动 ############
                js = "var q=document.documentElement.scrollTop=100000000000"
                driver.execute_script(js)
                time.sleep(0.9)  # 等待页面刷新

        ###########  ############
        execute_times(50)
        writer.writerows(oneTerm)
outfile.close()
########### 退出Chrome ############
driver.quit()
