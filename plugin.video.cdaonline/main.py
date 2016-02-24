# -*- coding: utf-8 -*-

import sys,re,os
import urllib,urllib2
import urlparse
import xbmc,xbmcgui,xbmcaddon
import xbmcplugin
import urlresolver

import resources.lib.cdaonline as cdaonline
import resources.lib.cdaresolver as cdaresolver

base_url        = sys.argv[0]
addon_handle    = int(sys.argv[1])
args            = urlparse.parse_qs(sys.argv[2][1:])
my_addon        = xbmcaddon.Addon()

PATH        = my_addon.getAddonInfo('path')
RESOURCES   = PATH+'/resources/'

FANART=RESOURCES+'fanart.png'

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

def addDir(name,ex_link=None, page=1, mode='folder',iconImage='DefaultFolder.png', infoLabels=None, fanart=FANART):
    url = build_url({'mode': mode, 'foldername': name, 'ex_link' : ex_link, 'page' : page})
    #li = xbmcgui.ListItem(name.encode("utf-8"), iconImage=iconImage)
    li = xbmcgui.ListItem(name, iconImage=iconImage, thumbnailImage=iconImage)
    if infoLabels:
        li.setInfo(type="movie", infoLabels=infoLabels)
    if fanart:
        li.setProperty('fanart_image', fanart )
    contextMenuItems = []
    contextMenuItems.append(('Informacja', 'XBMC.Action(Info)'))
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
        if 'cda' in h[selection]:
            print 'CDA'
            stream_url = cdaresolver.getVideoUrls(u[selection])
            if type(stream_url) is list:
                qualityList = [x[0] for x in stream_url]
                selection = xbmcgui.Dialog().select("Quality [can be set default]", qualityList)
                if selection>-1:
                    stream_url = cdaresolver.getVideoUrls(stream_url[selection][1])
                else:
                    stream_url=''
        else: 
            #print 'urlresolver'
            stream_url = urlresolver.resolve(u[selection])
    #print 'resolved'
    #print stream_url
    if stream_url:
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
    else:
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=stream_url))
        

## ######################
## MAIN
## ######################
            
    
xbmcplugin.setContent(addon_handle, 'video')	


mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]
page = args.get('page',[1])[0]

if mode is None:
    #addSeparator('[COLOR blue] FILMY == [/COLOR]',fanart=FANART)
    addDir(name="[COLOR blue]Filmy[/COLOR]",ex_link='http://cda-online.pl/filmy-online/',page=1, mode='ListMovies',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="Premiery",ex_link='http://cda-online.pl/kategoria/premiery/',page=1, mode='ListMovies',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="Filmy HD",ex_link='http://cda-online.pl/jakosc/hd/',page=1, mode='ListMovies',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name=" => [Gatunek]",ex_link='film|gatunek',page=1, mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name=" => [Rok]",ex_link='film|rok',page=1, mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    
    #addSeparator('[COLOR blue]SERIALE[/COLOR]',fanart=FANART)
    addDir(name="[COLOR blue]Seriale[/COLOR]",ex_link='http://cda-online.pl/seriale/',page=1, mode='ListSeriale',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name=" => [Gatunek]",ex_link='serial|gatunek',page=1, mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name=" => [Rok]",ex_link='serial|rok',page=1, mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    
    addDir('[COLOR green]Szukaj[/COLOR]','')
    

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


elif mode[0] == 'folder':
    if 'Szukaj' in fname:
        dialog = xbmcgui.Dialog()
        d = dialog.input('Szukaj, Podaj tytul filmu/serialu/bajki', type=xbmcgui.INPUT_ALPHANUM)
        ex_link='http://cda-online.pl/?s='+d.replace(' ','+')
        ListMovies(ex_link,page)
else:
    xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=''))        


xbmcplugin.endOfDirectory(addon_handle)