# -*- coding: utf-8 -*-

import urllib2,urllib,json
import re,os
from urlparse import urlparse


BASEURL= "https://iptvlinkss.blogspot.be/"
TIMEOUT = 10
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'

#https://iptvlinkss.blogspot.be/feeds/posts/summary?alt=json-in-script&max-results=9

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
    
def get_root():
    content = getUrl('https://iptvlinkss.blogspot.be/feeds/posts/summary?alt=json-in-script&callback=pageNavi&max-results=20')
    data=json.loads(re.search('\((.*?)\);',content).group(1))
    entry = data.get('feed',{}).get('entry',[])
    out=[]
    for one in entry:
        #one=entry[0]
        if 'iptv links' in one.get('category',[{}])[0].get('term',''):
            img = one.get('media$thumbnail',{}).get('url','')
            titleFull = one.get('title',{}).get('$t','')
            title = titleFull.split('Links')[0].strip()
            code = one.get('updated',{}).get('$t','').split('T')[0].strip()
            if code:
                title = '[COLOR lightblue]%s[/COLOR] %s'%(code,title)
            for l in one.get('link',[]):
                if 'text/html' in l.get('type',''):
                    url = l.get('href','')
            if url and img and title:
                out.append({'title':title,'img':img.replace('/s72-c/','/s300/'),'url':url,'code':code})
    return out
                
def get_root_web():
    content = getUrl(BASEURL)
    out=[]
    articles = re.compile('<article class=["\']post hentry["\']>(.*?)</article>',re.DOTALL).findall(content)
    for article in articles:
        #article=articles[0]
        href_title = re.search('<a href=["\'](.*?)["\'] title=["\'](.*?)["\']>',article)
        img = re.search('<a href=["\'](.*?jpg)["\'] imageanchor=["\']1["\']',article)
        if href_title and img:
            one={'title':href_title.group(2),'img':img.group(1),'url':href_title.group(1)}
            out.append(one)
    return out

def m3u2list(url):
    m3u_content = getUrl(url)
    out = []
    matches=re.compile('^#EXTINF:-?[0-9]*(.*?),(.*?)\n(.*?)$',re.I+re.M+re.U+re.S).findall(m3u_content)
   
    renTags={'tvg-id':'tvid',
             'audio-track':'audio-track',
             'group-title':'group',
             'tvg-logo':'img'}
                 
    for params, title, url in matches:
        one  = {"title": title, "url": url.split('<')[0]}
        match_params =re.compile(' (.+?)="(.*?)"',re.I+re.M+re.U+re.S).findall(params)
        for field, value in match_params:
            one[renTags.get(field.strip().lower(),'bad')] = value.strip()
        if not one.get('tvid'):
            one['tvid']=title
       
        one['urlepg']=''
        one['url']=one['url'].strip()
        one['title']=one['title'].strip()
        out.append(one)
    return out
    
      
def test():
    out = get_root()
    
