# -*- coding: utf-8 -*-

import sys,re,os
import urllib,urllib2
import urlparse
import xbmc,xbmcgui,xbmcaddon
import xbmcplugin
import urlresolver


import resources.lib.ekstraklasa as ekstraklasa
import resources.lib.estadios as estadios

base_url        = sys.argv[0]
addon_handle    = int(sys.argv[1])
args            = urlparse.parse_qs(sys.argv[2][1:])
my_addon        = xbmcaddon.Addon()
addonName       = my_addon.getAddonInfo('name')

PATH        = my_addon.getAddonInfo('path')
DATAPATH    = xbmc.translatePath(my_addon.getAddonInfo('profile')).decode('utf-8')
RESOURCES   = PATH+'/resources/'

FANART=RESOURCES+'fanart.png'
ekstraklasa.GATE = ''
if my_addon.getSetting('bramka')=='true':
    ekstraklasa.GATE = 'http://invisiblesurf.review/index.php?q='

## COMMON Functions

def addLinkItem(name, url, mode, params=1, iconimage=None, infoLabels=False, IsPlayable=True,fanart=FANART,itemcount=1):
    u = build_url({'mode': mode, 'foldername': name, 'ex_link' : url, 'params':params})
    
    if iconimage==None:
        iconimage='DefaultFolder.png'
    liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    
    if not infoLabels:
        infoLabels={"title": name}
    liz.setInfo(type="video", infoLabels=infoLabels)
    if IsPlayable:
        liz.setProperty('IsPlayable', 'true')
    if fanart:
        liz.setProperty('fanart_image',fanart)
    contextMenuItems = []
    contextMenuItems.append(('Informacja', 'XBMC.Action(Info)'))
    liz.addContextMenuItems(contextMenuItems, replaceItems=False)        
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz,isFolder=False,totalItems=itemcount)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%R, %Y, %P")
    return ok

def addDir(name,ex_link=None, params=1, mode='folder',iconImage='DefaultFolder.png', infoLabels=None, fanart=FANART,contextmenu=None):
    url = build_url({'mode': mode, 'foldername': name, 'ex_link' : ex_link, 'params' : params})

    li = xbmcgui.ListItem(name, iconImage=iconImage, thumbnailImage=iconImage)
    if infoLabels:
        li.setInfo(type="movie", infoLabels=infoLabels)
    if fanart:
        li.setProperty('fanart_image', fanart )
    if contextmenu:
        contextMenuItems=contextmenu
        li.addContextMenuItems(contextMenuItems, replaceItems=True) 
    else:
        contextMenuItems = []
        contextMenuItems.append(('Informacja', 'XBMC.Action(Info)'),)
        li.addContextMenuItems(contextMenuItems, replaceItems=False)  
          
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%R, %Y, %P")

def encoded_dict(in_dict):
    out_dict = {}
    for k, v in in_dict.iteritems():
        if isinstance(v, unicode):
            v = v.encode('utf8')
        elif isinstance(v, str):
            # Must be encoded in UTF-8
            v.decode('utf8')
        out_dict[k] = v
    return out_dict
    
def build_url(query):
    return base_url + '?' + urllib.urlencode(encoded_dict(query))
 
def getLinks(ex_link):
    linksL = ekstraklasa.getVideoLinks(ex_link)
    stream_url=''
    
    if len(linksL):
        if len(linksL)>1:
            lables = [x.get('label') for x in linksL]
            s = xbmcgui.Dialog().select('Dostępne jakości',lables)
        else:
            s=0
        #print 's',s
        stream_url=linksL[s].get('url') if s>-1 else ''
        host=linksL[s].get('label') if s>-1 else ''  

    
    print stream_url
    #xbmcgui.Dialog().ok('',stream_url)
    if stream_url:
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
    else:
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=''))

def estadios_getLinks(ex_link):
    link = estadios.getVideoLinks(ex_link)
    #xbmcgui.Dialog().ok('',link)
    if link:
        print link
        if 'extragoals' in link:
            import resources.lib.extragoalsresolver as extragoalsresolver
            stream_url = extragoalsresolver.getVideoUrls(link)
            #xbmcgui.Dialog().ok('',stream_url)
        else:
            try:
                stream_url = urlresolver.resolve(link)
            except Exception,e:
                stream_url=''
                s = xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]',str(e))
    
    print 'stream_url',stream_url
    if stream_url:
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
    else:
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=''))
                
## ######################
## MAIN
## ######################
            
    
xbmcplugin.setContent(addon_handle, 'video')	

mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]
params = args.get('params',[{}])[0]

# LigaTitle = my_addon.getSetting('LigaTitle')
# LigaUrl = my_addon.getSetting('LigaUrl')

if mode is None:
    addDir(name="[COLOR lightgreen]Live[/COLOR]",ex_link='',params={'user':'Ekstraklasa','sort':'live','page':'1'}, mode='getVideos',iconImage=RESOURCES+'../icon.png')
    addDir(name="Najnowsze",ex_link='Ekstraklasa',params={'user':'Ekstraklasa','sort':'recent','page':'1'}, mode='getVideos',iconImage=RESOURCES+'../icon.png')
    addDir(name="Najpopularniejsze",ex_link='Ekstraklasa',params={'user':'Ekstraklasa','sort':'visited','page':'1'}, mode='getVideos',iconImage=RESOURCES+'../icon.png')
    addDir('[COLOR blue]Skróty meczów[/COLOR]',ex_link='http://estadios.pl/skroty-meczow',params={}, mode='Estadios_skroty_Liga',iconImage=RESOURCES+'estadios.png')
    addDir('[COLOR blue]Football Video[/COLOR]',ex_link='',params={}, mode='livefootballol',iconImage=RESOURCES+'livefootballol.png')
    addLinkItem('[COLOR gold]-=Opcje=-[/COLOR]','','Opcje',IsPlayable=False)
##    

    
elif mode[0] =='Estadios_skroty':
    #url = LigaUrl if LigaUrl else ex_link
    out=estadios.get_skroty_meczow(ex_link)
    for f in out:
        addLinkItem(name=f.get('title'), url=f.get('url'), mode='Estadios_play', iconimage=f.get('img'), infoLabels=f, IsPlayable=True,fanart=f.get('img'))

elif mode[0] =='Estadios_skroty_Liga':
    data = estadios.get_liga()
    if data:
        label = [estadios.unicodePLchar(x[1].strip()) for x in data]
        value = [x[0].strip() for x in data]
        for t,v in zip(label,value):
            addDir(t,ex_link=v,params={}, mode='Estadios_skroty',iconImage='DefaultFolder.png')


elif mode[0] =='Estadios_play':
    estadios_getLinks(ex_link) 
##    

elif mode[0].startswith('livefootballol'):
    import resources.lib.livefootballol as livefootballol
    if '_play_' in mode[0]:
        #xbmcgui.Dialog().ok('_play_',ex_link)
        link = livefootballol.getVideoLinks(ex_link)
        try:
            stream_url = urlresolver.resolve(link)
        except Exception,e:
            stream_url=''
            xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]',str(e))
                
        print 'stream_url',stream_url
        if stream_url:
            xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
        else:
            xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=''))
    elif '_page_' in mode[0]:
        url = build_url({'mode': 'livefootballol_content_', 'foldername': '', 'ex_link' : ex_link, })
        xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)
    elif '_content_' in mode[0]:
        items,pagination = livefootballol.get_games(ex_link)
        if pagination[0]:
            addLinkItem(name='[COLOR blue]<< poprzednia strona <<[/COLOR]', url=pagination[0], mode='livefootballol_page_', IsPlayable=False)
        for one in items:
            addLinkItem(one.get('title',''),  one['url'], mode='livefootballol_play_', IsPlayable=True,infoLabels=one, iconimage=one.get('img')) 
        if pagination[1]:
            addLinkItem(name='[COLOR blue]>> następna strona >>[/COLOR]', url=pagination[1], mode='livefootballol_page_', IsPlayable=False)
    else:
        content = livefootballol.get_video()
        for one in content: # 
            addDir(one.get('title',''),  one['url'], mode='livefootballol_content_')      


elif mode[0] == 'Opcje':
    my_addon.openSettings()     

elif mode[0] =='getLinks':
    getLinks(ex_link)

elif mode[0] =='getVideos':
    print 'getVideos',params
    params = eval(params)
    print type(params)
    Litems,pagination = ekstraklasa.getVideos(**params)
    if pagination[0]:
        addLinkItem(name='[COLOR blue]<< poprzednia strona <<[/COLOR]', url=ex_link, mode='__page__', params=pagination[0], IsPlayable=False)
    items=len(Litems)
    for f in Litems:
        f['code']= f.get('duration_formatted','')
        f['code']='[COLOR lightgreen]onAir[/COLOR]' if f.get('onair',False) else f['code']
        addLinkItem(name=f.get('title'), url=f.get('id'), mode='getLinks', iconimage=f.get('thumbnail_240_url'), infoLabels=f, IsPlayable=True,itemcount=items,fanart=f.get('img'))
    if pagination[1]:
        addLinkItem(name='[COLOR blue]>> następna strona >>[/COLOR]', url=ex_link, mode='__page__', params=pagination[1], IsPlayable=False)

elif mode[0] == '__page__':
    url = build_url({'mode': 'getVideos', 'foldername': '', 'ex_link' : ex_link, 'params': params})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)

elif mode[0] == 'Opcje':
    my_addon.openSettings()   

elif mode[0] == 'folder':
    pass

else:
    xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=''))        


xbmcplugin.endOfDirectory(addon_handle)

