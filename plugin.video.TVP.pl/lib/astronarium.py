# -*- coding: utf-8 -*-

import urllib2
import urlparse
import re


TIMEOUT = 10
BASEURL='http://www.astronarium.pl'

def getUrl(url,proxy={},timeout=TIMEOUT):
    if proxy:
        urllib2.install_opener(
            urllib2.build_opener(
                urllib2.ProxyHandler(proxy)
            )
        )
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
    try:
        response = urllib2.urlopen(req,timeout=timeout)
        link = response.read()
        response.close()
    except:
        link='{}'
    return link

# url='http://www.astronarium.pl/odcinki/'
def getEpisodes(url='http://www.astronarium.pl/odcinki/'):
    content=getUrl(url)
    out=[]
    items = re.compile('<a href="(/odcinki.*?)"><img src="(.*?)" alt="(.*?)" class="odcinki-lista"></a>').findall(content)
    for item in items:
        href= BASEURL+item[0]
        img = BASEURL+item[1]
        title = unicodePLchar(item[2].split('"')[0])
        out.append({'title':title,'url':href,'img':img})
    return out
# url='http://www.astronarium.pl/odcinki/?id=26'
def getVideo(url):
    content=getUrl(url)
    link=''
    iframes = re.compile('<iframe (.*?)</iframe>',re.DOTALL).findall(content)
    for frame in iframes:
        src=re.compile('src="(.*?)"').findall(frame)
        src = src[0] if src else ''
        if 'youtube' in src:
            media_id=urlparse.urlparse(src).path.split('/')[-1]
            link = 'plugin://plugin.video.youtube/play/?video_id=' + media_id
    return link
         
def unicodePLchar(txt):
    txt = txt.replace('&nbsp;','')
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