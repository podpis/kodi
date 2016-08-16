# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 18:47:43 2016

@author: ramic
"""

import urllib2
import re

import jsunpack as jsunpack

BASEURL='http://www.cda.pl'
TIMEOUT = 5


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


##  JSONUNPACK

#        result = getUrl(url)
#        result = re.compile('(eval.*?)\n').findall(result)[-1]
#        result = unpack(result)

def _get_encoded_unpaker(content):
    src =''
    #packed = re.compile('(eval.function.*?\)\))\n',re.DOTALL).findall(content)
    packedMulti = re.compile("eval(.*?)\{\}\)\)",re.DOTALL).findall(content)
    for packed in packedMulti:
        packed=re.sub('  ',' ',packed)
        packed=re.sub('\n','',packed)
        try:
            unpacked = jsunpack.unpack(packed)
        except:
            unpacked=''
        if unpacked:
            unpacked=re.sub(r'\\',r'',unpacked)
            src1 = re.compile('file:\s*[\'"](.+?)[\'"],',  re.DOTALL).search(unpacked)
            src2 = re.compile('url:\s*[\'"](.+?)[\'"],',  re.DOTALL).search(unpacked)
            if src1:
                src = src1.group(1)
            elif src2:
                src = src2.group(1)
            if src:
                break
    return src

# url='http://www.cda.pl/video/49982323?wersja=720p'
# content = getUrl(url)

def scanforVideoLink(content):
    """
    Scans for video link included encoded one
    """
    video_link=''
    src1 = re.compile('file: [\'"](.+?)[\'"],',  re.DOTALL).search(content)
    src2 = re.compile('url: [\'"](.+?)[\'"],',  re.DOTALL).search(content)
    if src1:
        print 'found RE [file:]'
        video_link = src1.group(1)
    elif src2:
        print 'found RE [url:]'
        video_link = src2.group(1)
    else:
        print 'encoded : unpacker'
        video_link = _get_encoded_unpaker(content)

    return video_link


  
def getVideoUrls(url):
    """
    returns 
        - ulr http://....
        - or list of [('720p', 'http://www.cda.pl/video/1946991f?wersja=720p'),...]
         
    """  
    # check if version is selecte
    playerSWF1='|Cookie="PHPSESSID=1&Referer=http://static.cda.pl/player5.9/player.swf'
    playerSWF='|Referer=http://static.cda.pl/player5.9/player.swf'
    print url
    content = getUrl(url)
    src=[]
    if not '?wersja' in url:
         quality_options = re.compile('<a data-quality="(.*?)" (?P<H>.*?)>(?P<Q>.*?)</a>', re.DOTALL).findall(content)
         for quality in quality_options:
             link = re.search('href="(.*?)"',quality[1])
             hd = quality[2]
             src.insert(0,(hd,BASEURL+link.group(1)))
    if not src:     # no qualities availabe ... get whaterer is there
        src = scanforVideoLink(content)
        if src:
            src+=playerSWF1

    return src    


def getVideoUrlsQuality(url,quality=0):
    """
    returns url to video
    """
    src = getVideoUrls(url)
    if type(src)==list:
        selected=src[quality]
        print 'Quality :',selected[0]
        src = getVideoUrls(selected[1])
    return src
    
