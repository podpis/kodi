# -*- coding: utf-8 -*-

import sys,re,os
import urllib,urllib2
import urlparse
import xbmc,xbmcgui,xbmcaddon
import xbmcplugin

try:
   import StorageServer
except:
   import storageserverdummy as StorageServer
cache = StorageServer.StorageServer("viderpl")


import resources.lib.viderpl as vider


base_url        = sys.argv[0]
addon_handle    = int(sys.argv[1])
args            = urlparse.parse_qs(sys.argv[2][1:])
my_addon        = xbmcaddon.Addon()
addonName       = my_addon.getAddonInfo('name')

PATH        = my_addon.getAddonInfo('path')
RESOURCES   = PATH+'/resources/'
FANART      = None

## COMMON Functions
def getUrl(url,data=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link
    
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
    contextMenuItems.append(('Informacja', 'XBMC.Action(Info)'))
    liz.addContextMenuItems(contextMenuItems, replaceItems=False)        
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz,isFolder=False,totalItems=itemcount)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%R, %Y, %P")
    return ok

def addDir(name,ex_link=None, page=1, mode='folder',iconImage='DefaultFolder.png', infoLabels=None, fanart=FANART,contextmenu=None):
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

## sub functions
    

def ListMovies(ex_link):
    if ex_link.startswith('search'):
        items=vider.search(ex_link.split('|')[-1].strip())
    else:
        items = vider.scanUser(ex_link)
        
    for item in items:
        if item.get('folder'):
            addDir(name=item.get('title',''),ex_link=item.get('href'), mode='ListMovies',iconImage=item.get('img'))
        else:
            addLinkItem(name=item.get('title'), url=item.get('href'), mode='getLinks', iconimage=item.get('img'), infoLabels=item, IsPlayable=True)
    

def getLinks(ex_link):
    stream_url = vider.getVideoUrls(ex_link)
    
    if stream_url:
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
    else:
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=stream_url))
        
## Historia wyszukiwania
def HistoryLoad():
    return cache.get('history').split(';')

def HistoryAdd(entry):
    history = HistoryLoad()
    if history == ['']:
        history = []
    history.insert(0, entry)
    cache.set('history',';'.join(history[:50]))

def HistoryDel(entry):
    history = HistoryLoad()
    history.remove(entry)
    if history:
        cache.set('history',';'.join(history[:50]))
    else:
        HistoryClear()

def HistoryClear():
    cache.delete('history')


## ######################
## MAIN
## ######################
            
    
xbmcplugin.setContent(addon_handle, 'video')	


mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]
page = args.get('page',[1])[0]

if mode is None:
    addDir(name="[COLOR blue]Strona Główna[/COLOR]",ex_link='http://vider.pl', mode='ListMovies',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="[COLOR blue]Ranking Vider.pl (30dni)[/COLOR]",ex_link='http://vider.pl/ranking/month', mode='ListMovies',iconImage='DefaultFolder.png',fanart=FANART)
    addDir('[COLOR green]Szukaj[/COLOR]','',mode='Szukaj')


elif mode[0] == '__page__M':
    url = build_url({'mode': 'ListMovies', 'foldername': '', 'ex_link' : ex_link})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)
    

elif mode[0] == 'ListMovies':
    ListMovies(ex_link)

elif mode[0] == 'ListSeriale':
    ListSeriale(ex_link,page)

elif mode[0] == 'getLinks':
    getLinks(ex_link)

elif mode[0] == 'GatunekRok':
    (jezyk,rok,gatunek) = mf.getGatunekRok()
    if ex_link=='Typ':
        data = jezyk
    elif ex_link=='Rok':
        data = rok
    elif ex_link=='Kategorie':
        data = gatunek
        
    if data:
        label = [x[1].strip() for x in data]
        url = [x[0].strip() for x in data]
        ret = xbmcgui.Dialog().select('Wybierz: '+ex_link,label)
        if ret>-1:
            url = build_url({'mode': 'ListMovies', 'foldername': '', 'ex_link' : mf.BASEURL+ url[ret]})
            xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)

elif mode[0] == 'Opcje':
    my_addon.openSettings()   

elif mode[0] =='Szukaj':
    addDir('[COLOR green]Nowe Szukanie[/COLOR]','',mode='SzukajNowe')
    historia = HistoryLoad()
    if not historia == ['']:
        for entry in historia:
            contextmenu = []
            contextmenu.append(('Usuń', 'XBMC.Container.Refresh(%s)'% build_url({'mode': 'SzukajUsun', 'ex_link' : entry})),)
            contextmenu.append(('Usuń całą historię', 'XBMC.Container.Update(%s)' % build_url({'mode': 'SzukajUsunAll'})),)
            addDir(name=entry, ex_link='search|'+entry, mode='ListMovies', fanart=None, contextmenu=contextmenu) 

        
elif mode[0] =='SzukajNowe':
    d = xbmcgui.Dialog().input('Szukaj, Podaj tytul', type=xbmcgui.INPUT_ALPHANUM)
    if d:
        HistoryAdd(d)
        ex_link='search|'+d
        ListMovies(ex_link)

elif mode[0] =='SzukajUsun':
    HistoryDel(ex_link)
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'%  build_url({'mode': 'Szukaj'}))

    
elif mode[0] == 'SzukajUsunAll':
    HistoryClear()
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'%  build_url({'mode': 'Szukaj'}))

elif mode[0] == 'folder':
    pass

else:
    xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=''))        


xbmcplugin.endOfDirectory(addon_handle)

