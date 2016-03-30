# -*- coding: utf-8 -*-

import urllib2
import re

TIMEOUT=10

def getUrl(url,data=None,cookies=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36')
    if cookies:
        req.add_header("Cookie", cookies)
    try:
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        link =  response.read()
        response.close()
    except:
        link=''
    return link

def getVideoUrls(url):
    """    
    returns 
        - ulr http://....
        - or list of [('720p', 'http://...'),...]
    """        
    #print url
    Cookie='|Cookie="PHPSESSID=1'
    content = getUrl(url)
    src=[]
    quality_options = re.compile('<source src="(.*?)" type="(.*?)" data-res="(.*?)">').findall(content)
    for quality in  quality_options:
        link = quality[0]
        hd = quality[2].split('"')[0]
        src.append((hd,link+Cookie))  
    return src    
    
