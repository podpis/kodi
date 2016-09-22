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

RESOURCES   = my_addon.getAddonInfo('path')+'/resources/'

FANART=False

import resources.lib.ekabaretypl as ekabaretypl


## COMMON Functions

    
def addLinkItem(name, url, mode, page='1', iconimage=None, infoLabels=False, IsPlayable=True,fanart=FANART,itemcount=1):
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

def addDir(name,ex_link=None, page='1', mode='folder',iconImage='DefaultFolder.png', infoLabels=None, fanart=FANART,contextmenu=None,itemcount=1):
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


def resolvePlay(link):
    stream_url=''
    if link:
        try:
            stream_url = urlresolver.resolve(link)
            #xbmcgui.Dialog().ok('stream_url',stream_url)
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
page= args.get('page',['1'])[0]


if mode is None:
    addLinkItem(name='[COLOR green]====== Skecze ======[/COLOR]', url='', page='', mode='', IsPlayable=False)
    addDir(name="  [COLOR lightgreen]Top Lista[/COLOR]",ex_link='http://www.ekabaret.pl/toplista.html', mode='getskecze',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="  [COLOR lightgreen]Polecane[/COLOR]",ex_link='http://www.ekabaret.pl/polecane.html', mode='getskecze',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="  [COLOR lightgreen]Wywiady i relacje[/COLOR]",ex_link='http://www.ekabaret.pl/wywiady.html', mode='getskecze',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="  [COLOR lightgreen][I]Szukaj[/I][/COLOR]",ex_link='http://www.ekabaret.pl/wideo.html',     mode='szukaj',iconImage='DefaultFolder.png',fanart=FANART)
    addLinkItem(name='[COLOR blue]====== Kategorie ======[/COLOR]', url='', page='', mode='', IsPlayable=False)
    addDir(name="  [COLOR lightblue]Kabarety[/COLOR]",ex_link='http://www.ekabaret.pl/kabarety.html', mode='getKategorie',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="  [COLOR lightblue]Soliści[/COLOR]",ex_link='http://www.ekabaret.pl/solisci.html', mode='getKategorie',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="  [COLOR lightblue]Grupy Impro[/COLOR]",ex_link='http://www.ekabaret.pl/impro.html', mode='getKategorie',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="  [COLOR lightblue]Stand-up[/COLOR]",ex_link='http://www.ekabaret.pl/standup.html', mode='getKategorie',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="  [COLOR lightblue][I]Szukaj[/I][/COLOR]",ex_link='http://www.ekabaret.pl/kategorie.html', mode='szukaj',iconImage='DefaultFolder.png',fanart=FANART)
    

elif mode[0].startswith('__page__'):
    nextmode = mode[0].split('|')[-1]
    url = build_url({'mode': nextmode, 'foldername': '', 'ex_link' : ex_link,'page':page})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)


elif mode[0] == 'getskecze':
    data = page if 'szukaj=' in page else None
    items,pagination = ekabaretypl.get_Skecze(ex_link,data)
    if pagination[0]:
        addLinkItem(name='[COLOR blue]<< Poprzednia strona <<[/COLOR]', url=pagination[0], page='', mode='__page__|getskecze', IsPlayable=False)
    for f in items:
        addLinkItem(name=f.get('title'), url=f.get('url'), mode='getLinks', iconimage=f.get('img'), infoLabels=f)
    if pagination[1]:
        addLinkItem(name='[COLOR blue]>> Następna strona >>[/COLOR]', url=pagination[1], page='', mode='__page__|getskecze', IsPlayable=False)

elif mode[0] == 'getKategorie':
    data = page if 'szukaj=' in page else None
    items,pagination = ekabaretypl.get_Katergorie(ex_link,data)
    if pagination[0]:
        addLinkItem(name='[COLOR blue]<< Poprzednia strona <<[/COLOR]', url=pagination[0], page='', mode='__page__|getKategorie', IsPlayable=False)
    for f in items:
        addDir(name=f.get('title'), ex_link=f.get('url'), mode='getskecze', iconImage=f.get('img'),infoLabels=f)
    if pagination[1]:
        addLinkItem(name='[COLOR blue]>> Następna strona >>[/COLOR]', url=pagination[1], page='', mode='__page__|getKategorie', IsPlayable=False)


elif mode[0] == 'szukaj':
    msg = 'Podaj tytuł skeczu' if 'wideo' in ex_link else 'Podaj nazwer kabaretu, solisty, grupy'
    d = xbmcgui.Dialog().input(msg, type=xbmcgui.INPUT_ALPHANUM)
    if d:
        data='szukaj=%s'%urllib.quote_plus(d)
        mmode='getskecze' if 'wideo' in ex_link else'getKategorie'
        url = build_url({'mode': mmode, 'foldername': '', 'ex_link' : ex_link,'page':data})
        xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url) 


elif mode[0] == 'getLinks':
    link = ekabaretypl.getVideoUrl(ex_link)
    resolvePlay(link)

elif mode[0] == 'folder':
    pass

xbmcplugin.endOfDirectory(addon_handle)

