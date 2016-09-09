# -*- coding: utf-8 -*-

import sys,re,os
import urllib,urllib2
import urlparse
import xbmc,xbmcgui,xbmcaddon
import xbmcplugin
import json 


base_url        = sys.argv[0]
addon_handle    = int(sys.argv[1])
args            = urlparse.parse_qs(sys.argv[2][1:])
my_addon        = xbmcaddon.Addon()

PATH        = my_addon.getAddonInfo('path')
RESOURCES   = PATH+'/resources/'
sys.path.append( os.path.join( PATH, "lib" ) )


# ____________________________
def getUrl(url,data=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link
    
def addLinkItem(name, url, mode, iconimage=None, infoLabels=False, IsPlayable=True,fanart=None):
    u = build_url({'mode': mode, 'foldername': name, 'ex_link' : url})
    
    if iconimage==None:
        iconimage='DefaultFolder.png'
    liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    if not infoLabels:
        infoLabels={"Title": name}
    liz.setInfo(type="Video", infoLabels=infoLabels)
    if IsPlayable:
        liz.setProperty('IsPlayable', 'true')
    if fanart:
        liz.setProperty('fanart_image',fanart)
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%P")
    return ok


def addDir(name,ex_link=None,mode='folder',iconImage='DefaultFolder.png',fanart=''):
    url = build_url({'mode': mode, 'foldername': name, 'ex_link' : ex_link})
    li = xbmcgui.ListItem(name, iconImage=iconImage)
    if fanart:
        li.setProperty('fanart_image', fanart )
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def m3u2list():
    out = []
    response=getUrl('https://www.dropbox.com/s/c10u75x2yf96ql3/IPTV%20PKC.m3u?dl=1')
    matches=re.compile('^#EXTINF:-?[0-9]*(.*?),(.*?)\n(.*?)$',re.I+re.M+re.U+re.S).findall(response)
           
    for params, t, u in matches:
        url = u.strip()
        title = t.strip()
        if url and ('http' in url or 'rtmp' in url):
            print url
            if not 'youtube' in url:
                one  = {"title": title, "url": url}
                match_params =re.compile(' (.+?)="(.*?)"',re.I+re.M+re.U+re.S).findall(params)
                for field, value in match_params:
                    one[renTags.get(field.strip().lower(),'')] = value.strip()
                out.append(one)
    return out


def play(ex_link,fname=''):
    print '##PLAY',ex_link
    if ex_link:
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=ex_link))
    else:
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=''))
        

##
# MAIN
##

xbmcplugin.setContent(addon_handle, 'movies')	

mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]


if mode is None:
    addDir('LiveTV: iptvsatlinks',mode='iptvsatlinks',iconImage=RESOURCES+'iptvsatlinks.jpg')
    addDir('LiveTV: ceskatelevize.cz',mode='czeska', iconImage=RESOURCES+'logo-ceskatelevize-full.png')
    addDir('LiveTV: iptv1',mode='m3u',iconImage=RESOURCES+'m3u.jpg')

elif mode[0] == 'Opcje':
    my_addon.openSettings()   


elif mode[0] == 'playUrl':
    play(ex_link)

elif mode[0] == 'm3u':
    m3u_items=m3u2list()
    for one in m3u_items:
        addLinkItem(one.get('title',''),  one['url'], 'playUrl', IsPlayable=True,infoLabels=one, iconimage=one.get('img')) 


elif mode[0].startswith('czeska'):
    import ceskatelevize
    if 'play' in mode[0]:
        stream_msg_url = ceskatelevize.getVideo(ex_link)
        if stream_msg_url.get('url',''):
            label=[x[0] for x in stream_msg_url.get('url')]
            value=[x[1] for x in stream_msg_url.get('url')]
            s = xbmcgui.Dialog().select('Select',label)
            steram_url= value[s] if s>-1 else ''
            play(steram_url)
        else:
            xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]',stream_msg_url.get('msg',''))
        
    else:
        items = ceskatelevize.get_root()
        for one in items:
            addLinkItem(one.get('title',''),  one.get('url'), 'czeska_play', IsPlayable=True,infoLabels=one, iconimage=one.get('img'))  

elif mode[0].startswith('iptvsatlinks'):
    import iptvsatlinks
    if '_play_' in mode[0]:
        if '.ts' in ex_link:
            finalUrl='plugin://plugin.video.f4mTester/?name=%s&url=%s&streamtype=TSDOWNLOADER'%(fname,urllib.quote_plus(ex_link))
            xbmc.executebuiltin('XBMC.RunPlugin('+finalUrl+')')
            xbmcgui.Dialog().ok('',ex_link)
            # finalUrl = ex_link
            # xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=finalUrl))
        else:
            play(ex_link,fname)
    elif '_content_' in mode[0]:
        m3u_items = iptvsatlinks.m3u2list(ex_link)
        for one in m3u_items:
            addLinkItem(one.get('title',''),  one['url'], 'iptvsatlinks_play_', IsPlayable=True,infoLabels=one, iconimage=one.get('img')) 
    else :
        content = iptvsatlinks.get_playlist()
        for one in content: # 
            if one['url']:
                addDir(one.get('title',''),  one['url'], 'iptvsatlinks_content_')      
            else:
                addLinkItem(one.get('title',''),  '', '', IsPlayable=False) 
                
xbmcplugin.endOfDirectory(addon_handle)
