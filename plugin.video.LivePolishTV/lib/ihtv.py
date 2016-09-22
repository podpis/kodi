# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import time
import mydecode


BASEURL='http://i-hqtv.com/'
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

    groups=re.compile('<li id="menu-item-.*?" class=".*?"><a href="(.*?)">(.*?)</a></li>').findall(content)
    for href,title in groups:
        #href,title =groups[0]

        out.append(fixForEPG({'title':title.strip(),'tvid':title.strip(),'img':'','url':href,'group':'','urlepg':''}))
    if out and addheader:
        t='[COLOR yellow]Updated: %s (i-htv.net)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.append({'title':t,'tvid':'','img':'','url':'http://wizja.tv/','group':'','urlepg':''})
              
    return out

url='http://i-hqtv.com/tvn-7/'
def decode_url(url='http://i-hqtv.com/discovery-channel/'):
    vido_url=''
    content = getUrl(url)
    iframes = re.compile('<iframe(.*?)</iframe>').findall(content)
    if iframes:
        pageUrl = re.compile('src="(.*?)"',re.IGNORECASE).findall(iframes[0])
        if pageUrl:
            data=getUrl(pageUrl[0])
            vido_url = mydecode.decode(pageUrl[0],data)
            print '@@@@@',vido_url

    return vido_url    
    
##

def test():
    out = get_root()
    #one=out[-4]
    for one in out:
        url=one.get('url')
        print url
        link=decode_url(url)
        print link,'\n'
    