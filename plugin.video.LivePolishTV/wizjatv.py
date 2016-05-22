# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import time
import execjs


BASEURL='http://wizja.tv/'
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
    url='http://wizja.tv/'
    content = getUrl(url)
    channels=re.compile('<a href="(watch.*?)"><img src="(.*?)"></a>').findall(content)
    out=[]
    if addheader:
        t='[COLOR yellow]Updated: %s (wizja.tv)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.append({'title':t,'tvid':'','img':'','url':'http://wizja.tv/','group':'','urlepg':''})
    #one=match[0]
    for ch in channels:
        t = ch[1].split('/')[-1].split('.')[0]
        i = BASEURL + ch[1]
        h = BASEURL + ch[0]
        out.append(fixForEPG({'title':t,'tvid':t,'img':i,'url':h,'group':'','urlepg':''}))
    #return sorted(out, key=lambda k: k['title'],reverse=True)    
    return out
    
#rtmp://185.66.141.231:1875/haYequChasp4T3eT?event=37&token=aTL2E0ZGxyPnjVUzkiAlb1WXBQ9rg6<playpath>pHe7repheT?event=37&token=aTL2E0ZGxyPnjVUzkiAlb1WXBQ9rg6 <swfUrl>http://wizja.tv/player/StrobeMediaPlayback_v2.swf <pageUrl>http://wizja.tv/player.php?target=ams_nl1&ch=37


def decode_url(url='http://wizja.tv/watch.php?id=22'):
    vido_url=''
    if 'wizja.tv' in url:
        
        id = re.search('id=(.*?)$',url).group(1)
        playerulr='http://wizja.tv/player.php?target=ams_nl1&ch=%s'%id
        header={'User-Agent':UA,
                'Host':'wizja.tv',
                'Referer':url,
                'Upgrade-Insecure-Requests':'1',
                'Cookie':'PHPSESSID=1'}

        url2='http://wizja.tv/porter.php?ch=%s'%id
        data = getUrl(url,header=header)
        data = getUrl(url2,header=header)
        data = getUrl(playerulr,header=header)
        print data
        iframes = re.compile('<iframe(.*?)</iframe>').findall(data)
        for f in iframes:
            print f,'\n'
        #    vido_url = m[0][1]+' playpath='+m[0][0]+' swfUrl=http://looknij.tv/wp-content/plugins/yendif-player/public/assets/libraries/player.swf?1438149198120 live=1 pageUrl=http://looknij.tv'
    return vido_url

    
##
out = get_root()