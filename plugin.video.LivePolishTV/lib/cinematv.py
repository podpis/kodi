# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import time
import mydecode
import urlparse

BASEURL='http://cinema-tv.xyz/'
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

fix={}


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
    valid_group=['ogolne','filmowe','sportowe','naukowe','informacje','bajki','muzyczne']
    groups=re.compile('<a href="(http://cinema-tv.xyz/.*?/.*?)/">(.*?)</a></li>').findall(content)
    for href,title in groups:
        group = href.split('/')[3] if len(href.split('/'))>4 else ''
        if group in valid_group:
            t = title
            i = ''
            h = href.replace(' ','%20')
            out.append(fixForEPG({'title':t,'tvid':t,'img':i,'url':h,'group':group,'urlepg':''}))
    if addheader and len(out):
        t='[COLOR yellow]Updated: %s (cinema-tv)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.insert(0,{'title':t,'tvid':'','img':'','url':BASEURL,'group':'','urlepg':''})
      
    return out
# url='http://cinema-tv.xyz/ogolne/tvp1hd'
# url='http://cinema-tv.xyz/naukowe/discovery-channel/'
# url='http://cinema-tv.xyz/ogolne/tvnhd/'
# url='http://cinema-tv.xyz/filmowe/kinopolska/'
# url='http://cinema-tv.xyz/filmowe/axnhd/'
# url='http://cinema-tv.xyz/naukowe/animalplanet/'
def decode_url(url='http://cinema-tv.xyz/muzyczne/polotv/'):
    vido_url=''
    if 'cinema-tv' in url:
        content = getUrl(url)
        idx1=content.find('<div class="entry-content clearfix">')
        idx2=content.find('<div class="NavHead">')
        if idx1>-1:
            data=content[idx1:idx2]
        else:
            data=content
        iframes = re.compile('<iframe(.*?)</iframe>').findall(data)
        if iframes:
            pageUrl = re.compile('src="(.*?)"').findall(iframes[0])
            if pageUrl:
                pageUrl=pageUrl[0].replace(' ','%20')
                data=getUrl(pageUrl)
                vido_url = new_decode(pageUrl,data)
                if vido_url=='':
                    vido_url = mydecode.decode(pageUrl,data)

        elif 'src' in content:
            vido_url = mydecode.decode(url,data) 

    return vido_url  



def new_decode(pageUrl,data):
    jwplayer = re.compile('<script type="text/javascript" src="(http.*?jwplayer.*?)"></script>').findall(data)
    jwplayer = [x for x in jwplayer if 'livecounter' not in x]
    vido_url=''
    host=''
    if jwplayer:
        host = urlparse.urlparse(jwplayer[0]).netloc
    
    swfUrl={'dotstream.tv':'http://dotstream.tv/jwp/jwplayer.flash.swf',
            'privatestream.tv':'http://privatestream.tv/js/jwplayer.flash.swf',
            'p.jwpcdn.com':'http://p.jwpcdn.com/6/12/jwplayer.flash.swf',
            'api.peer5.com':'http://api.peer5.com/jwplayer6/assets/flashls.provider.swf'
            }
    
    if re.search('a = ([0-9]+)',data):
        a=int(re.search('a = ([0-9]+)',data).group(1))
        b=int(re.search('b = ([0-9]+)',data).group(1))
        c=int(re.search('c = ([0-9]+)',data).group(1))
        d=int(re.search('d = ([0-9]+)',data).group(1))
        f=int(re.search('f = ([0-9]+)',data).group(1))
        v_part = re.search('v_part = \'(.*?)\';',data).group(1)
        link = 'rtmp://%d.%d.%d.%d/'%(a/f,b/f,c/f,d/f) + v_part.split('/')[1]+'/'+' playpath='+v_part.split('/')[-1]
    
        vido_url = link + ' swfUrl='+swfUrl.get(host,'http://dotstream.tv/jwp/jwplayer.flash.swf') + ' swfVfy=1 live=1 timeout=13 pageUrl='+pageUrl
    return vido_url



def test(out):
    o=out[0]
    for o in out:
        url=o['url']
        print url
        content = getUrl(url)
        idx=content.find('<div class="entry-content clearfix">')
        if idx>-1:
            print 'YES','\t',o['url'],#data=content[idx:]
        else:
            print 'NO','\t',o['url']
##
def go():
    out = get_root()
    o=out[1]
    for o in out:
        print o['url']
        decode_url( o['url']) 
        print '\n'