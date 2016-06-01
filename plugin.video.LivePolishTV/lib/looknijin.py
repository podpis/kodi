# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import time

BASEURL='http://looknij.in/'
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
TIMEOUT = '10'

fix={
'Canal Film':'Canal+ Film',
'Canal Sport HD':'Canal+ Sport',
'HBOHD':'HBO',
'Minimini HD':'Minimini+',
'Polsat2HD':'Polsat 2',
'NsportHD':"nSport",
'TLC Polska HD':"TLC",
'Discovery Channel Historia':"Discovery Historia",
'TVPHD':'TVP HD',
'Natgeo Wild HD':"Nat Geo Wild",
'TVP2HD':'TVP 2',
'TVP1HD':'TVP 1',
}

def fixForEPG(one):
    newName = fix.get(one.get('tvid'),'')
    if newName:
        one['title']=newName
        one['tvid']=newName
    return one
    

def getUrl(url,data=None,header={},cookies=None):
    if not header:
        header = {'User-Agent':UA}
    req = urllib2.Request(url,data,headers=header)
    try:
        response = urllib2.urlopen(req, timeout=10)
        if cookies=='':
            cookies=response.info()['Set-Cookie']
        link = response.read()
        response.close()
    except:
        link=''
    return link    


def get_root(addheader=False):
    out=[]
    next_page = 1
    while next_page:
        print 'page',next_page
        tmp_out,next_page = get_page(page=next_page)
        print 'channels#',len(tmp_out)
        out.extend(tmp_out)
    len(out)
    if len(out)>0 and addheader:
        t='[COLOR yellow]Updated: %s (yoy.tv)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.insert(0,{'title':t,'tvid':'','img':'','url':'http://yoy.tv/','group':'','urlepg':''})
    return out
    
def get_page(page=1):
    url = 'https://looknij.in/tv-online/strona[%d]+'%(page)
    content = getUrl(url)
    out=[]
    hrefs = re.compile('<h3 class.*?<a href="(.*?)">(.*?)</a>').findall(content)
    imgs = re.compile('<a href="(.*?)"><img src="(.*?)"').findall(content)
    for im,href in zip(imgs,hrefs):
        group=''
        t=href[-1].split('[')[0].strip()
        i=im[-1]
        h=im[0]
        t = t.title()
        for s in ['TV','TVN','MTV','TVP','BIS','TVR','TVS','HBO','BBC','AXN','ATM','AMC','HD','TLC','ID','XD','TVT','CBS']:
            t = re.sub("((?i)"+s+")",s.upper(), t) #,flags=re.IGNORECASE
        out.append(fixForEPG({'title':t,'tvid':t,'img':i,'url':h,'group':group,'urlepg':''}))
    
    # pagination
    url_next = r'https://looknij.in/tv-online/strona[%d]+'%(page+1)
    idx=content.find(url_next)
    next_page = page+1 if idx>-1 else None
    return out,next_page

#url='https://looknij.in//tv-filmbox-extra-lektor-20'
def decode_url(url):
    # cookieJar = cookielib.MozillaCookieJar()
    # rtmp://live.looknij.in/live/<playpath>FILMBOX <swfUrl>https://looknij.in/views/js/jwplayer.flash.swf <pageUrl>https://looknij.in//tv-filmbox-extra-lektor-20
    if 'looknij.in' in url:
        content = getUrl(url)
        swfUrl='https://looknij.in/views/js/jwplayer.flash.swf'
        flash = re.compile('post\([\'"](.*?)["\']').findall(content)
        if flash:
            data = getUrl(BASEURL+flash[0])
            rtmp = re.search('"(rtmp:.*?)"',data)
            if rtmp:
                rtmp = rtmp.group(1).replace('\\','')
                vido_url = rtmp.strip() +' swfUrl='+swfUrl+' swfVfy=1 live=1 timeout='+TIMEOUT+' pageUrl='+url
    return vido_url    

##    
# out=get_root(addheader=False)
# for o in out:
#     print o.get('title')
#     o['url']=decode_url(o.get('url'))
#     print o['url']