# -*- coding: utf-8 -*-

import urllib2,urllib,json
import re,os
from urlparse import urlparse
import base64
import cookielib

BASEURL= "http://www.livefootballol.me"
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

def get_video(url='http://www.livefootballol.me/video/'):
    content = getUrl(url)
    divs = re.compile('<h3 class="page-header item-title">(.*?)</h3>',re.DOTALL).findall(content)
    out=[]
    for div in divs:
        #div = divs[0]
        href_title = re.compile('<a href="(.*?)">(.*?)</a>',re.DOTALL).findall(div)
        count = re.compile('title="Article Count:">(.*?)<',re.DOTALL).findall(div)
        if href_title and count:
            h = BASEURL + href_title[0][0]
            t = href_title[0][1].strip() + ' ([COLOR blue]' +count[0].strip() +'[/COLOR])'
            out.append({'url':h,'title':t})
    return out

# url='http://www.livefootballol.me/video/england/'
def get_games(url):
    content = getUrl(url)
    tds = re.compile('<td>(.*?)</td>',re.DOTALL).findall(content)
    out=[]
    nextPage=False
    prevPage=False
    for td in tds:
        #td = tds[0]
        href = re.compile('<a href="(.*?)"',).findall(td)
        title = re.compile('>(.*?)<',re.DOTALL).findall(td)
        if href and title:
            h = BASEURL + href[0]
            t = title[0].strip()
            t = re.sub('(\d+-\d+)','[COLOR blue]\g<1>[/COLOR]',t)
            out.append({'url':h,'title':t})
    if out:
        nextPage = re.compile('<a class="next" href="(.*?)" ').findall(content)
        nextPage = BASEURL + nextPage[0] if nextPage else False
        prevPage = re.compile('<a class="previous" href="(.*?)" ').findall(content)
        prevPage = BASEURL + prevPage[0] if prevPage else False
    return (out,(prevPage,nextPage))   
#items,pagination=get_games(url)

# url='http://www.livefootballol.me/video/england/11-09-2016-aston-villa-nottingham-forest.html'
def getVideoLinks(url):
    content = getUrl(url)
    vl=''
    src = re.compile('data-config="(//.*\.json)"').findall(content)
    if src:
        vl = src[0]
    return vl

def test():
    out,pagination = get_games('http://www.livefootballol.me/video/england/')    
    for one in out:
        vl=getVideoLinks(one.get('url'))
        print vl