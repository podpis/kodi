# -*- coding: utf-8 -*-
"""
Created on Thu Nov 05 23:24:27 2015

@author: ramic
"""


import urllib2
import re
import time

NameFix={
    "TV PULS":"TV Puls",
    "PULS 2":"Puls 2",
    "TeleToon":"Teletoon+",
    "11 Sport":"Eleven Sports",
    "FOX Comedy": "Fox Comedy",
    "DOMO+" :"Domo+ HD",
    "TVP1":"TVP 1",
    "Polsat Cafe":"Polsat Café",
    "FilmBox Action":"Filmbox Action",
    "HBO 2": "HBO2",
    "Ale Kino":"ale kino+",
    "Canal Sport 2":"Canal+ Sport 2",
    "Discovery":"Discovery Channel",
    "National Geographic":"National Geographic Channel",
    }

def fixForEPG(one):
    if one['title'] == "Polsat Viasat Explore":
        if 'explore' in one.get('img'):
            one['tvid'] = "Viasat Explore"
        elif 'history' in one.get('img'):
            one['tvid'] = "Viasat History"
        elif 'nature' in one.get('img'):
            one['tvid'] = "Viasat Nature"
    elif one['title'] in NameFix.keys():
        one['tvid'] =NameFix[one['title']]
    return one


def getUrl(url,data=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link
    
def get_root_looknji(addheader=False):
    url='http://looknij.tv/wp-admin/admin-ajax.php'
    params='action=get_portfolio_works&category=all&now_open_works=0&html_template=Grid+columns&works_per_load=51'
    content = getUrl(url,params)
    title=re.findall('<h5>(.*)</h5>',content)
    href=re.findall('<a class="ico_link"  href="(.*)"><span></span></a>',content)
    img=re.findall('<img alt="(.*)" src="(.*);src=(.*)">',content)
    grp=re.findall('<div data-category="(.*) " class="',content)
    out=[]
    if addheader:
        t='[COLOR yellow]Updated: %s (Looknij)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.append({'title':t,'tvid':'','img':'','url':'http://looknij.tv','group':'','urlepg':''})
    for t,h,i,c in zip(title,href,img,grp):
        out.append(fixForEPG({'title':t,'tvid':t,'img':i[-1],'url':h,'group':c,'urlepg':''}))
    #return sorted(out, key=lambda k: k['title'],reverse=True)    
    return out

def decode_url(url='http://looknij.tv/?port=eleven'):
    vido_url=''
    if 'looknij.tv' in url:
        urlpl = getUrl(url)
        m = re.compile('<div class="yendifplayer".*?src="([^"]+)".*?data-rtmp="([^"]+)"', re.DOTALL).findall(urlpl)
        if m:
            vido_url = m[0][1]+' playpath='+m[0][0]+' swfUrl=http://looknij.tv/wp-content/plugins/yendif-player/public/assets/libraries/player.swf?1438149198120 pageUrl=http://looknij.tv live=1'
    return vido_url

def decode_all_urls(out):
    out_hrefs=[]    
    for one in out:
        print one.get('title')
        vido_url = decode_url(one.get('url',''))
        if vido_url:
            one['url']=vido_url
            out_hrefs.append(one) 
    return out_hrefs

    
#out=get_root_looknji(addheader=True)
#out2=decode_all_urls(out)    
#decode_url()