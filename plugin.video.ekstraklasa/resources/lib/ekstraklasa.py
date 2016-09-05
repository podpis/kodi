# -*- coding: utf-8 -*-

import urllib2,urllib,json
import re,os
from urlparse import urlparse
import base64
import cookielib

BASEURL= "https://api.dailymotion.com"
TIMEOUT = 10
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'

GATE='http://invisiblesurf.review/index.php?q='

def getUrl(url,data=None,cookies=None):
    if GATE:
        url = GATE+base64.b64encode(url)+'&hl=ed'
        print url
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

# user='Ekstraklasa'
# fields='id,uri,duration,record_status,duration_formatted,title,onair,private,views_total,created_time,thumbnail_240_url'


def getLive(user):
    url = BASEURL+"/user/"+user+"/videos?flags=live_onair&fields="+urllib.quote('id,duration,title,onair,private,thumbnail_240_url')
    content = getUrl(url)
    L=[]
    if content:
        data = json.loads(content)
        L = data.get('list',[])
        for l in L:
            print l
    return L
    
def getVideos(user,sort='recent',page='1'):  #visited
    print 'user,sort,page'
    print user,sort,page
    fields='id,uri,duration,record_status,duration_formatted,title,onair,private,views_total,created_time,thumbnail_240_url'
    query = {  'fields':fields,
               'page':page,
               'thumbnail_ratio':'widescreen',
               'sort':sort,
               'limit':50,
               'localization':'pl_PL'
            }
    nextPage=False
    prevPage=False
    L=[]
    
    if sort =='live':
        L = getLive(user)

    else:
        url = BASEURL+"/user/"+user+"/videos?"+urllib.urlencode(query)
        content = getUrl(url)
        data = json.loads(content)
        L = data.get('list',[])
        nextPage = {'user':user,'sort':sort,'page':data.get('page',page)+1} if data.get('has_more',False) else False
        prevPage = {'user':user,'sort':sort,'page':data.get('page',page)-1} if data.get('page',page)>1 else False

        
    return (L,(prevPage,nextPage))

# media_id='x4nrxj6'x2yclwl
def getVideoLinks(media_id='x2yclwl'):
    content = getUrl('http://www.dailymotion.com/embed/video/%s' % media_id)
    srcs=re.compile('"(1080|720|480|380)":\[{"type":"(.*?)","url":"(.*?)"}\]',re.DOTALL).findall(content)
    #srcs=re.compile('"(auto)":\[{"type":"(.*?)","url":"(.*?)"}\]',re.DOTALL).findall(content)
    out=[]
    for quality,type,url in srcs:
        out.append({'label':quality,'url':url.replace('\\','')}) 
    if not out:
        srcs=re.compile('"(auto)":\[{"type":"(.*?)","url":"(.*?)"}\]',re.DOTALL).findall(content)
        for quality,type,url in srcs:
            m3u = getUrl(url.replace('\\','')+ '&redirect=0')
            if '#EXTM3U' in m3u:
                qq=re.compile('NAME="(.*?)"\n(.*?)\n').findall(m3u)
                for label,url in qq:
                    out.append({'label':label,'url':url})    
            else:
                out.append({'label':'auto','url':m3u}) 
    return out
    
# def getVideoLinks(media_id='x2yclwl'):
#     content = getUrl('http://www.dailymotion.com/embed/video/%s' % media_id)
#     html = re.search('({"context".+?)\);\n', content, re.DOTALL)
#     out=[]
#     if html:
#         html = json.loads(html.group(1))
#         if 'metadata' in html: html = html['metadata']
#         if 'qualities' in html:
#             html = html['qualities']
#             print html
#             for k in ['1080','720','480','380']:
#                 if html.has_key(k):
#                    out.append({'label':k,'url':html[k][0].get('url','')}) 
#             if not out and html.has_key('auto'):
#                 k='auto'
#                 m3u = getUrl(html.get('auto',[{}])[0].get('url','')+ '&redirect=0')
#                 out.append({'label':'auto','url':m3u}) 
#     return out