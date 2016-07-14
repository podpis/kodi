# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import aes.pyaes as aes

BASEURL='http://sitemtv.rf.gd/'
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
TIMEOUT = 10

def getUrl(url,data=None,header={},cookie=''):
    if not header:
        header = {'User-Agent':UA}
    if cookie:
        header = {'Cookie':cookie} 
    req = urllib2.Request(url,data,headers=header)
    try:
        response = urllib2.urlopen(req, timeout=TIMEOUT)
        link = response.read()
        response.close()
    except urllib2.HTTPError as e:
        link=e.read()
        link=''
    return link      


def get_cookie():
    data = getUrl(BASEURL)
    a= re.compile('a=toNumbers\("(.*?)"\)').findall(data)[0]
    b= re.compile('b=toNumbers\("(.*?)"\)').findall(data)[0]
    c= re.compile('c=toNumbers\("(.*?)"\)').findall(data)[0]
    toN = lambda a: [ int(a[2*i:2*i+2],16) for i in range(len(a)/2)]
    a= toN(a)
    b= toN(b)
    c= toN(c)
    cipher = aes.new(a, 2, b)
    padded_plaintext = cipher.decrypt(c)
    cookie = '__test='+''.join(['%0.2x'%ord(x) for x in padded_plaintext])
    return cookie
    
def get_root(addheader=False):
    content = getUrl(BASEURL,cookie=get_cookie())
    out=[]
    items=re.compile('<a target="soccer" href="(.*?)"[^>]*><[^>]*>(.*?)</button>').findall(content)
    for href,title in items:
        out.append({'title':title,'tvid':title,'img':'','url':href,'group':'','urlepg':''})
    return out

url='http://sitemtv.rf.gd/tvp1.html?src=?token=looknij.in'
def decode_url(url):
    #rtmp://demo.fms.visionip.tv:1935/live<playpath>demo-sub-polsat2-hsslive-25f-16x9-SD <swfUrl>https://www.hlsplayer.net/player/grindplayer/GrindPlayer.swf <pageUrl>http://sitemtv.rf.gd/polsat1.html?src=?token=looknij.in
    vido_url=''
    content = getUrl(url,cookie=get_cookie())
    if content:
        swfUrl = re.compile('"player"data="(.*?)"').findall(content)
        flashvars = re.compile('"flashvars" value="(.*?)"').findall(content)
        if swfUrl and flashvars:
            src = re.compile('src=([^;]*)').findall(flashvars[0])
            if src:
                vido_url = src[0].replace('&amp','') + ' swfUrl='+swfUrl[0] + ' swfVfy=1 live=1 timeout=13  pageUrl='+url

    return vido_url 