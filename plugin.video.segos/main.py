# -*- coding: utf-8 -*-

import sys,re,os
import urllib,urllib2
import urlparse
import xbmc,xbmcgui,xbmcaddon
import xbmcplugin
#from metahandler import metahandlers
import urlresolver

try:
   import StorageServer
except:
   import storageserverdummy as StorageServer
cache = StorageServer.StorageServer("segos")


import resources.lib.segos as segos
import resources.lib.cdaresolver as cdaresolver

base_url        = sys.argv[0]
addon_handle    = int(sys.argv[1])
args            = urlparse.parse_qs(sys.argv[2][1:])
my_addon        = xbmcaddon.Addon()
addonName       = my_addon.getAddonInfo('name')

PATH        = my_addon.getAddonInfo('path')
DATAPATH    = xbmc.translatePath(my_addon.getAddonInfo('profile')).decode('utf-8')
RESOURCES   = PATH+'/resources/'
FANART      = None


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

def ListMovies(ex_link,page):
    filmy,pagination = segos.scanMainpage(ex_link,int(page))
    if pagination[0]:
        addLinkItem(name='[COLOR blue]<< Poprzednia strona <<[/COLOR]', url=ex_link, page=pagination[0], mode='__page__M', IsPlayable=False)
    items=len(filmy)
    for f in filmy:
        addLinkItem(name=f.get('title'), url=f.get('url'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True,itemcount=items)
    if pagination[1]:
        addLinkItem(name='[COLOR blue]>> Następna strona >>[/COLOR]', url=ex_link, page=pagination[1], mode='__page__M', IsPlayable=False)

def ListSearch(ex_link):
    filmy = segos.szukaj(ex_link)
    items=len(filmy)
    for f in filmy:
        addLinkItem(name=f.get('title'), url=f.get('url'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True,itemcount=items)
   

def getLinks(ex_link):
    linksL = segos.getVideoLinks(ex_link)
    stream_url=''
    print '#######',linksL
    if len(linksL):
        if len(linksL)>1:
            lables = [x.get('host') for x in linksL]
            s = xbmcgui.Dialog().select('Linki',lables)
        else:
            s=0
        
        link=linksL[s].get('href') if s>-1 else ''
        host=linksL[s].get('host') if s>-1 else ''        
        if 'cda' in host:
            print 'CDA'
            print link
            stream_url = cdaresolver.getVideoUrls(link)
            if type(stream_url) is list:
                qualityList = [x[0] for x in stream_url]
                selection = xbmcgui.Dialog().select("Wybierz jakość", qualityList)
                if selection>-1:
                    stream_url = cdaresolver.getVideoUrls(stream_url[selection][1])
                else:
                    stream_url=''
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
            
    
xbmcplugin.setContent(addon_handle, 'movies')	


mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]
page = args.get('page',[1])[0]

if mode is None:
    addDir(name="[COLOR blue]Filmy[/COLOR]",ex_link='http://segos.es/filmy.php?page=1', mode='ListMovies',page=1,iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name=" => [I]Kategorie Filmów[/I]",ex_link='cat', mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="[COLOR blue]Bajki[/COLOR]",ex_link='http://segos.es/bajki.php?page=1', mode='ListMovies',page=1,iconImage='DefaultFolder.png',fanart=FANART)

    addDir('[COLOR green]Szukaj[/COLOR]','',mode='Szukaj')
    #addLinkItem('[COLOR gold]-=Opcje=-[/COLOR]','','Opcje',IsPlayable=False)

    
elif mode[0] == 'Opcje':
    my_addon.openSettings()   

elif mode[0] == '__page__M':
    url = build_url({'mode': 'ListMovies', 'foldername': '', 'ex_link' : ex_link ,'page':page})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)
elif mode[0] == '__page__S':
    url = build_url({'mode': 'ListSeriale', 'foldername': '','ex_link' : ex_link ,'page':page})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)



elif mode[0] == 'ListMovies':
    ListMovies(ex_link,page)

elif mode[0] == 'getLinks':
    getLinks(ex_link)

elif mode[0] == 'ListSearch':
    ListSearch(ex_link)


elif mode[0] == 'GatunekRok':
    data = segos.get_kategorie()
    if data:
        label = [x[1].strip() for x in data]
        url = [x[0].strip() for x in data]
        ret = xbmcgui.Dialog().select('Wybierz: '+ex_link,label)
        if ret>-1:
            url = build_url({'mode': 'ListMovies', 'foldername': '', 'ex_link' : url[ret],'page':1})
            print url
            xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)

elif mode[0] =='Szukaj':
    addDir('[COLOR green]Nowe Szukanie[/COLOR]','',mode='SzukajNowe')
    historia = HistoryLoad()
    if not historia == ['']:
        for entry in historia:
            contextmenu = []
            contextmenu.append(('Usuń', 'XBMC.Container.Refresh(%s)'% build_url({'mode': 'SzukajUsun', 'ex_link' : entry})),)
            contextmenu.append(('Usuń całą historię', 'XBMC.Container.Update(%s)' % build_url({'mode': 'SzukajUsunAll'})),)
            addDir(name=entry, ex_link='http://segos.es/szukaj.php?title='+urllib.quote_plus(entry), mode='ListSearch', page=1, fanart=None, contextmenu=contextmenu) 

        
elif mode[0] =='SzukajNowe':
    d = xbmcgui.Dialog().input('Szukaj, Podaj tytuł filmu/serialu/bajki', type=xbmcgui.INPUT_ALPHANUM)
    if d:
        HistoryAdd(d)
        ListSearch('http://segos.es/szukaj.php?title='+urllib.quote_plus(d))

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

