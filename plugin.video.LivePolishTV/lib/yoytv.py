# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import time
import cookielib

BASEURL='http://yoy.tv/'
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
TIMEOUT = '10'

fix={
'Pa Sat':'Polsat',
'Cinemax2':'Cinemax 2',
'HBO 2 HD':'HBO2 HD',
'Psat Sport News':'Polsat Sport News',
'Extreme Sports':'Extreme Sport',
'Stopklatka':'Stopklatka TV',
#'Szostka':'',
#'Cbs Action':'',
'Cbs Reality':'CBS Reality',
#'Cbs Drama':'',
#'BBC Knowledge':'',
'BBC Earth HD':'BBC Earth',
#'Ci Polsat':'',
'Polsat Food':'Polsat Food Network',
'Fokus TV':'Fokus TV',
'Eska TV':'Eska TV',
'4Fun TV':'4fun TV',
'4Fun Hits':'4fun Hits',
'4Fun Fit&Amp;Dance':'4fun Fit Dance',
'TVP Poloniia':'TVP Polonia',
'TVP Puls 2':'Puls 2',
'TVP Abc':'TVP ABC',
#'Mgm HD':'',
'Romance TV HD':'Romance TV',
'TV4':'TV 4',
#'Euronews En':'',
#'Word Fashion Channel':'',
'Trwam':'TV Trwam',
#'Mango 24':'',
#'BBC HD':'',
#'BBC Word News':'',
'Eurosport  2':'Eurosport 2',
#'I24':'',
#'Cnc Ii':'',
'Nickjr':'Nick Jr',
'Alekino':'ale kino+',
'Canal':'Canal+',
'Canal Sport':'Canal+ Sport',
'Canal Sport 2':'Canal+ Sport 2',
'Canal Discovery':'Canal+ Discovery HD',
'Canal 1':'Canal+ 1',
'Canal Seriale':'Canal+ Seriale',
'Canal Film':'Canal+ Film',
'Nsport':'nSport',
'Canal Family':'Canal+ Family',
'Planete':'Planete+',
'Teletoon':'Teletoon+',
'Minimini':'Minimini+',
'Domo+':'Domo+ HD',
'Style TVN':'TVN Style',
'Active Meteo TVN':'TVN Meteo Active',
'24 TVN BIS':'TVN 24 BIS',
'Turbo TVN':'TVN Turbo',
'24 TVN':'TVN 24',
'7 TVN':'TVN 7',
#'TVT':'',
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


def get_root(live='1',country='140',addheader=False):
    out=[]
    next_page = 1
    while next_page:
        print 'page',next_page
        tmp_out,next_page = get_page(live=live,country=country,page=next_page)
        print 'channels#',len(tmp_out)
        out.extend(tmp_out)
    len(out)
    if len(out)>0 and addheader:
        t='[COLOR yellow]Updated: %s (yoy.tv)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.insert(0,{'title':t,'tvid':'','img':'','url':'http://yoy.tv/','group':'','urlepg':''})
    return out
    
def get_page(live='1',country='140',page=1):
    url = 'http://yoy.tv/channels?live=%s&country=%s&page=%d'%(live,country,page)
    content = getUrl(url)
    out=[]
    lists=re.compile('<li class=".*?">(.*?)</li>',re.DOTALL).findall(content)
    for li in lists:
        group=''
        href = re.search('href="(http://yoy.tv/channels/.*?)"',li)
        src = re.search('src="(.*?)"',li)
        title = re.search('alt="(.*?)"',li)
        transmituje = li.find('>Nie transmituje<')
        if href and title and src:

            t = title.group(1).replace('.','').title()
            for s in ['TV','TVN','MTV','TVP','BIS','TVR','TVS','HBO','BBC','AXN','ATM','AMC','HD','TLC','ID','XD','TVT','CBS']:
                t = re.sub("((?i)"+s+")",s.upper(), t) #,flags=re.IGNORECASE
            if transmituje>0 :
                t +=' [COLOR red]offline[/COLOR]'
            i = src.group(1)
            h = href.group(1)
            out.append(fixForEPG({'title':t,'tvid':t,'img':i,'url':h,'group':group,'urlepg':''}))
    
    # pagination
    url_next = r'http://yoy.tv/channels?live=%s&country=%s&page=%d'%(live,country,page+1)
    idx=content.find(url_next)
    next_page = page+1 if idx>-1 else None
    return out,next_page

#url='http://yoy.tv/channels/793'
#url='http://yoy.tv/channels/3330'
def decode_url(url):
    # cookieJar = cookielib.MozillaCookieJar()
    # rtmp://94.242.228.182/yoy/_definst_<playpath>398 <swfUrl>http://yoy.tv/playerv3a.swf <pageUrl>http://yoy.tv/channels/398
    vido_url=''
    if 'yoy.tv' in url:
        content = getUrl(url)
        flash = re.compile('FlashVars value="(.*?)"').findall(content)
        if flash:
            rtmp = re.search('(rtmp://.*?)\&',flash[0])
            cid = re.search('cid=(.*?)\&',flash[0])
            if rtmp:
                ip1 =map(int,re.compile('/(\d+)\.(\d+)\.(\d+)\.(\d+)/').findall(rtmp.group(1))[0])
                ip2 = '.'.join([str(255-ip1[x]) for x in [3,2,0,1]])
                vido_url = 'rtmp://'+ip2+'/yoy/_definst_/'+cid.group(1).strip() +' swfUrl=http://yoy.tv/playerv3a.swf swfVfy=1 live=1 timeout='+TIMEOUT+' pageUrl='+url
    return vido_url    

##    
# out=get_root(live='1',country='140',addheader=False)
# decode_url(out[0]['url'])
# for o in out:
#     print o.get('title')
# headers={'Referer':'http://yoy.tv/channels/3330',
# 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
# 'X-Requested-With':'XMLHttpRequest'}
# url='http://yoy.tv/freeminutes'
