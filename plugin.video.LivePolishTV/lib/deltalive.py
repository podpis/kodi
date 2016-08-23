# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import time
import mydecode


BASEURL='http://delta-live.pro/'
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

def fixForEPG(one):
    return one

def getUrl(url,data=None,header={}):
    if not header:
        header = {'User-Agent':UA}
    req = urllib2.Request(url,data,headers=header)
    try:
        response = urllib2.urlopen(req, timeout=15)
        link = response.read()
        response.close()
    except:
        link=''
    return link
    

def get_root(addheader=False):
    content = getUrl(BASEURL)
    out=[]
    group=''
    submenus = re.compile('<ul class="submenu">(.*?)</ul>',re.DOTALL).findall(content)
    for submenu in submenus:
        channels=re.compile('<li><a href="(.*?)">(.*?)</a></li>').findall(submenu)
        for ch in channels:
            t = ch[1].strip()
            i = ''
            h = BASEURL + ch[0]
            out.append(fixForEPG({'title':t,'tvid':t,'img':i,'url':h,'group':group,'urlepg':''}))
    if addheader and len(out):
        t='[COLOR yellow]Updated: %s (delta-live.pro)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.append({'title':t,'tvid':'','img':'','url':'http://delta-live.pro','group':'','urlepg':''})
      
    return out

# url='http://delta-live.pro/4,pl,tvp1hd.html'
# url='http://delta-live.pro/5,pl,tvp2hd.html'
# url='http://delta-live.pro/7,pl,polsathd.html'
# url='http://delta-live.pro/8,pl,tvnhd.html'
# url='http://delta-live.pro/44,pl,polsat-1.html'
# url='http://delta-live.pro/66,pl,puls.html'
# url='http://delta-live.pro/59,pl,cfamilyhd.html'
def decode_url(url='http://delta-live.pro/28,pl,tvpsporthd.html'):
    vido_url=''
    if 'delta-live' in url:
        content = getUrl(url)
        iframes = re.compile('<iframe(.*?)</iframe>').findall(content)
        if iframes:
            pageUrl = re.compile('src="(.*?)"').findall(iframes[0])
            if pageUrl:
                data=getUrl(pageUrl[0])
                vido_url = mydecode.decode(pageUrl[0],data)
                if 'static.u-pro.fr' in data and not vido_url:
                    source = re.compile('src=["\'](http.*?)["\']').findall(data)
                    if source:
                         source = re.compile('source=(rtmp.*?[^&]*)').findall(source[0])
                         if source:
                             vido_url = source[0]
                print '@@@@@',vido_url

    return vido_url  

def test():
    out = get_root(True)
    outg=[]
    for one in out:
        print '\n',one.get('title')
        video=decode_url(one.get('url'))
        if not video:
            outg.append((one.get('title'),one.get('url')))
        print video
   