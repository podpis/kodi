# -*- coding: utf-8 -*-

"""
Created on Fri May 29 22:10:54 2015

@author: Michal
"""

import urllib2
import json 
import re
from time import localtime, strftime

TIMEOUT = 10

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
    
def getProxies():
    content=getUrl('http://www.idcloak.com/proxylist/free-proxy-list-poland.html')
    speed = re.compile('<div style="width:\d+%" title="(\d+)%"></div>').findall(content)
    trs = re.compile('<td>(http[s]*)</td><td>(\d+)</td><td>(.*?)</td>',re.DOTALL).findall(content)
    # if len(speed) == len(trs):
    #    speed = [int(x) for x in speed] 
    #    trs = [x for (y,x) in sorted(zip(speed,trs),reverse=True)]
    proxies=[{x[0]: '%s:%s'%(x[2],x[1])} for x in trs]
    return proxies
    
#parent_id=25746022
def vodTVP_getApiQuery(parent_id,count=10):
    listing_url = 'http://www.api.v3.tvp.pl/shared/listing.php?dump=json'
    url = listing_url + '&direct=true&count=%d&parent_id=%s'% (count,parent_id)
    response = urllib2.urlopen(url)
    js = json.loads(response.read())
    response.close()
    return js

def _getPlayable(episode):
    E={}
    E['filename'] = str(episode.get('_id',''))
    if 'video/mp4' in (episode.get('videoFormatMimes') or []):
        E['filename'] = E['filename']+'&mime_type=video/mp4'
    E['fanart'] = vodTVP_getImage(episode,'image_16x9')
    E['img'] = vodTVP_getImage(episode,'image')
    E['tvshowtitle'] =  episode.get('website_title','').encode('utf-8')
    E['title'] =  episode.get('website_title','').encode('utf-8') +', ' +episode.get('title','').encode('utf-8')
    E['plot'] =  episode.get('description_root','').encode('utf-8')
    E['aired'] =  episode.get('publication_start_dt','').encode('utf-8')
    release_date = episode.get('release_date','')
    release_date_sec = release_date.get('sec','') if release_date else ''
    if release_date_sec:
        E['date'] =  strftime("%d.%m.%Y", localtime(release_date_sec))
    else:
        E['date']= '?'
    return E

channel_id='26221210&mime_type=video/mp4'
VIDEO_LINK='http://www.tvp.pl/pub/stat/videofileinfo?video_id='
TOKENIZER_URL = 'http://www.tvp.pl/shared/cdn/tokenizer_v2.php?object_id='

def vodTVP_GetStreamTokenizer(channel_id,proxy={},timeout=TIMEOUT):
    video_url=''
    # videofileinfo = urllib2.urlopen( TOKENIZER_URL+ channel_id)
    # js = json.loads(videofileinfo.read())
    # videofileinfo.close()
    js = json.loads(getUrl(TOKENIZER_URL+ channel_id,proxy,timeout))
    if js.has_key('formats'):
        formats = js.get('formats')
        if isinstance(formats,list):
            video_url=[]
            for one in formats:
                if 'application/vnd.ms-ss' in one.get('mimeType',''):
                    continue
                totalBitrate =  one.get('totalBitrate','')/100
                quality = 'SD'
                if    2000 < totalBitrate <= 5000  : quality = 'SD'
                elif  5000 < totalBitrate <= 10000 : quality = '720p'
                elif 10000 < totalBitrate <= 20000 : quality = '1080p'
                elif 20000 < totalBitrate <= 30000 : quality = '2K'
                elif totalBitrate >= 30000 : quality = '4K'
                
                label = 'Bitrate %d Type:'%totalBitrate + one.get('mimeType','').split('/')[-1] 
                print label
                video_url.append({'title':label,'url':one.get('url',''),'bitrate':totalBitrate})
            video_url = sorted(video_url, key=lambda k: k['bitrate']) 
        else:
            video_url = formats.get('url','')
        # mimeTypes = [x.get('mimeType','') for x in formats] if isinstance(formats,list) else formats.get('mimeType','')
        # # Get m3u source:
        # if 'application/x-mpegurl' in mimeTypes:
        #     one = js.get('formats')[mimeTypes.index('application/x-mpegurl')]
        #     return one.get('url','')
        # elif isinstance(formats,list):
        #     for one in formats:
        #         if 'video/mp4' in one.get('mimeType','') and one.has_key('url'):
        #             return one.get('url')
        # else:
        #     return formats.get('url') 
    return video_url
        
def vodTVP_GetStreamUrl(channel_id,proxy={},timeout=TIMEOUT):
    # videofileinfo = urllib2.urlopen( VIDEO_LINK+ channel_id)
    # js = json.loads(videofileinfo.read())
    # videofileinfo.close()
    video_url = vodTVP_GetStreamTokenizer(channel_id,proxy,timeout)
    if len(video_url)>0:
        return video_url
    js = json.loads(getUrl(VIDEO_LINK+ channel_id,proxy,timeout))
    if js.has_key('video_url'):
        return js.get('video_url')
    else:
        # videofileinfo = urllib2.urlopen(VIDEO_LINK + channel_id.split('&')[0])
        # js = json.loads(videofileinfo.read())
        # videofileinfo.close()
        js = json.loads(getUrl(VIDEO_LINK+ channel_id.split('&')[0],proxy,timeout))
        if js.has_key('copy_of_object_id'):
            channel_id = js.get('copy_of_object_id') + '&mime_type'+ js.get('mime_type','video/mp4')
            video_url = vodTVP_GetStreamTokenizer(channel_id,proxy,timeout)
            return video_url
        elif js.has_key('video_url'):
            return js.get('video_url')
    return ''

def vodTVP_getImage(item,key):
    urlImage = 'http://s.v3.tvp.pl/images/%s/%s/%s/uid_%s_width_%d_gs_0.jpg'
    iconUrl=''
    if key in item:
        iconFile = item[key][0]['file_name']
        iconWidth = item[key][0]['width']
        iconUrl = urlImage %(iconFile[0],iconFile[1],iconFile[2],iconFile[:-4],iconWidth)
    return iconUrl

def vodTVP_root(parent_id='1785454'):
    #l1=vodTVPapi(parent_id,20)
    ROOT=[{'id': 1649941, 'img': '', 'title': 'Seriale'},
          {'id': 1627183, 'img': '', 'title': 'Filmy Fabularne'},
          {'id': 4190012, 'img': '', 'title': 'Dokumenty'},
          {'id': 4190017, 'img': '', 'title': 'Archiwa'},
          {'id': 4934948, 'img': '', 'title': 'Audycje / Programy'},
        ]
    return ROOT


def vodTVPapi(parent_id=22672029,Count=150):
    js=vodTVP_getApiQuery(parent_id,Count)
    items = js.pop('items')
    lista_pozycji = []
    lista_katalogow = []
    if js.get('found_any'):
        for item in items:
            if len(item.get('videoFormatMimes',[])):
                playable=_getPlayable(item)
                if playable.get('filename',''):
                    lista_pozycji.append(playable)
            else:
                img= vodTVP_getImage(item,'image_4x3')      
                title= item.get('title','').encode('utf-8')
                _id=item.get('_id','')
                if item['url'].startswith('http'):
                    lista_katalogow.append({'img':img,'title':title,'id':_id})
    if len(lista_katalogow)==1 and lista_katalogow[0].get('title')=='wideo':
        (lista_katalogow,lista_pozycji) = vodTVPapi(lista_katalogow[0].get('id'),Count)
    return (lista_katalogow,lista_pozycji)
# a=vodTVPapi(882)
# a=vodTVPapi(22672029)
# a=vodTVPapi(26221226)
#a=vodTVPapi()
# Rozrywka
# a=vodTVPapi(22672029) 
# Latajacy klub dwojki
# a=vodTVPapi(24413489)
# vodTVP_GetStreamUrl(a[1][0]['filename'])
# channel_id=a[1][1]['filename']
