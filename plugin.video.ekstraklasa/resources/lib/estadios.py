# -*- coding: utf-8 -*-

import urllib2,urllib,json
import re,os
from urlparse import urlparse
import base64
import cookielib

BASEURL= "http://estadios.pl"
TIMEOUT = 10
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'



def getUrl(url,data=None,cookies=None):

    req = urllib2.Request(url,data)
    req.add_header('User-Agent', UA)
    if cookies:
        req.add_header("Cookie", cookies)
    try:
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        link = response.read()
        response.close()
    except:
        link=''
    return link

def get_liga(url='http://estadios.pl/skroty-meczow'):
    content = getUrl(url)
    divs = re.compile('<div class="przyciski_lig">(.*?)</div>',re.DOTALL).findall(content)
    lgas=[]
    if divs:
        lgas = re.compile('<a href="(.*?)".*title="(.*?)">').findall(divs[0])
    return lgas

url='http://estadios.pl/skroty-meczow,wszystkie'    
def get_skroty_meczow(url):
    content = getUrl(url)
    TRs = re.compile('<tr class="dol_ciemny_tr" itemscope itemtype="http://data-vocabulary.org/Event">(.*?)</tr>',re.DOTALL).findall(content)
    #tr=TRs[0]
    out=[]
    for tr in TRs:
        title = re.compile('<div itemprop="summary" style="font-size: 1px; color: #F5F5F5;">(.*?)</div>(.*?)</td>',re.DOTALL).findall(tr)
        href = re.compile('<a href="(.*?)" title="Zobacz mecz" itemprop="url">(.*?)</a>').findall(tr)
        if title and href:
            when = re.compile('>(.*?)<').search(title[0][1]).group(1) if '<' in title[0][1] else title[0][1].strip()
            t=unicodePLchar('%s [COLOR lightblue]%s[/COLOR]'%(when,title[0][0].strip()))
            u=href[0][0]
            c=href[0][1]
            out.append( {'title':t,'url':u,'code':c} )
    return out

# url='http://estadios.pl/mecz19549,anderlecht-bruksela-gent'
# url='http://estadios.pl/mecz19541,inter-mediolan-palermo'
# url='http://estadios.pl/mecz19570,malta-szkocja'
# url='http://estadios.pl/mecz19677,termalica-bruk-bet-nieciecza-legia-warszawa'
# url=out[4].get('url')
def getVideoLinks(url):
    content = getUrl(url)
    iframe = re.compile('<div class="klip_film">(.*?)</div>',re.DOTALL).findall(content)
    src=''
    if iframe:
        src = re.findall('src="(.*?)"',iframe[0])
        src = src[0] if src else ''
        if 'playwire' in src:
            src = re.findall('data-config="(.*?)"',iframe[0])
            src = src[0] if src else ''
        print src
    return src

def test():
    out = get_skroty_meczow(url)
    for one in out:
        getVideoLinks(one.get('url'))
    
def unicodePLchar(txt):
    txt = txt.replace('#038;','')
    txt = txt.replace('&lt;br/&gt;',' ')
    txt = txt.replace('&#34;','"')
    txt = txt.replace('&#39;','\'').replace('&#039;','\'')
    txt = txt.replace('&#8221;','"')
    txt = txt.replace('&#8222;','"')
    txt = txt.replace('&#8217;','\'')
    txt = txt.replace('&#8211;','-').replace('&ndash;','-')
    txt = txt.replace('&quot;','"').replace('&amp;quot;','"')
    txt = txt.replace('&oacute;','ó').replace('&Oacute;','Ó')
    txt = txt.replace('&amp;oacute;','ó').replace('&amp;Oacute;','Ó')
    #txt = txt.replace('&amp;','&')
    txt = txt.replace('\u0105','ą').replace('\u0104','Ą')
    txt = txt.replace('\u0107','ć').replace('\u0106','Ć')
    txt = txt.replace('\u0119','ę').replace('\u0118','Ę')
    txt = txt.replace('\u0142','ł').replace('\u0141','Ł')
    txt = txt.replace('\u0144','ń').replace('\u0144','Ń')
    txt = txt.replace('\u00f3','ó').replace('\u00d3','Ó')
    txt = txt.replace('\u015b','ś').replace('\u015a','Ś')
    txt = txt.replace('\u017a','ź').replace('\u0179','Ź')
    txt = txt.replace('\u017c','ż').replace('\u017b','Ż')
    return txt
                