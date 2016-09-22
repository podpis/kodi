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

FANART=RESOURCES+'tlo.jpg'

import resources.lib.animepl as animepl


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



def getEpisodes(ex_link):
    episodes = animepl.get_episodes(ex_link)
    #xbmcgui.Dialog().ok('Linki %d'%len(episodes),ex_link)
    for f in episodes:
        addLinkItem(name=f.get('title'), url=f.get('url'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True)
   

def getLinks(ex_link):
    linksL = animepl.getLinks(ex_link)
    stream_url=''
    lables = [x.get('title') for x in linksL]
    s = xbmcgui.Dialog().select('Linki',lables)
    link = linksL[s].get('url') if s>-1 else ''
    link = animepl.getVideoUrl(link)
    if link:
        #xbmcgui.Dialog().ok('Link',link)
        if 'sibnet.ru' in link:
           stream_url = link
        else:
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
    addDir(name="Popularne anime",ex_link='http://on-anime.pl/anime/', mode='on_anime:popularne_anime',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="Katalog anime",ex_link='', mode='on_anime:katalog_anime',page='1',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="Sezony anime",ex_link='http://on-anime.pl/sezon/', mode='on_anime:sezony_anime',page='1',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="Szukaj",ex_link='', mode='on_anime:szukaj',page='1',iconImage='DefaultFolder.png',fanart=FANART)

elif mode[0] == '__page__':
    url = build_url({'mode': ex_link, 'foldername': '', 'ex_link' : '','page':page})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)

elif mode[0] == '__page__S':
    url = build_url({'mode': 'on_anime:sezony_anime', 'foldername': '', 'ex_link' : ex_link,'page':page})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)

elif mode[0] == 'on_anime:popularne_anime':
    items = animepl.get_anime(ex_link)
    for f in items:
        addDir(name=f.get('title'), ex_link=f.get('url'), mode='on_anime:getEpisodes', iconImage=f.get('img'), infoLabels=f)

elif mode[0] == 'on_anime:sezony_anime':
    items,pagination = animepl.get_seasons(ex_link)
    if pagination[0]:
        addLinkItem(name='[COLOR green]<< Sezon: [B]%s[/B][/COLOR]'%pagination[0].get('title'), url=pagination[0].get('url'), page='1', mode='__page__S', IsPlayable=False)
    if pagination[1]:
        addLinkItem(name='[COLOR green]>> Sezon: [B]%s[/B][/COLOR]'%pagination[1].get('title'), url=pagination[1].get('url'), page='1', mode='__page__S', IsPlayable=False)
    for f in items:
        addDir(name=f.get('title'), ex_link=f.get('url'), mode='on_anime:getEpisodes', iconImage=f.get('img'), infoLabels=f)
    
    
elif mode[0] == 'on_anime:katalog_anime':
    sort_key = my_addon.getSetting('katalog_sortuj_key')
    sort_val = my_addon.getSetting('katalog_sortuj_val')
    if not sort_key or not sort_val:
        sort_key = 'Ilość głowsów malejąco'
        sort_val = '9'
    addLinkItem("[COLOR lightblue]Sortuj [/COLOR] [COLOR blue][B]"+sort_key+"[/B][/COLOR]",'',mode='on_anime:set_sort',IsPlayable=False)
    items,pagination=animepl.get_katalog_anime(dane='',strona=page,sortuj=sort_val)
    if pagination[0]:
        addLinkItem(name='[COLOR blue]<< Poprzednia strona <<[/COLOR]', url='on_anime:katalog_anime', page=pagination[0], mode='__page__', IsPlayable=False)
    for f in items:
        addDir(name=f.get('title'), ex_link=f.get('url'), mode='on_anime:getEpisodes', iconImage=f.get('img'), infoLabels=f)
    if pagination[1]:
        addLinkItem(name='[COLOR blue]>> Następna strona >>[/COLOR]', url='on_anime:katalog_anime', page=pagination[1], mode='__page__', IsPlayable=False)

elif mode[0] == 'on_anime:szukaj':
    d = xbmcgui.Dialog().input('Podaj tytuł', type=xbmcgui.INPUT_ALPHANUM)
    if d:
        dane='tytul-%s'%urllib.quote_plus(d)
        items,pagination=animepl.get_katalog_anime(dane=dane,strona=page,sortuj='9')
        for f in items:
            addDir(name=f.get('title'), ex_link=f.get('url'), mode='on_anime:getEpisodes', iconImage=f.get('img'), infoLabels=f)
        
    
elif mode[0] == 'on_anime:set_sort':
    keys = ['Alfabetycznie','Alfabetycznie malejąco','Data premiery','Data premiery malejąco','Ilość odcinków','Ilość odcinków malejąco',
            'Miejsce w rankingu','Miejsce w rankingu malejąco','Ocena','Ocena malejąco','Ilość głosów','Ilość głowsów malejąco']
    vals = ['0','1','2','3','4','5','6','7','10','11','8','9']
    selection = xbmcgui.Dialog().select('Sortuj po:',keys)
    if selection>-1:
        my_addon.setSetting('katalog_sortuj_key', keys[selection])      
        my_addon.setSetting('katalog_sortuj_val', vals[selection])    
        xbmc.executebuiltin('XBMC.Container.Refresh')  

elif mode[0] == 'ListSeriale':
    ListSeriale(ex_link)

elif mode[0] == 'on_anime:getEpisodes':
    getEpisodes(ex_link)

elif mode[0] == 'getLinks':
    getLinks(ex_link)

elif mode[0] == 'folder':
    pass

xbmcplugin.endOfDirectory(addon_handle)

