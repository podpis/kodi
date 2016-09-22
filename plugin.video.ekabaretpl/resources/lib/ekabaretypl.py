# -*- coding: utf-8 -*-

import sys,os,re
import urllib,urllib2
import urlparse
import json

UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36'
BASEURL='http://www.ekabaret.pl/'
TIMEOUT=10

def getUrl(url,data=None,cookies=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', UA)

    try:
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        link = response.read()
        response.close()
    except:
        link=''
    return link

# url='http://www.ekabaret.pl/polecane-2.html'
# url='http://www.ekabaret.pl/wideo.html'
# data='szukaj=trudne+zadania'
def get_Skecze(url='http://www.ekabaret.pl/toplista.html',data=None):
    content = getUrl(url,data)

    ids = [(a.start(), a.end()) for a in re.finditer('<div class="ico_video">', content)]
    ids.append( (-1,-1) )
    out=[]
    i=0
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        
        href_title = re.compile('<div style="margin-top: 15px;"><a href="(.*?)" title="(.*?)">').findall(subset)
        img = re.compile('transparent url\(\'(.*?)\'\)').findall(subset)
        if href_title :
            title = href_title[0][1].strip()
            href = urlparse.urljoin(BASEURL,href_title[0][0])
            one = {'url'   : href,
                'title'  : unicodePLchar(title),
                'img'    : img[0] if img else '',
                    }
            out.append(one)
    
    prevPage=re.compile('<a href="([^"]*)">&lt;&lt;&lt; poprzednia</a>').findall(content)
    prevPage = urlparse.urljoin(BASEURL,prevPage[0]) if prevPage else False
    nextPage=re.compile('<a href="([^"]*)">następna &gt;&gt;&gt; </a>').findall(content)
    nextPage = urlparse.urljoin(BASEURL,nextPage[0]) if nextPage else False
    return out,(prevPage,nextPage)

url='http://www.ekabaret.pl/kabarety.html'
url='http://www.ekabaret.pl/kategorie.html'
def get_Katergorie(url,data=None):
    content = getUrl(url,data)
    ids = [(a.start(), a.end()) for a in re.finditer('<div class="box">', content)]
    ids.append( (-1,-1) )
    out=[]
    i=0
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        
        href_title = re.compile('<b><a href="(.*?)" title="(.*?)">').findall(subset)
        img = re.compile('transparent url\(\'(.*?)\'\)').findall(subset)
        plot = re.compile('<div style="font-size: 12px; line-height: 17px;">(.*?)<',re.DOTALL).findall(subset)
        info = re.compile('<div class="inboxKATinfo"(.*?)</div>',re.DOTALL).findall(subset)
        Nskeczy=''
        for tmp in info:
            if 'Skeczy video:' in tmp:
                Nskeczy = re.compile('<b>(\d+)</b>').findall(tmp)
                break

        if href_title :
            title = href_title[0][1].strip()
            id = re.search('(\d+)-',href_title[0][0])
            if id:
                href = 'http://www.ekabaret.pl/wideokat-%s.html'%id.group(1)
            else:
                href = urlparse.urljoin(BASEURL,href_title[0][0])
            
            title += ' (%s)'%Nskeczy[0] if Nskeczy else ''
            one = {'url'   : href,
                'title'  : unicodePLchar(title),
                'plot'  : unicodePLchar(plot[0].strip()) if plot else '',
                'img'    : urlparse.urljoin(BASEURL,img[0]) if img else '',
                    }
            out.append(one)
    
    prevPage=re.compile('<a href="([^"]*)">&lt;&lt;&lt; poprzednia</a>').findall(content)
    prevPage = urlparse.urljoin(BASEURL,prevPage[0]) if prevPage else False
    nextPage=re.compile('<a href="([^"]*)">następna &gt;&gt;&gt; </a>').findall(content)
    nextPage = urlparse.urljoin(BASEURL,nextPage[0]) if nextPage else False
    return out,(prevPage,nextPage)
    
# url='http://www.ekabaret.pl/tv-7264.html'
def getVideoUrl(url):
    content = getUrl(url)
    video_url=''
    iframes = re.compile('<iframe(.*?)</iframe>',re.DOTALL).findall(content)
    for iframe in iframes:
        #iframe = iframes[0]
        src = re.compile('src=[\'"](.*?)[\'"]').findall(iframe)
        if src:
            video_url=src[0].strip()
            break
    return video_url
    
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