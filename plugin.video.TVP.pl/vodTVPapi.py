# -*- coding: utf-8 -*-
"""
Created on Fri May 29 22:10:54 2015

@author: Michal
"""

import urllib2
#import simplejson 
import json as simplejson
from time import localtime, strftime


def getUrl(url):
    req = urllib2.Request(url)
    #req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link


def vodTVP_getApiQuery(parent_id,count=10):
    listing_url = 'http://www.api.v3.tvp.pl/shared/listing.php?dump=json'
    url = listing_url + '&direct=true&count=%d&parent_id=%s'% (count,parent_id)
    response = urllib2.urlopen(url)
    json = simplejson.loads(response.read())
    response.close()
    return json

def _getPlayable(episode):
    E={}
    E['filename'] = str(episode.get('_id',''))
    if 'video/mp4' in (episode.get('videoFormatMimes') or []):
        E['filename'] = E['filename']+'&mime_type=video/mp4'
    E['fanart'] = vodTVP_getImage(episode,'image_16x9')
    E['img'] = vodTVP_getImage(episode,'image')
    E['tvshowtitle'] =  episode.get('website_title','').encode('utf-8')
    E['title'] =  episode.get('title','').encode('utf-8')
    E['plot'] =  episode.get('description_root','').encode('utf-8')
    E['aired'] =  episode.get('publication_start_dt','').encode('utf-8')
    release_date = episode.get('release_date','')
    release_date_sec = release_date.get('sec','') if release_date else ''
    if release_date_sec:
        E['date'] =  strftime("%d.%m.%Y", localtime(release_date_sec))
    else:
        E['date']= '?'
    return E


def vodTVP_GetStreamUrl(channel_id):
    videofileinfo = urllib2.urlopen('http://www.tvp.pl/pub/stat/videofileinfo?video_id=' + channel_id)
    json = simplejson.loads(videofileinfo.read())
    videofileinfo.close()
    return json.get('video_url','')

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
    ROOT=[{'id': 1649941, 'img': '', 'title': 'seriale'},
          {'id': 1627183, 'img': '', 'title': 'filmy fabularne'},
          {'id': 4190012, 'img': '', 'title': 'dokumenty'},
          {'id': 4190017, 'img': '', 'title': 'archiwa'},
          {'id': 4934948, 'img': '', 'title': 'audycje / programy'},
          {'id': 8525989, 'img': '', 'title': '-> [Rozrywka]'}]
    return ROOT

def vodTVPapi(parent_id,Count=150):
    json=vodTVP_getApiQuery(parent_id,Count)
    items = json.pop('items')
    lista_pozycji = []
    lista_katalogow = []
    if json.get('found_any'):
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

# Rozrywka
# a=vodTVPapi(8525989) 
# Latajacy klub dwojki
# a=vodTVPapi(19021815)
# vodTVP_GetStreamUrl(a[1][2]['filename'])