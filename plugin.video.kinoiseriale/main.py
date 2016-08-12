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
cache = StorageServer.StorageServer("kinoseriale")


import resources.lib.kinoseriale as kinoseriale
import resources.lib.cdaresolver as cdaresolver
import resources.lib.playernautresolver as playernautresolver
import resources.lib.unshorten as unshorten


base_url        = sys.argv[0]
addon_handle    = int(sys.argv[1])
args            = urlparse.parse_qs(sys.argv[2][1:])
my_addon        = xbmcaddon.Addon()
addonName       = my_addon.getAddonInfo('name')

PATH        = my_addon.getAddonInfo('path')
DATAPATH    = xbmc.translatePath(my_addon.getAddonInfo('profile')).decode('utf-8')
RESOURCES   = PATH+'/resources/'

FANART=RESOURCES+'fanart.png'

kinoseriale.BRAMKA = ''
if my_addon.getSetting('bramka')=='true':
    kinoseriale.BRAMKA = 'http://www.bramka.proxy.net.pl/index.php?q='


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
    filmy,pagination = kinoseriale.scanMainpage(ex_link,int(page))
    print '$$$$$$$$$$$$$$$$$$$$$$',filmy
    if pagination[0]:
        addLinkItem(name='[COLOR blue]<< poprzednia strona <<[/COLOR]', url=ex_link, mode='__page__M', page=pagination[1], IsPlayable=False)
    items=len(filmy)
    
    for f in filmy:
        addLinkItem(name=f.get('title'), url=f.get('href'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True,itemcount=items)
    if pagination[1]:
        addLinkItem(name='[COLOR blue]>> następna strona >>[/COLOR]', url=ex_link, mode='__page__M', page=pagination[1], IsPlayable=False)


def ListSeriale(ex_link,page):
    filmy,pagination = kinoseriale.scanMainpage(ex_link,int(page))
    if pagination[0]:
        addLinkItem(name='[COLOR blue]<< poprzednia strona <<[/COLOR]', url=ex_link, mode='__page__S', page=pagination[1], IsPlayable=False)
    items=len(filmy)
    for f in filmy:
        addDir(name=f.get('title'), ex_link=f.get('href'), mode='getEpisodes', iconImage=f.get('img'), infoLabels=f)
    if pagination[1]:
        addLinkItem(name='[COLOR blue]>> nastepna strona >>[/COLOR]', url=ex_link, mode='__page__S', page=pagination[1], IsPlayable=False)

        

def ListEpisodes(ex_link):
    episodes = kinoseriale.scanTVshow(ex_link)
    for f in episodes:
        addLinkItem(name=f.get('title'), url=f.get('href'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True)

    
def getLinks(ex_link):
    links = kinoseriale.getVideoLinks(ex_link)
    stream_url=''
    print '$'*4
    print links
    t = [ x.get('title') for x in links]
    u = [ x.get('url') for x in links]
    h = [ x.get('host') for x in links]
    selection = xbmcgui.Dialog().select("Sources", t)
    if selection>-1:
        link = u[selection]
        if 'offcard.net' in h[selection]:
            stream_url = link
            #item = xbmcgui.ListItem('title')
            #item.setProperty("SWFPlayer", "http://offcard.net/static/player/flowplayer-3.2.8.swf")
            # play won't accept unicode strings, so convert
            #xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(str(stream_url), item)
        elif 'cda' in h[selection]:
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
            try:
                stream_url = urlresolver.resolve(link)
            except Exception,e:
                stream_url=''
                s = xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]','Może inny link będzie działał?','ERROR: %s'%str(e))
    
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

def RankingiFilmowe(ex_link,page):
    folders = kinoseriale.Rankingi()
    for folder in folders:
        addDir(name=folder.get('title'),ex_link=folder.get('url'),page=1, mode='ListMovies',iconImage='DefaultFolder.png',fanart=FANART)
        
        
        
## ######################
## MAIN
## ######################
            
    
xbmcplugin.setContent(addon_handle, 'video')	


mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]
page = args.get('page',[1])[0]

if mode is None:
    addDir(name="[COLOR blue]Filmy[/COLOR]",ex_link='http://www.kinoiseriale.tv/filmy/szukaj.html?ask=Wyszukaj+Film&stype=1&site=1',page=1, mode='ListMovies',iconImage='DefaultFolder.png',fanart=FANART)
    #addDir(name="Premiery",ex_link='http://cda-online.pl/kategoria/premiery/',page=1, mode='ListMovies',iconImage='DefaultFolder.png',fanart=FANART)
    #addDir(name="Filmy HD",ex_link='http://cda-online.pl/jakosc/hd/',page=1, mode='ListMovies',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name=" => [Gatunki]",ex_link='film|gat',page=1, mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name=" => [Rok Produkcji]",ex_link='film|rok',page=1, mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name=" => [Typ filmu]",ex_link='film|mode',page=1, mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name=" => [Wersja językowa]",ex_link='film|mode',page=1, mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="Rankingi Filmowe",ex_link='',page=1, mode='RankingiFilmowe',iconImage='DefaultFolder.png',fanart=FANART)
    addDir('[COLOR green]Szukaj Film[/COLOR]',ex_link='&stype=1',mode='Szukaj')
    addDir(name="[COLOR blue]Seriale[/COLOR]",ex_link='http://www.kinoiseriale.tv/filmy/szukaj.html?ask=Wyszukaj+Film&stype=2&site=1',page=1, mode='ListSeriale',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name=" => [Gatunki]",ex_link='serial|gat',page=1, mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    #addDir(name=" => [Rok]",ex_link='serial|rok',page=1, mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    
    addDir('[COLOR green]Szukaj Serial[/COLOR]',ex_link='&stype=2',mode='Szukaj')
    #addLinkItem('[COLOR gold]-=Opcje=-[/COLOR]','','Opcje')

elif mode[0] == 'Opcje':
    my_addon.openSettings()   

elif mode[0] == '__page__M':
    url = build_url({'mode': 'ListMovies', 'foldername': '', 'ex_link' : ex_link, 'page': page})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)
    
elif mode[0] == '__page__S':
    url = build_url({'mode': 'ListSeriale', 'foldername': '', 'ex_link' : ex_link, 'page': page})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)
    
elif mode[0] == 'getEpisodes':
    ListEpisodes(ex_link)


elif mode[0] == 'RankingiFilmowe':
    RankingiFilmowe(ex_link,page)
    
elif mode[0] == 'ListMovies':
    ListMovies(ex_link,page)

elif mode[0] == 'ListSeriale':
    ListSeriale(ex_link,page)

elif mode[0] == 'getLinks':
    getLinks(ex_link)

elif mode[0] == 'GatunekRok':
    param = ex_link.split('|')
    data = kinoseriale.getGatunekRok(rodzaj=param[0],typ=param[1])
    if data:
        ret = xbmcgui.Dialog().select('Wybierz:', data[0])
        if ret>-1:
            if param[0]=='film': 
                tryb = 'ListMovies'
                url = re.sub('%s=0'%param[1],'%s=%s'%(param[1],data[1][ret]),'http://www.kinoiseriale.tv/filmy/szukaj.html?ask=Wyszukaj+Film&mode=0&type=0&qual=0&gat=0&rok=0&stype=1&site=1')
            else:
                tryb = 'ListSeriale'
                url = re.sub('%s=0'%param[1],'%s=%s'%(param[1],data[1][ret]),'http://www.kinoiseriale.tv/filmy/szukaj.html?ask=Wyszukaj+Film&mode=0&type=0&qual=0&gat=0&stype=2&site=1')
            url = build_url({'mode': tryb, 'foldername': '', 'ex_link' : url, 'page': 1})
            xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)

elif mode[0] == 'Opcje':
    my_addon.openSettings()   

elif mode[0] =='Szukaj':
    addDir('[COLOR green]Nowe Szukanie[/COLOR]',ex_link,mode='SzukajNowe')
    historia = HistoryLoad()
    if not historia == ['']:
        for entry in historia:
            if ex_link in entry:
                contextmenu = []
                contextmenu.append(('Usuń', 'XBMC.Container.Refresh(%s)'% build_url({'mode': 'SzukajUsun', 'ex_link' : entry})),)
                contextmenu.append(('Usuń całą historię', 'XBMC.Container.Update(%s)' % build_url({'mode': 'SzukajUsunAll'})),)
                addDir(name=entry.split('&')[0], ex_link='http://www.kinoiseriale.tv/filmy/szukaj.html?ask='+entry.replace(' ','+'), mode='ListMovies', fanart=None, contextmenu=contextmenu) 
        

        
elif mode[0] =='SzukajNowe':
    d = xbmcgui.Dialog().input('Szukaj, Podaj tytul filmu/serialu/bajki', type=xbmcgui.INPUT_ALPHANUM)
    if d:
        HistoryAdd(d+ex_link)
        url='http://www.kinoiseriale.tv/filmy/szukaj.html?ask='+d.replace(' ','+')+ex_link
        if ex_link=='&stype=1':
            ListMovies(url,'1')
        else:
            ListSeriale(url,'1')
        
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

