# -*- coding: utf-8 -*-

import sys,os,re
import urllib,urllib2
import urlparse
import cookielib
import json

BASEURL='http://iitv.pl/'

def getUrl(url, cj=None,post=None, headers=None,timeout=20):
    cookie_handler = urllib2.HTTPCookieProcessor(cj)
    opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
    req = urllib2.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
    if headers:
        for h,hv in headers:
            req.add_header(h,hv)

    response = opener.open(req,post,timeout=timeout)
    link=response.read()
    response.close()
    return link;


def getSeriale(page=1):
    page=int(page)
    url='http://iitv.pl/ajax/getCellsList/%d?init=false'%int(page)
    out=[]
    nextPage=False
    prevPage=False
    headers=[['Accept','application/json, text/plain, */*'],
            ['Connection','keep-alive'],
            ['X-Requested-With','XMLHttpRequest'],
            ['Referer','http://iitv.pl/']]
    cj=cookielib.LWPCookieJar()            
    content  = getUrl(url,cj,headers=headers)
    if content:
        data=json.loads(content)
        for k,v in data['results'].iteritems():
            one={}
            one['title'] = '%s %s'%(v.get('seasonAndEpisodeCode',''),v.get('seriesTitle'))
            one['plot']=v.get('description','')
            one['img']=v.get('imageUrl','')
            one['url']=v.get('url','')
            one['data']=v.get('date','')
            one['code']=v.get('flag','')
            one['urlSeries']=v.get('theSeriesUrl','')
            out.append(one)
    
    nextPage=int(page)+1 if len(out) else False
    prevPage = page-1 if page>1 else False
    return (out,(prevPage,nextPage))
     

def getPopular():
    content  = getUrl(BASEURL)
    ul = re.compile('<ul id="popular-list">(.*?)</ul>',re.DOTALL).findall(content)
    out=[]
    for u in ul:
        ps=re.compile('<a href="(http:.*?)">([^<]+)<').findall(u)
        for u,t in ps:
            out.append({'title':unicodePLchar(t) ,'url':u})
    return out
    
def getList():
    content  = getUrl(BASEURL)
    ul = re.compile('<ul id="list">(.*?)</ul>',re.DOTALL).findall(content)
    out=[]
    for u in ul:
        ps=re.compile('<a href="(http:.*?)">([^<]+)<').findall(u)
        for u,t in ps:
            out.append({'title':unicodePLchar(t) ,'url':u})
    return out

#url='http://iitv.pl/100-code'
def getEpisodes(url):
    content  = getUrl(url)
    out=[]
    el = re.compile('<div class="episodes-list">(.*?)</div>',re.DOTALL).findall(content)
    if el:
        for li in re.compile('<li>(.*?)</li>',re.DOTALL).findall(el[0]):
            date = re.compile('class="column date">(.*?)<').search(li)
            epis = re.compile('episode-code">(.*?)<').search(li)
            href = re.compile('href="(http.*?)"[^>]*>(.*?)<').search(li)
            if href:
                code = date.group(1) if date else '' 
                title = epis.group(1) if date else ''
                title += ' '+href.group(2) if date else ''
                out.append({'title':unicodePLchar(title) ,'url':href.group(1),'code':code})
    return out

#url='http://iitv.pl/arrow/s04e04-beyond-redemption'
def getLinks(url):
    content  = getUrl(url)
    ul = re.compile('<ul class="tab-content"(.*?)</ul>',re.DOTALL).findall(content)
    out=[]
    for u in ul:
        lang = re.compile('id="(.*?)"').search(u)
        lang = lang.group(1) if lang else ''
        lang = lang.replace('org','[COLOR grey]ORYGINAŁ[/COLOR]')
        lang = lang.replace('lecPL','[COLOR green]Lektor[/COLOR]')
        lang = lang.replace('subPL','[COLOR orange]Napisy[/COLOR]')
        links = re.compile('<a class="video-link" href="(.*?)" data-link-id=".*?">(.*?)</a>').findall(u)
        for l in links:
            out.append({'title': '[%s] %s'%(lang,l[-1]),'url':l[0]})
    return out
 
#url='http://iitv.pl/arrow/s04e04-beyond-redemption?link=221'
def getHostUrl(url):
    content  = getUrl(url)
    src=''
    iframes = re.compile('<iframe(.*?)</iframe>',re.DOTALL).findall(content)
    for frame in iframes:
        src = re.compile('src=["\'](.*?)["\']').search(frame)
        src = src.group(1) if src else ''
    return src
 
def unicodePLchar(txt):
    txt = txt.replace('#038;','')
    txt = txt.replace('&nbsp;','')
    txt = txt.replace('&lt;br/&gt;',' ')
    txt = txt.replace('&#34;','"')
    txt = txt.replace('&#39;','\'').replace('&#039;','\'')
    txt = txt.replace('&#8221;','"')
    txt = txt.replace('&#8222;','"')
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
    

