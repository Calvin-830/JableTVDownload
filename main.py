# author: hcjohn463
#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import os
import re
import urllib.request
import m3u8
from Crypto.Cipher import AES
from config import headers
from crawler import prepareCrawl
from merge import mergeMp4
from delete import deleteM3u8, deleteMp4
from cover import get_cover
import time
import cloudscraper
from args import *
# In[2]:

parser = get_parser()
args = parser.parse_args()

if(len(args.url) != 0):
    url = args.url
elif(args.random == True):
    url = av_recommand()
else:
    # 使用者輸入Jable網址
    url = input('輸入jable網址:')

# In[3]:


# 建立番號資料夾
urlSplit = url.split('/')
dirName = urlSplit[-2]
if not os.path.exists(dirName):
    os.makedirs(dirName)
folderPath = os.path.join(os.getcwd(), dirName)
# In[4]:


# 得到 m3u8 網址
htmlfile = cloudscraper.create_scraper(browser='chrome', delay=10).get(url)
result = re.search("https://.+m3u8", htmlfile.text)
m3u8url = result[0]

m3u8urlList = m3u8url.split('/')
m3u8urlList.pop(-1)
downloadurl = '/'.join(m3u8urlList)


# 儲存 m3u8 file 至資料夾

m3u8file = os.path.join(folderPath, dirName + '.m3u8')
opener = urllib.request.build_opener()
opener.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'), ('Referer', 'https://jable.tv')]
urllib.request.install_opener(opener)
urllib.request.urlretrieve(m3u8url, m3u8file)
# In[5]:


# 得到 m3u8 file裡的 URI和 IV
m3u8obj = m3u8.load(m3u8file)
m3u8uri = ''
m3u8iv = ''
for key in m3u8obj.keys:
    if key:
        m3u8uri = key.uri
        m3u8iv = key.iv

# 儲存 ts網址 in tsList
tsList = []
for seg in m3u8obj.segments:
    tsUrl = downloadurl + '/' + seg.uri
    tsList.append(tsUrl)


# In[6]:

# 有加密
if m3u8uri:
    m3u8keyurl = downloadurl + '/' + m3u8uri  # 得到 key 的網址

    # 得到 key的內容
    response = requests.get(m3u8keyurl, headers=headers, timeout=10)
    contentKey = response.content
    print(contentKey)
    vt = m3u8iv.replace("0x", "")[:16].encode()  # IV取前16位

    ci = AES.new(contentKey, AES.MODE_CBC, vt)  # 建構解碼器
else:
    ci = ''


# In[7]:


# 刪除m3u8 file
deleteM3u8(folderPath)


# In[8]:


# 開始爬蟲並下載mp4片段至資料夾
prepareCrawl(ci, folderPath, tsList)


# In[9]:


# 合成mp4
mergeMp4(folderPath, tsList)


# In[10]:


# 刪除子mp4
deleteMp4(folderPath)

# In[11]:
# get cover
get_cover(html_file=htmlfile, folder_path=folderPath)
