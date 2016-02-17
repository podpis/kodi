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


## COMMON Functions
def getUrl(url,data=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link
    
def addLinkItem(name, url, mode, page=1, iconimage=None, infoLabels=False, IsPlayable=True,fanart=None):
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
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz,isFolder=False)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%R, %Y, %P")
    return ok

def addDir(name,ex_link=None, page=1, mode='folder',iconImage='DefaultFolder.png', infoLabels=None, fanart=''):
    url = build_url({'mode': mode, 'foldername': name, 'ex_link' : ex_link, 'page' : page})
    #li = xbmcgui.ListItem(name.encode("utf-8"), iconImage=iconImage)
    li = xbmcgui.ListItem(name, iconImage=iconImage)
    if infoLabels:
        li.setInfo(type="video", infoLabels=infoLabels)
    if fanart:
        li.setProperty('fanart_image', fanart )
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
    

def ListMovies(ex_link,page):
    filmy,pagination = cdaonline.scanMainpage(ex_link,int(page))
    if pagination[0]:
        addLinkItem(name='[COLOR blue]<< poprzednia strona <<[/COLOR]', url=ex_link, mode='__page__M', page=pagination[1], IsPlayable=False)
    for f in filmy:
        addLinkItem(name=f.get('title'), url=f.get('href'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True,fanart=None)
    if pagination[1]:
        addLinkItem(name='[COLOR blue]>> nastepna strona >>[/COLOR]', url=ex_link, mode='__page__M', page=pagination[1], IsPlayable=False)


def ListSeriale(ex_link,page):
    filmy,pagination = cdaonline.scanMainpage(ex_link,int(page))
    if pagination[0]:
        addLinkItem(name='[COLOR blue]<< poprzednia strona <<[/COLOR]', url=ex_link, mode='__page__S', page=pagination[1], IsPlayable=False)
    for f in filmy:
        addDir(name=f.get('title'), ex_link=f.get('href'), mode='getEpisodes', iconImage=f.get('img'), infoLabels=f)
    if pagination[1]:
        addLinkItem(name='[COLOR blue]>> nastepna strona >>[/COLOR]', url=ex_link, mode='__page__S', page=pagination[1], IsPlayable=False)

        

def ListEpisodes(ex_link):
    episodes = cdaonline.scanTVshow(ex_link)
    for f in episodes:
        addLinkItem(name=f.get('title'), url=f.get('href'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True,fanart=None)

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
            print 'urlresolver'
            stream_url = urlresolver.resolve(u[selection])
    print 'resolved'
    print stream_url
    if stream_url:
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
    else:
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=stream_url))
        

## ######################
## MAIN
            
    
xbmcplugin.setContent(addon_handle, 'movies')	

mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]
page = args.get('page',[1])[0]

if mode is None:
    addDir(name="Premiery",ex_link='http://cda-online.pl/kategoria/premiery/',page=1, mode='ListMovies',iconImage='DefaultFolder.png',fanart='')
    addDir(name="Filmy HD",ex_link='http://cda-online.pl/jakosc/hd/',page=1, mode='ListMovies',iconImage='DefaultFolder.png',fanart='')
    addDir(name="Filmy",ex_link='http://cda-online.pl/filmy-online/',page=1, mode='ListMovies',iconImage='DefaultFolder.png',fanart='')
    addDir(name="Seriale",ex_link='http://cda-online.pl/seriale/',page=1, mode='ListSeriale',iconImage='DefaultFolder.png',fanart='')
    addDir('Szukaj','')
  

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

elif mode[0] == 'Opcje':
    my_addon.openSettings()   


elif mode[0] == 'folder':
    if fname == 'Szukaj':
        dialog = xbmcgui.Dialog()
        d = dialog.input('Szukaj, Podaj tytul filmu/serialu/bajki', type=xbmcgui.INPUT_ALPHANUM)
        ex_link='http://cda-online.pl/?s='+d.replace(' ','+')
        ListMovies(ex_link,page)


xbmcplugin.endOfDirectory(addon_handle)