# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import time
import execjs
import mydecode


BASEURL='http://i-htv.net/'
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

fix={
"tvp1":"TVP 1",
"tvp2":"TVP 2",
"tvphd":"TVP HD",
"tvn":"TVN",
"tvn7":"TVN 7",
"tvpuls":"TV PLUS",
"tvn24":"TVN 24",
"tvpinfo":"TVP Info",
"tvrepublika":"TV Republika",
"canal":"Canal+",
"canalfilm":"Canal+ Film",
"canalfamily":"Canal+ Family",
"axn":"AXN",
"hbo":"HBO",
"hbo2":"HBO2",
"hbo3":"HBO 3",
"fox":"Fox",
"kino-polska":"Kino Polska",
"canalsport2":"Canal+ Sport 2",
"canalsport":"Canal+ Sport",
"nsport":"Nsport",
"eurosport":"Eurosport",
"eurosport2":"Eurosport 2",
"tvpsport":"TVP Sport",
"eleven":"Eleven",
"elevensport":"Eleven Sports",
"animalplanet":"Animal Planet",
"discovery":"Discovery Channel",
"discoveryhistoria":"Discovery Historia",
"history":"History",
"h2 ":"History 2",
"natgeo":"National Geographic Channel",
"natgeowild":"Nat Geo Wild",
"tvnturbo":"TVN Turbo",
"tvnstyle":"TVN Style",
"tlc":"TLC",
"eskatv":"Eska TV",
"mtv":"MTV Polska",}

def fixForEPG(one):
    newName = fix.get(one.get('tvid'),'')
    if newName:
        one['title']=newName
        one['tvid']=newName
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
    groups=re.compile('<li><a href="(.*?)">(.*?)</a></li>').findall(content)
    for href,group in groups:
        #print href
        # url='http://i-htv.net/ogolne.html'
        # url='http://i-htv.net/informacyjne.html'
        # url='http://i-htv.net/filmowe.html'
        #url='http://i-htv.net/sportowe.html'
        #url='http://i-htv.net/muzczyne.html'
        content = getUrl(BASEURL+href)
        channels=re.compile('<a href="(.*?)" class="link"><img src="(.*?)"').findall(content)
        
        if addheader:
            t='[COLOR yellow]Updated: %s (i-htv.net)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
            out.append({'title':t,'tvid':'','img':'','url':'http://wizja.tv/','group':'','urlepg':''})
        #one=match[0]
        for ch in channels:
            t = ch[1].split('/')[-1].split('.')[0]
            i = BASEURL + ch[1]
            h = BASEURL + ch[0]
            out.append(fixForEPG({'title':t,'tvid':t,'img':i,'url':h,'group':group,'urlepg':''}))
      
    return out

   
def decode_url(url='http://i-htv.net/tvp1.html'):
    vido_url=''
    if 'i-htv.net' in url:
        content = getUrl(url)
        iframes = re.compile('<iframe(.*?)</iframe>').findall(content)
        if iframes:
            pageUrl = re.compile('src="(.*?)"').findall(iframes[0])
            if pageUrl:
                data=getUrl(pageUrl[0])
                vido_url = mydecode.decode(pageUrl[0],data)
                print '@@@@@',vido_url
               
        # header={'User-Agent':UA,
        #         'Host':'wizja.tv',
        #         'Referer':url,
        #         'Upgrade-Insecure-Requests':'1',
        #         'Cookie':'PHPSESSID=1'}
    return vido_url    
    
##
# reload(mydecode)
##
# out=get_root()
# 
# for o in out:
#     # print 'url="%s"'%o.get('url')
#     print '"%s"'%o.get('title')
#
# url=out[0].get('url')
# 
# url="http://i-htv.net/tvp1.html"
# url="http://i-htv.net/tvp2.html"
# url="http://i-htv.net/tvphd.html"
# url="http://i-htv.net/tvn.html"
# url="http://i-htv.net/tvn7.html"
# url="http://i-htv.net/tvpuls.html"
# url="http://i-htv.net/tvn24.html"
# url="http://i-htv.net/tvpinfo.html"
# url="http://i-htv.net/tvrepublika.html"
# url="http://i-htv.net/canal.html"
# url="http://i-htv.net/canalfilm.html"
# url="http://i-htv.net/canalfamily.html"
# url="http://i-htv.net/axn.html"
# url="http://i-htv.net/hbo.html"
# url="http://i-htv.net/hbo2.html"
# url="http://i-htv.net/hbo3.html"
# url="http://i-htv.net/fox.html"
# url="http://i-htv.net/kinopolska.html"
# url="http://i-htv.net/canalsport.html"
# url="http://i-htv.net/canalsport2.html"
# url="http://i-htv.net/nsport.html"
# url="http://i-htv.net/eurosport.html"
# url="http://i-htv.net/eurosport2.html"
# url="http://i-htv.net/tvpsport.html"
# url="http://i-htv.net/eleven.html"
# url="http://i-htv.net/elevensport.html"
# url="http://i-htv.net/animalplanet.html"
# url="http://i-htv.net/discovery.html"
# url="http://i-htv.net/discoveryhistoria.html"
# url="http://i-htv.net/history.html"
# url="http://i-htv.net/h2.html"
# url="http://i-htv.net/natgeo.html"
# url="http://i-htv.net/natgeowild.html"
# url="http://i-htv.net/tvnturbo.html"
# url="http://i-htv.net/tvnstyle.html"
# url="http://i-htv.net/tlc.html"
# url="http://i-htv.net/eskatv.html"
# url="http://i-htv.net/mtv.html"

# link=decode_url(url)
# print link