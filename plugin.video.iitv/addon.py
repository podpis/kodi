# -*- coding: utf-8 -*-

import sys,re,os
import urllib,urllib2
import urlparse
import xbmc,xbmcgui,xbmcaddon
import xbmcplugin

import urlresolver


base_url        = sys.argv[0]
addon_handle    = int(sys.argv[1])
args            = urlparse.parse_qs(sys.argv[2][1:])
my_addon        = xbmcaddon.Addon()
addonName       = my_addon.getAddonInfo('name')
my_addon_id     = my_addon.getAddonInfo('id')

FANART      = None

import iitv


## COMMON Functions

    
def addLinkItem(name, url, mode, page=1, iconimage=None, infoLabels=False, IsPlayable=True,fanart=FANART,itemcount=1):
    u = build_url({'mode': mode, 'foldername': name, 'ex_link' : url, 'page':page})
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
    #if 'urlSeries' in infoLabels.keys():
    #    contextMenuItems.append(('[COLOR green]Wszystkie Epizody[/COLOR]', 'RunPlugin(plugin://%s?mode=getEpisodes&ex_link=%s)'%(my_addon_id,infoLabels.get('urlSeries'))))
    contextMenuItems.append(('Informacja', 'XBMC.Action(Info)'))
    liz.addContextMenuItems(contextMenuItems, replaceItems=False)        
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz,isFolder=False,totalItems=itemcount)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%R, %Y, %P")
    return ok

def addDir(name,ex_link=None, page=0, mode='folder',iconImage='DefaultFolder.png', infoLabels=None, fanart=FANART,contextmenu=None,itemcount=1):
    url = build_url({'mode': mode, 'foldername': name, 'ex_link' : ex_link, 'page' : page})
    #li = xbmcgui.ListItem(name.encode("utf-8"), iconImage=iconImage)
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
          
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True,totalItems=itemcount)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%R, %Y, %P")
    return ok
    

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


## sub functions


def OstatnieSeriale(ex_link):
    seriale,pagination = iitv.getSeriale(ex_link)
    if pagination[0]:
        addLinkItem(name='[COLOR blue]<< Poprzednia strona <<[/COLOR]', url=pagination[0], mode='__page__', IsPlayable=False)
    for f in seriale:
        addLinkItem(name=f.get('title'), url=f.get('url'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True)
    if pagination[1]:
        addLinkItem(name='[COLOR blue]>> Następna strona >>[/COLOR]', url=pagination[1], mode='__page__', IsPlayable=False)


def ListSeriale(ex_link):
    if ex_link=='list':
        seriale = iitv.getList()
    elif ex_link=='popular':
        seriale = iitv.getPopular()
    items=len(seriale)
    for f in seriale:
        addDir(name=f.get('title'), ex_link=f.get('url'), mode='getEpisodes', iconImage=f.get('img'), infoLabels=f,itemcount=items)


def getEpisodes(ex_link):
    episodes = iitv.getEpisodes(ex_link)
    for f in episodes:
        addLinkItem(name=f.get('title'), url=f.get('url'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True)
        

def getLinks(ex_link):
    linksL = iitv.getLinks(ex_link)
    stream_url=''
    if len(linksL):
        lables = [x.get('title') for x in linksL]
        s = xbmcgui.Dialog().select('Linki',lables)
        link=linksL[s].get('url') if s>-1 else ''
        if link:
            link = iitv.getHostUrl(link)
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
            
    
xbmcplugin.setContent(addon_handle, 'movies')	

mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]

if mode is None:
    addDir(name="Ostatnio dodane",ex_link='1', mode='OstatnieSeriale',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="Popularne",ex_link='popular', mode='ListSeriale',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="Wszystkie",ex_link='list', mode='ListSeriale',iconImage='DefaultFolder.png',fanart=FANART)

elif mode[0] == '__page__':
    url = build_url({'mode': 'OstatnieSeriale', 'foldername': '', 'ex_link' : ex_link})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)

elif mode[0] == 'OstatnieSeriale':
    OstatnieSeriale(ex_link)

elif mode[0] == 'ListSeriale':
    ListSeriale(ex_link)

elif mode[0] == 'getEpisodes':
    getEpisodes(ex_link)

elif mode[0] == 'getLinks':
    getLinks(ex_link)

elif mode[0] == 'folder':
    pass

xbmcplugin.endOfDirectory(addon_handle)

