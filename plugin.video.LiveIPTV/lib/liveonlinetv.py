# -*- coding: utf-8 -*-

import urllib2,urllib,json
import re,os
from urlparse import urlparse
import mydecode

BASEURL= "http://www.liveonlinetv247.info"
TIMEOUT = 10
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'


def getUrl(url,data=None,cookies=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', UA)
    if cookies:
        req.add_header("Cookie", cookies)
    try:
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        link = response.read()
        response.close()
    except:
        link=''
    return link
    
    
def get_root():
    content = getUrl(BASEURL+'/tvchannels.php')
    out=[]
    channels = re.compile('<td><a href="(.*?)"><img src="(.*?)" width="100" height="100" border="0"><br>(.*?)</a></td>').findall(content)
    for href,img,title in channels:
        one={'title':title,'img':img,'url':BASEURL+href}
        out.append(one)
    return out


    
url='http://www.liveonlinetv247.info/foxnews.php'
url='http://www.liveonlinetv247.info/skynews.php'
url='http://www.liveonlinetv247.info/sabtv.php'
def decode_url(url):    
    content = getUrl(url)
    iframes = re.compile('<iframe(.*?)</iframe>',re.DOTALL).findall(content)
    if iframes:
        pageUrl = re.compile('src=["\'](.*?)["\']').findall(iframes[0])
        if pageUrl:
            data = getUrl(pageUrl[0])
            link1 = re.compile('<source type="application/x-mpegurl" src="(.*?)"').findall(data)
            if link1:
                print link1[0]
            else:
                srcs=re.compile('src=["\'](http:.*?)["\']').findall(data)
                srcs=re.compile('src=["\'](http://www.liveonlinetv247.info.*?)["\']',re.I).findall(data)
                for src in srcs:
                    if 'externalurl' in src:
                        link2=src[src.find('externalurl')+12:]
                        print link2
                        break
                    elif 'embed' in src:
                        print src
                        data = getUrl(src)
                        break
                        
            #vido_url = mydecode.decode(pageUrl[0],data)
def test():
    out=get_root()
    for one in out[:10]:
        url=one.get('url')
        print url
        decode_url(url)
        print '\n\n'