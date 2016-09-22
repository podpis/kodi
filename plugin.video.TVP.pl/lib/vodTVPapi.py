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

#episode=item
def _getPlayable(episode):
    E={}
    E['filename'] = str(episode.get('_id',''))
    if 'video/mp4' in (episode.get('videoFormatMimes') or []):
        E['filename'] = E['filename']+'&mime_type=video/mp4'
    E['fanart'] = vodTVP_getImage(episode,['image_16x9','image'])
    E['img'] = vodTVP_getImage(episode,['image'])
    E['tvshowtitle'] =''
    if episode.get('website_title',None):
        E['tvshowtitle'] =  episode.get('website_title','').encode('utf-8')
    E['title']=''
    if episode.get('website_title',None):
        E['title'] =  episode.get('website_title','').encode('utf-8') + ', ' 
    E['title'] += episode.get('title','').encode('utf-8')
    E['plot'] =  episode.get('description_root','').encode('utf-8')
    E['aired'] =  episode.get('publication_start_dt','').encode('utf-8')
    release_date = episode.get('release_date','')
    release_date_sec = release_date.get('sec','') if release_date else ''
    E['duration'] = episode.get('duration','')
    if release_date_sec:
        E['date'] =  strftime("%d.%m.%Y", localtime(release_date_sec))
    else:
        E['date']= '?'
    return E

channel_id='26754935&mime_type=video/mp4'
VIDEO_LINK='http://www.tvp.pl/pub/stat/videofileinfo?video_id='
TOKENIZER_URL = 'http://www.tvp.pl/shared/cdn/tokenizer_v2.php?object_id='
BRAMKA='http://www.bramka.proxy.net.pl/index.php?q='

def vodTVP_GetStreamTokenizer(channel_id='26754935',proxy={},timeout=TIMEOUT,bramka=False):
    video_url=''
    # videofileinfo = urllib2.urlopen( TOKENIZER_URL+ channel_id)
    # js = json.loads(videofileinfo.read())
    # videofileinfo.close()
    BP = BRAMKA if bramka else ''
    js = json.loads(getUrl(BP+TOKENIZER_URL+ channel_id,proxy,timeout))
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
        
def vodTVP_GetStreamUrl(channel_id='26403971',proxy={},timeout=TIMEOUT,bramka=False):
    # videofileinfo = urllib2.urlopen(VIDEO_LINK+ channel_id)
    # js = json.loads(videofileinfo.read())
    # videofileinfo.close()
    video_url = vodTVP_GetStreamTokenizer(channel_id,proxy,timeout,bramka)
    if len(video_url)>0:
        return video_url
    js = json.loads(getUrl(VIDEO_LINK+ channel_id,proxy,timeout))
    if js.has_key('video_url'):
        return js.get('video_url')
    else:
        # videofileinfo = urllib2.urlopen(VIDEO_LINK + channel_id.split('&')[0])
        # js = json.loads(videofileinfo.read())
        # videofileinfo.close()
        BP = BRAMKA if bramka else ''
        js = json.loads(getUrl(BP+VIDEO_LINK+ channel_id.split('&')[0],proxy,timeout))
        if js.has_key('copy_of_object_id'):
            channel_id = js.get('copy_of_object_id') + '&mime_type'+ js.get('mime_type','video/mp4')
            video_url = vodTVP_GetStreamTokenizer(channel_id,proxy,timeout)
            return video_url
        elif js.has_key('video_url'):
            return js.get('video_url')
    return ''

def vodTVP_getImage(item,img_keys=['image_16x9','image']):
    urlImage = 'http://s.v3.tvp.pl/images/%s/%s/%s/uid_%s_width_%d_gs_0.jpg'
    iconUrl=''
    for key in img_keys:
        if key in item:
            iconFile = item[key][0].get('file_name',None)
            iconWidth = item[key][0].get('width',None)
            if iconFile and iconWidth:
                iconUrl = urlImage %(iconFile[0],iconFile[1],iconFile[2],iconFile[:-4],iconWidth)
            break
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


def vodTVPapi(parent_id=25621524,Count=150):
    js=vodTVP_getApiQuery(parent_id,Count)
    items = js.pop('items')
    lista_pozycji = []
    lista_katalogow = []
    #print 'parent_id',parent_id
    if js.get('found_any'):
        for item in items:
            if len(item.get('videoFormatMimes',[])):
                playable=_getPlayable(item)
                if playable.get('filename',''):
                    lista_pozycji.append(playable)
                    
            elif item.get('playable',False):
                playable=_getPlayable(item)
                if playable.get('filename',''):
                    playable['filename']=str(item.get('asset_id',''))
                    lista_pozycji.append(playable)                    
            else:
                img= vodTVP_getImage(item,['image','image_4x3'])      
                title= item.get('title','').encode('utf-8')
                _id=item.get('_id','')
                if item['url'].startswith('http'):
                    lista_katalogow.append({'img':img,'title':title,'id':_id})
    if len(lista_katalogow)==1 and lista_katalogow[0].get('title')=='wideo':
        (lista_katalogow,lista_pozycji) = vodTVPapi(lista_katalogow[0].get('id'),Count)
    return (lista_katalogow,lista_pozycji)

#url='http://188.47.195.3/token/video/live/26767399/20160921/1401320273/a8b4364c-e774-4cc8-a37b-5b35235a05be/live191.isml/manifest.m3u8'
#url='http://188.47.195.3/token/video/live/26771385/20160921/1401320273/373d5ad8-de22-4ad9-89d5-338e39ce3e0c/tvpinfo.isml/tvpinfo.m3u8'
def m3u_quality(url):
    #http://httpstream2.rai.it/Italy/rai2.isml/QualityLevels(1256000)/manifest(format=m3u8-aapl).m3u8
    out=[url]
    if url and url.endswith('.m3u8'):
        rptxt = re.search('/(\w+)\.m3u8',url)
        rptxt = rptxt.group(1) if rptxt else 'manifest'
        content = getUrl(url)
        #content = '#EXTM3U\r\n#EXT-X-VERSION:2\r\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=393072,RESOLUTION=512x288\r\nQualityLevels(376000)/manifest(format=m3u8-aapl)\r\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=730332,RESOLUTION=512x288\r\nQualityLevels(706000)/manifest(format=m3u8-aapl)\r\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1251552,RESOLUTION=512x288\r\nQualityLevels(1216000)/manifest(format=m3u8-aapl)\r\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1905632,RESOLUTION=720x404\r\nQualityLevels(1856000)/manifest(format=m3u8-aapl)\r\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=2518832,RESOLUTION=1024x576\r\nQualityLevels(2456000)/manifest(format=m3u8-aapl)\r\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=3847432,RESOLUTION=1280x720\r\nQualityLevels(3756000)/manifest(format=m3u8-aapl)\r\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=7935432,RESOLUTION=1920x1080\r\nQualityLevels(7756000)/manifest(format=m3u8-aapl)\r\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=266032\r\nQualityLevels(256000)/manifest(format=m3u8-aapl)\r\n'
        matches=re.compile('RESOLUTION=(.*?)\r\n(QualityLevels\(.*\)/manifest\(format=m3u8-aapl\))').findall(content)
        if matches:
            out=[{'title':'auto','url':url}]
            #title, part = matches[0]
            for title, part in matches:
                one={'title':title,'url':url.replace('manifest',part)}
                out.append(one)
    return out
    
# a=vodTVPapi(19181289)
# a=vodTVPapi(26326674)
# a=vodTVPapi(26389937)
#a=vodTVPapi()
# Rozrywka
# a=vodTVPapi(22672029) 
# Latajacy klub dwojki
# a=vodTVPapi(24413489)
# vodTVP_GetStreamUrl(a[1][0]['filename'])
# vodTVP_GetStreamUrl('26401493')
# channel_id=a[1][1]['filename']
