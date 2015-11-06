# -*- coding: utf-8 -*-
"""
Created on Thu Nov 05 23:24:27 2015

@author: ramic
"""


import urllib2
import re

def getUrl(url,data=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link
    
def get_root_looknji():
    url='http://looknij.tv/wp-admin/admin-ajax.php'
    params='action=get_portfolio_works&category=all&now_open_works=0&html_template=Grid+columns&works_per_load=51'
    content = getUrl(url,params)
    title=re.findall('<h5>(.*)</h5>',content)
    href=re.findall('<a class="ico_link"  href="(.*)"><span></span></a>',content)
    img=re.findall('<img alt="(.*)" src="(.*);src=(.*)">',content)
    grp=re.findall('<div data-category="(.*) " class="',content)
    out=[]
    for t,h,i,c in zip(title,href,img,grp):
        out.append({'title':t,'img':i[-1],'url':h,'group':c})
    return sorted(out, key=lambda k: k['title'],reverse=True)    

def decode_url(url='http://looknij.tv/?port=eleven'):
    vido_url=''
    if 'looknij.tv' in url:
        urlpl = getUrl(url)
        m = re.compile('<div class="yendifplayer".*?src="([^"]+)".*?data-rtmp="([^"]+)"', re.DOTALL).findall(urlpl)
        if m:
            vido_url = m[0][1]+' playpath='+m[0][0]+' swfUrl=http://looknij.tv/wp-content/plugins/yendif-player/public/assets/libraries/player.swf?1438149198120 pageUrl=http://looknij.tv live=1'
    return vido_url
    
#get_root_looknji()
#decode_url()