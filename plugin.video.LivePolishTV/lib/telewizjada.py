# -*- coding: utf-8 -*-
"""
Created on Fri Jan 01 15:26:07 2016

@author: ramic
"""

import urllib2,urllib
import re
import time
import json as json

BASEURL='http://www.telewizjada.net/'

NameFix={
    "Private TV":"Private",
    "Extreme Sports":"Extreme Sport",
    "Boomerang Central":"Boomerang",
    "Domo+":"Domo+ HD",
    "TV PULS":"TV Puls",
    "TV6":"TV 6",
    "TV4":"TV 4",
    "Ale Kino+":"ale kino+",
    "TVN24 Biznes i Świat": "TVN 24 BIS",
    "Super Stacja" :"Superstacja",
    "FilmBox":"Filmbox",
    "FilmBox Action":"Filmbox Action",
    "HBO 2": "HBO2",
    "Sci Fi":"SciFi Universal",
    "Universal Channel":"Universal HD",
    "MiniMini+":"Minimini+",
    "Discovery":"Discovery Channel",
    "National Geographic":"National Geographic Channel",
    "Polsat Cafe":"Polsat Café",
    "Eleven Sport":"Eleven Sports",
    'Polsat Viasat Nature':'Viasat Nature',
    'Polsat Viasat Explore':'Viasat Explore',
    'Polsat Viasat History':'Viasat History'
    }

def fixForEPG(one):
    if one['title'] == "Polsat Viasat Explore":
        if 'explore' in one.get('img'):
            one['tvid'] = "Viasat Explore"
        elif 'history' in one.get('img'):
            one['tvid'] = "Viasat History"
        elif 'nature' in one.get('img'):
            one['tvid'] = "Viasat Nature"
    elif one['title'] in NameFix.keys():
        one['tvid'] =NameFix[one['title']]
    return one

def getUrl(url,data=None,cookies=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
    if cookies:
        req.add_header("Cookie", cookies)
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

def get_Cookies(url,params=None):
    req = urllib2.Request(url,params)
    sock=urllib2.urlopen(req)
    cookies=sock.info()['Set-Cookie']
    sock.close()
    return cookies

def get_cookie_value(cookies='',value='sesssid'):
    idx1=cookies.find(value+'=')
    if idx1==-1:
        return''
    else:
        idx2=cookies.find(';',idx1+1)
    return cookies[idx1:idx2]

def listChannels():     
    data=getUrl(BASEURL + 'get_channels.php')
    result = json.loads(data)
    out=[]
    for item in result['channels']:
        cookies =  get_Cookies(BASEURL + 'set_cookie.php','url=%s' % item['url'])
        msec = get_cookie_value(cookies,'msec')
        sessid = get_cookie_value(cookies,'sessid')
        cookie_ref = '|Cookie='+ urllib.quote_plus( msec + '; ' + sessid)
        
        href = getUrl(BASEURL + 'get_channel_url.php','cid=%d' % item['id'],cookies)
        
        one = { 'id': item['id'], 
                'title': item['displayName'].encode('utf-8'),
                'tvid': item['displayName'].encode('utf-8'),
                'img': BASEURL + item['bigThumb'],
                'group': item['categoryID'],
                'url': href+cookie_ref,
                'urlepg' :item['epgUrl'],
                'epgname':item['name'][6:],
                'href': item['url']}
        one_fix = fixForEPG(one)
        print one_fix.get('title')
        out.append(one_fix)
    return out


def get_mainchannel(cid=1):
    data=getUrl(BASEURL + 'get_mainchannel.php','cid=%s' % cid)
    return json.loads(data)


def get_root_telewizjada(addheader=False):     
    data=getUrl(BASEURL + 'get_channels.php')
    try:
        result = json.loads(data)
    except:
        result = {}
    out=[]
    if addheader:
        t='[COLOR yellow]Updated: %s (Telewizjada)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.append({'title':t,'tvid':'','img':'','url':'http://looknij.tv','group':'','urlepg':''})
    for item in result.get('channels',[]):
        item.update(get_mainchannel(item.get('id')))
        one = { 'id': item.get('id'), 
                'title': item.get('displayName').encode('utf-8') ,
                'tvid': item.get('displayName').encode('utf-8'),
                'img': BASEURL + item.get('thumb'),
                'group': item.get('categoryID'),
                'url': item.get('url'), #href+cookie_ref,
                'urlepg' :item.get('epgUrl'),
                'epgname':item.get('displayName'),
                'href': item.get('url')}
        
        one_fix = fixForEPG(one)
        print one_fix.get('title')
        out.append(one_fix)
    if addheader and len(out)==1:
        out=[]
    return out

#url=out[0].get('url')
#_id=out[0].get('id')
#url='http://l137.telewizjada.net:1935/tw/2014tvtvp1/playlist.m3u8'
def decode_url(url,_id):
    cookies =  get_Cookies(BASEURL + 'set_cookie.php','url=%s' % url)
    msec = get_cookie_value(cookies,'msec')
    sessid = get_cookie_value(cookies,'sessid')
    cookie_ref = '|Cookie='+ urllib.quote_plus( msec + '; ' + sessid)
    #http://www.telewizjada.net/live.php?cid=2    
    #href = getUrl(BASEURL + 'get_channel_url.php','cid=%d' % _id,cookies)    
    href = getUrl(BASEURL + 'get_channel_url.php','cid=%d' % _id,cookies)    
    if not href.startswith('http'):
        href = json.loads(href).get('url','')
    return href+cookie_ref 

def get_epg_now_next(channelname='polsat'):
    epg=getUrl('http://www.telewizjada.net/get_epg.php','channelname=%s&offset=60'%channelname)
    strout =''
    if epg:
        epg=json.loads(epg)
        if epg:
            strout='[COLOR green]%s[/COLOR], [COLOR blue]%s[/COLOR]'%( epg[0].get('title',''),epg[1].get('title','') ) 
    return strout
    #href=getUrl('http://www.telewizjada.net/get_epg.php','channelname=polsat&offset=60',cookies)

def get_epg(channelname='polsat'):
    epg=getUrl('http://www.telewizjada.net/get_epg.php','channelname=%s&offset=60'%channelname)
    strout =''
    if epg:
        epg=json.loads(epg)
        for one in epg:
            mytime = time.strftime('%H:%M', time.localtime(one.get('starttime')))
            strout += '%s [COLOR green]%s[/COLOR] [%s]\n' % (mytime,one.get('title').encode('utf-8') ,one.get('category').encode('utf-8'))
#        if epg:
 #           strout='[COLOR green]%s[/COLOR], [COLOR blue]%s[/COLOR]'%( epg[0].get('title',''),epg[1].get('title','') ) 
    return strout

def decode_all_urls(out,):
    out_hrefs=[]    
    for one in out:
        print one.get('title')
        vido_url = decode_url(one.get('url',''),one.get('id',''))
        if vido_url:
            one['url']=vido_url
            out_hrefs.append(one) 
    return out_hrefs


def build_m3u(out,fname='telewizjadatv.m3u'):    
    entry='#EXTINF:-1 tvg-id="{tvid}" tvg-logo="{img}" url-epg="{urlepg}" group-title="{group}",{title}\n{url}\n\n'
    OUTxmu='#EXTM3U\n'
    #OUTxmu=OUTxmu+'\n#EXTINF:-1, [COLOR yellow]Update: %s [/COLOR]\nhttp://www.youtube.com/\n\n' %(time.strftime("%d/%m/%Y: %H:%M:%S"))
    for one in out:
        OUTxmu=OUTxmu+entry.format(**one)
    myfile = open(fname,'w')
    myfile.write(OUTxmu)
    myfile.close()


if __name__ == "__main__":
    pass
    #out=get_root_telewizjada()
    #decode_url(out[0].get('url'),out[0].get('id'))
    #get_epg_now_next(out[0]['epgname'])
    #out2=decode_all_urls(out)
    #build_m3u(out,fname='telewizjadatv_new.m3u')
