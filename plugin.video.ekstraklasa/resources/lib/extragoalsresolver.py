# -*- coding: utf-8 -*-

import urllib2
import re

TIMEOUT=10
UA = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'


def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', UA)
    try:
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        cookies = response.headers['set-cookie']
        print 'set-cookie',url,cookies
        link = response.read()
        response.close()
    except:
        link=''
    return link


# url='//extragoals.com/video/embed/cc5e8ddd92'
# url='//extragoals.com/video/embed/e696ccfd4a'

def getVideoUrls(url):
    if url.startswith('//'):
        url = 'https:'+url
    src=''
    BRAMKA = 'http://www.bramka.proxy.net.pl/index.php?q='
    content = getUrl(BRAMKA+url)
    srcs = re.compile('src=["\'](//cdn.streamable.com/video/mp4/.+?)["\']',re.DOTALL).findall(content)
    if srcs:
       src=srcs[0] 
       if src.startswith('//'):
           src = 'http:'+src
    return src    
    