# -*- coding: utf-8 -*-
"""
Created on Thu Nov 05 23:24:27 2015

@author: ramic
"""

from requests import Session
import urllib2
import re

def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

def get_root_looknji():
    session = Session()

    # HEAD requests ask for *just* the headers, which is all you need to grab the
    # session cookie
    session.head('http://looknij.tv/?page_id=11')
    
    response = session.post(
        url='http://looknij.tv/wp-admin/admin-ajax.php',
        data={
                'html_template':'Grid columns',
            'now_open_works':'0',
            'action':'get_portfolio_works',
            'works_per_load':'51',
            'category':'all'
        },
        headers={
            'Access-Control-Allow-Origin':'http://looknij.tv'
        }
    )
    
    content=response.text

    title=re.findall('<h5>(.*)</h5>',content)
    href=re.findall('<a class="ico_link"  href="(.*)"><span></span></a>',content)
    img=re.findall('<img alt="(.*)" src="(.*);src=(.*)">',content)
    out=[]
    for t,h,i in zip(title,href,img):
        out.append({'title':t,'img':i[-1],'url':h})
    return sorted(out, key=lambda k: k['title'],reverse=True)        

def parse(sHtmlContent, sPattern, iMinFoundValue = 1, ignoreCase = False):
        if ignoreCase:
            aMatches = re.compile(sPattern, re.DOTALL|re.I).findall(sHtmlContent)
        else:
            aMatches = re.compile(sPattern, re.DOTALL).findall(sHtmlContent)
        if (len(aMatches) >= iMinFoundValue):                
            return True, aMatches
        return False, aMatches

def decode_url(url='http://looknij.tv/?port=eleven'):
    vido_url=''
    if 'looknij.tv' in url:
        urlpl = getUrl(url)
        pattern = '<div class="yendifplayer".*?src="([^"]+)".*?data-rtmp="([^"]+)"'
        rResult = parse(urlpl, pattern)
        xResult = rResult[1][0]
        vido_url = xResult[1]+' playpath='+xResult[0]+' swfUrl=http://looknij.tv/wp-content/plugins/yendif-player/public/assets/libraries/player.swf?1438149198120 pageUrl=http://looknij.tv live=1'
    return vido_url
    
#get_root_looknji()