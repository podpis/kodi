# -*- coding: utf-8 -*-

import urllib2
import re


TIMEOUT=10

def getUrl(url,data=None,cookies=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36')
    #req.add_header('Host', 'www.playernaut.com')
    #req.add_header('Upgrade-Insecure-Requests', '1')
    if cookies:
        req.add_header("Cookie", cookies)
    try:
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        link =  response.read()
        response.close()
    except:
        link=''

    return link

# url='http://www.posiedze.pl/wideo/aFIuLmiX83'
url = 'http://e.posiedze.pl/aFIuLmiX83'
def _getstuff(content,Cookie):
    src=[]
    quality_options = re.compile('["\']file["\']\s*:\s*["\'](.*?)["\']').findall(content)
    for quality in  quality_options:
        link = quality[0].replace('\\','')
        hd = quality[1].split('"')[0]
        src.append((hd,link+Cookie))
    return src

def getVideoUrls(url):
    """    
    returns 
        - ulr http://....
        - or list of [('720p', 'http://...'),...]
    """        
    #print url
    Cookie='|Cookie="PHPSESSID=1'
    if '/embed/' in url:
        url=url.replace('/embed/','/?v=')
    content = getUrl(url)
    src = _getstuff(content,Cookie)
    if not src:
        script = re.compile('<script>(.*?)</script>',re.DOTALL).findall(content)
        # len(script)
        src=[]
        for s in script:
            if s.find("ﾟωﾟﾉ=")>-1:
                aa=aadecode.AADecoder(s)
                content = aa.decode()
                src = _getstuff(content,Cookie)
                break
    return src    
    