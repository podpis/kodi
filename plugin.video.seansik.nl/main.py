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
cache = StorageServer.StorageServer("seansikNL")

import resources.lib.seansikNL as seansik
from resources.lib.multi_select import MultiChoiceDialog

base_url        = sys.argv[0]
addon_handle    = int(sys.argv[1])
args            = urlparse.parse_qs(sys.argv[2][1:])
my_addon        = xbmcaddon.Addon()
addonName       = my_addon.getAddonInfo('name')

PATH        = my_addon.getAddonInfo('path')
DATAPATH    = xbmc.translatePath(my_addon.getAddonInfo('profile')).decode('utf-8')
RESOURCES   = PATH+'/resources/'

FANART=None


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
    url,data = ex_link.split('?') if '?'in ex_link else (ex_link,None)
    filmy,pagination = seansik.scanMainpage(url,int(page),data)
    if pagination[0]:
        addLinkItem(name='[COLOR blue]<< poprzednia strona <<[/COLOR]', url=ex_link, mode='__page__M', page=pagination[0], IsPlayable=False)
    items=len(filmy)
    for f in filmy:
        addLinkItem(name=f.get('title'), url=f.get('href'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True,itemcount=items,fanart=f.get('img'))
    if pagination[1]:
        addLinkItem(name='[COLOR blue]>> następna strona >>[/COLOR]', url=ex_link, mode='__page__M', page=pagination[1], IsPlayable=False)


def ListSeriale(ex_link,page):
    filmy = seansik.scanTVshows()
    items=len(filmy)
    for f in filmy:
        addDir(name=f.get('title'), ex_link=f.get('href'), mode='getEpisodes', iconImage=f.get('img'), infoLabels=f, fanart=f.get('img'))
    
        

def ListEpisodes(ex_link):
    episodes = seansik.scanEpisodes(ex_link)
    for f in episodes:
        addLinkItem(name=f.get('title'), url=f.get('href'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True,fanart=f.get('img'))

def FSLinks(ex_link):
    filmy = seansik.Search(ex_link)
    for f in filmy:
        addLinkItem(name=f.get('title',''), url=f.get('url'), mode='getLinks', iconimage=f.get('icon'), infoLabels=f, IsPlayable=True,fanart=f.get('img'))
    

    
def getLinks(ex_link):
    linksL = seansik.getVideoLinks(ex_link)
    stream_url=''
    
    if len(linksL):
        if len(linksL)>1:
            lables = [x.get('host') for x in linksL]
            s = xbmcgui.Dialog().select('Dostępne źródła',lables)
        else:
            s=0
        print 's',s
        link=linksL[s].get('url') if s>-1 else ''
        host=linksL[s].get('host') if s>-1 else ''  

        try:
            stream_url = urlresolver.resolve(link)

        except Exception,e:
            stream_url=''
            s = xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]','host [B]%s[/B] padł'%host,'UTRresolver ERROR: [%s]'%str(e))
    
    print stream_url
    #xbmcgui.Dialog().ok('',stream_url)
    if stream_url:
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
    else:
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=''))


def linkdata(jezyk):
    outstr=''
    if jezyk:
        outstr+='wersja[%s]+'%jezyk
    print '$$$ linkdata',outstr
    return outstr
        
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

jezyk = my_addon.getSetting('jezyk')

mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]
page = args.get('page',[1])[0]

if mode is None:
    addLinkItem("[COLOR lightblue]Ustaw język[/COLOR] [COLOR blue][B]"+jezyk+"[/B][/COLOR]",'',mode='setJezyk',IsPlayable=False)
    addDir(name="[COLOR blue]Filmy[/COLOR]",ex_link='http://www.seansik.nl/filmy-online/',page=1, mode='ListMovies',iconImage='DefaultFolder.png')
    #addDir(name="Filmy (Lektor,Dubbing,Polskie)",ex_link='http://alltube.tv/filmy-online/wersja[Lektor,Dubbing,PL]+',page=1, mode='ListMovies',iconImage='DefaultFolder.png')
    addDir(name=" => [Gatunek]",ex_link='gatunek',page=1, mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name=" => [Rok]",ex_link='rok',page=1, mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    #addDir(name=" => [Język]",ex_link='jezyk',page=1, mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)

    addDir(name="[COLOR blue]Junior[/COLOR]",ex_link='http://www.seansik.nl/filmy-online/kategoria[2,3,5,6,10,12]+',page=1, mode='ListMovies',iconImage='DefaultFolder.png')

    addDir(name="[COLOR green]Seriale[/COLOR]",ex_link=None,page=1, mode='ListSeriale',iconImage='DefaultFolder.png')
    addDir('Szukaj','',mode='Szukaj')


elif mode[0] =='setJezyk':
    data = ['Lektor','Dubbing','Napisy','PL','ENG']
    dialog = MultiChoiceDialog("Wybierz wersje językową", data)
    dialog.doModal()
    selected = ','.join([data[x] for x in dialog.selected])
    my_addon.setSetting('jezyk',selected)
    xbmc.executebuiltin('XBMC.Container.Refresh')

elif mode[0] == '__page__M':
    url = build_url({'mode': 'ListMovies', 'foldername': '', 'ex_link' : ex_link, 'page': page})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)
    
elif mode[0] == '__page__S':
    url = build_url({'mode': 'ListSeriale', 'foldername': '', 'ex_link' : ex_link, 'page': page})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)

elif mode[0] == '__page__P':
    url = build_url({'mode': 'PlaylistLinks', 'foldername': '', 'ex_link' : ex_link, 'page': page})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)
    
elif mode[0] == 'getEpisodes':
    ListEpisodes(ex_link)

elif mode[0] == 'ListMovies':
    data = linkdata(jezyk)
    ListMovies(ex_link+data,page)

elif mode[0] == 'ListSeriale':
    ListSeriale(ex_link,page)

elif mode[0] == 'getLinks':
    getLinks(ex_link)

elif mode[0] == 'searchItems':
    FSLinks(ex_link)

elif mode[0] == 'GatunekRok':
    data = seansik.filter(ex_link)
    if data:
        ret = xbmcgui.Dialog().select('Wybierz:', data[0])
        if ret>-1:
            href = 'http://www.seansik.nl/filmy-online/'+data[1][ret]+linkdata(jezyk)
            url = build_url({'mode': 'ListMovies', 'foldername': '', 'ex_link' : href, 'page': 1})
            xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)

elif mode[0] == 'Opcje':
    my_addon.openSettings()   

elif mode[0] =='Szukaj':
    addDir('[B]Nowe Szukanie[/B]','',mode='SzukajNowe')
    historia = HistoryLoad()
    if not historia == ['']:
        for entry in historia:
            contextmenu = []
            contextmenu.append(('Usuń', 'XBMC.Container.Refresh(%s)'% build_url({'mode': 'SzukajUsun', 'ex_link' : entry})),)
            contextmenu.append(('Usuń całą historię', 'XBMC.Container.Update(%s)' % build_url({'mode': 'SzukajUsunAll'})),)
            addDir(name=entry, ex_link=entry, mode='searchItems', fanart=None, contextmenu=contextmenu) 
        

        
elif mode[0] =='SzukajNowe':
    d = xbmcgui.Dialog().input('Szukaj, Podaj tytul filmu/serialu/bajki', type=xbmcgui.INPUT_ALPHANUM)
    if d:
        HistoryAdd(d)
        FSLinks(d)

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

