# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import time
import mydecode

BASEURL='http://telewizja-live.com/'

fix={
'Tvp1':'TVP 1',
 'Tvp2':'TVP 2',
 'Tvphd':'TVP HD',
 'Tvn':'TVN',
 'Tvn24':'TVN24',
 'Axn':'AXN',
 'Hbo2':'HBO2',
 'Para':'Para',
 'Filmbox':'Filmbox',
 'Comedycenter':'Comedy Center',
 'Animalplanet':'Animal Planet',
 'Canaldiscovery':'Discovery Canal',
 'Discoveryturbo':'Discovery turbo',
 'History':'History',
 'H2':'H2',
 'Natgeowild':'Natgeowild',
 'Tvnstyle':'Tvn Style',
 'Tlc':'TLC',
 'Eurosport':'Eurosport',
 'Elevensports':'Eleven sports',
 'Polsatsport':'Polsat sport'}

def fixForEPG(one):
    newName = fix.get(one.get('tvid'),'')
    if newName:
        one['title']=newName
        one['tvid']=newName
    return one
    
def getUrl(url,data=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
    try:
        response = urllib2.urlopen(req, timeout=10)
        link = response.read()
        response.close()
    except:
        link=''
    return link
    
def get_root(addheader=False):
    out=[]
    urls=['http://telewizja-live.com/ogolne.html']
    urls=['http://telewizja-live.com/ogolne.html','http://telewizja-live.com/informacyjne.html',
            'http://telewizja-live.com/filmowe.html','http://telewizja-live.com/naukowe.html',
            'http://telewizja-live.com/sportowe.html','http://telewizja-live.com/bajkowe.html']
    orange=['Tvn7',
    'Tvpuls',
    'Tv4',
    'Polsat',
    'Tvn24Biz',
    'Tvpinfo',
    'Trwam',
    'Canal',
    'Canalfamily',
    'Hbo',
    'Hbo3',
    'Fox',
    'Discovery',
    'Natgeo',
    'Tvnturbo',
    'Canalsport',
    'Canalsport2',
    'Nsport',
    'Eurosport2',
    'Tvpsport',
    'Eleven',
    'Polsatsport2',
    'Polsatsport3']
    
    for url in urls:
        content = getUrl(url)
        
        code=url[:-5].split('/')[-1]
        items = re.compile('<a href="(.*?)" class="link"><img src="(.*?)"').findall(content)

        #one=match[0]
        for item in items:
            #print h,t,i
            c = code
            t = item[0].split('.')[0].title()
            i = BASEURL+item[1]
            h = BASEURL+item[0]
            if t in orange:
                print t
                c = '[COLOR orange]'+c+'[/COLOR]'
            out.append(fixForEPG({'title':t,'tvid':t,'img':i,'url':h,'group':'','urlepg':'','code':c}))
        #return sorted(out, key=lambda k: k['title'],reverse=True)    
    
    if addheader and len(out):
        t='[COLOR yellow]Updated: %s (telewizja-live)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.insert(0,{'title':t,'tvid':'','img':'','url':BASEURL,'group':'','urlepg':''})
    return out

def decode_url(url='http://telewizja-live.com/canalsport.html'):
    vido_url=''
    
    content = getUrl(url)
    iframe = re.compile('<iframe(.*?)</iframe>',re.DOTALL).findall(content)
    if iframe:
        pageUrl = re.compile('src="(http.*?)"').findall(iframe[0])
        if pageUrl:
            data = getUrl(pageUrl[0])
            vido_url = mydecode.decode(pageUrl[0],data)
    return vido_url 
    
def test():
    out = get_root(True)
    outg=[]
    for one in out:
        print '\n',one.get('title')
        video=decode_url(one.get('url'))
        if not video:
            outg.append(one.get('title'))
        print video
   
