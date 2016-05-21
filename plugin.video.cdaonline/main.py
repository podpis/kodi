# -*- coding: utf-8 -*-

import sys,re,os
import urllib,urllib2
import urlparse
import xbmc,xbmcgui,xbmcaddon
import xbmcplugin
import urlresolver

try:
   import StorageServer
except:
   import storageserverdummy as StorageServer
cache = StorageServer.StorageServer("cdaonline")


import resources.lib.cdaonline as cdaonline
import resources.lib.cdaresolver as cdaresolver
import resources.lib.playernautresolver as playernautresolver
import resources.lib.unshorten as unshorten


base_url        = sys.argv[0]
addon_handle    = int(sys.argv[1])
args            = urlparse.parse_qs(sys.argv[2][1:])
my_addon        = xbmcaddon.Addon()
addonName       = my_addon.getAddonInfo('name')

PATH        = my_addon.getAddonInfo('path')
RESOURCES   = PATH+'/resources/'

FANART=RESOURCES+'fanart.png'

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

def addSeparator(name, url='', mode='', iconimage=None, fanart=FANART):
    u = build_url({'mode': mode, 'foldername': name, 'ex_link' : url, 'page':1})
    liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setProperty('IsPlayable', 'false')
    if fanart:
        liz.setProperty('fanart_image',fanart)
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz,isFolder=False)
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
    

def ListMovies(ex_link,page):
    filmy,pagination = cdaonline.scanMainpage(ex_link,int(page))
    print '$$$$$$$$$$$$$$$$$$$$$$',filmy
    if pagination[0]:
        addLinkItem(name='[COLOR blue]<< poprzednia strona <<[/COLOR]', url=ex_link, mode='__page__M', page=pagination[1], IsPlayable=False)
    items=len(filmy)
    
    for f in filmy:
        addLinkItem(name=f.get('title'), url=f.get('href'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True,itemcount=items)
    if pagination[1]:
        addLinkItem(name='[COLOR blue]>> nastepna strona >>[/COLOR]', url=ex_link, mode='__page__M', page=pagination[1], IsPlayable=False)


def ListSeriale(ex_link,page):
    filmy,pagination = cdaonline.scanMainpage(ex_link,int(page))
    if pagination[0]:
        addLinkItem(name='[COLOR blue]<< poprzednia strona <<[/COLOR]', url=ex_link, mode='__page__S', page=pagination[1], IsPlayable=False)
    items=len(filmy)
    for f in filmy:
        addDir(name=f.get('title'), ex_link=f.get('href'), mode='getEpisodes', iconImage=f.get('img'), infoLabels=f)
    if pagination[1]:
        addLinkItem(name='[COLOR blue]>> nastepna strona >>[/COLOR]', url=ex_link, mode='__page__S', page=pagination[1], IsPlayable=False)

        

def ListEpisodes(ex_link):
    episodes = cdaonline.scanTVshow(ex_link)
    for f in episodes:
        addLinkItem(name=f.get('title'), url=f.get('href'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True)

    
def getLinks(ex_link):
    links = cdaonline.getVideoLinks(ex_link)
    stream_url=''
    print '$'*4
    print links
    t = [ x.get('title') for x in links]
    u = [ x.get('url') for x in links]
    h = [ x.get('host') for x in links]
    selection = xbmcgui.Dialog().select("Sources", t)
    if selection>-1:
        print '^^S unshorten.unshorten'
        link = unshorten.unshorten(u[selection])
        print link
        print '^^E unshorten.unshorten'
        if 'cda' in h[selection]:
            print 'CDA'
            stream_url = cdaresolver.getVideoUrls(link)
            if type(stream_url) is list:
                qualityList = [x[0] for x in stream_url]
                selection = xbmcgui.Dialog().select("Quality [can be set default]", qualityList)
                if selection>-1:
                    stream_url = cdaresolver.getVideoUrls(stream_url[selection][1])
                else:
                    stream_url=''
        elif 'playernaut' in h[selection]:
            print 'playernaut'
            print link
            stream_url = playernautresolver.getVideoUrls(link)
            print 'playernaut'
            print stream_url
            if type(stream_url) is list:
                qualityList = [x[0] for x in stream_url]
                hrefs = [x[1] for x in stream_url]
                selection = xbmcgui.Dialog().select("Quality [can be set default]", qualityList)
                if selection>-1:
                    stream_url=hrefs[selection]
                else:
                    stream_url=''
                
        else: 
            print '!!!urlresolver'
            print link
            stream_url = urlresolver.resolve(link)
            if stream_url:
                pass
            else:
                stream_url=''
                xbmcgui.Dialog().ok('[COLOR red] Problem [/COLOR]', 'Może inny link będzie działał?')
    
    print stream_url
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
    addDir(name="[COLOR blue]Filmy[/COLOR]",ex_link='http://cda-online.pl/filmy-online/',page=1, mode='ListMovies',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="Premiery",ex_link='http://cda-online.pl/kategoria/premiery/',page=1, mode='ListMovies',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="Filmy HD",ex_link='http://cda-online.pl/jakosc/hd/',page=1, mode='ListMovies',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name=" => [Gatunek]",ex_link='film|gatunek',page=1, mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name=" => [Rok]",ex_link='film|rok',page=1, mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    
    addDir(name="[COLOR blue]Seriale[/COLOR]",ex_link='http://cda-online.pl/seriale/',page=1, mode='ListSeriale',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name=" => [Gatunek]",ex_link='serial|gatunek',page=1, mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name=" => [Rok]",ex_link='serial|rok',page=1, mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    
    addDir('[COLOR green]Szukaj[/COLOR]','',mode='Szukaj')


elif mode[0] == '__page__M':
    url = build_url({'mode': 'ListMovies', 'foldername': '', 'ex_link' : ex_link, 'page': page})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)
    
elif mode[0] == '__page__S':
    url = build_url({'mode': 'ListSeriale', 'foldername': '', 'ex_link' : ex_link, 'page': page})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)
    
elif mode[0] == 'getEpisodes':
    ListEpisodes(ex_link)


elif mode[0] == 'ListMovies':
    ListMovies(ex_link,page)

elif mode[0] == 'ListSeriale':
    ListSeriale(ex_link,page)

elif mode[0] == 'getLinks':
    getLinks(ex_link)

elif mode[0] == 'GatunekRok':
    param = ex_link.split('|')
    data = cdaonline.getGatunekRok(rodzaj=param[0],typ=param[1])
    if data:
        ret = xbmcgui.Dialog().select('Wybierz:', data[0])
        if ret>-1:
            if param[0]=='film': 
                tryb = 'ListMovies'
            else:
                tryb = 'ListSeriale'
            url = build_url({'mode': tryb, 'foldername': '', 'ex_link' : data[1][ret], 'page': 1})
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
            addDir(name=entry, ex_link='http://cda-online.pl/?s='+entry.replace(' ','+'), mode='ListMovies', fanart=None, contextmenu=contextmenu) 
        

        
elif mode[0] =='SzukajNowe':
    d = xbmcgui.Dialog().input('Szukaj, Podaj tytul filmu/serialu/bajki', type=xbmcgui.INPUT_ALPHANUM)
    if d:
        HistoryAdd(d)
        ex_link='http://cda-online.pl/?s='+d.replace(' ','+')
        ListMovies(ex_link,page)

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

