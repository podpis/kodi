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
cache = StorageServer.StorageServer("efilmy")


#import resources.lib.efilmy as ef

base_url        = sys.argv[0]
addon_handle    = int(sys.argv[1])
args            = urlparse.parse_qs(sys.argv[2][1:])
my_addon        = xbmcaddon.Addon()
addonName       = my_addon.getAddonInfo('name')

PATH        = my_addon.getAddonInfo('path')
DATAPATH    = xbmc.translatePath(my_addon.getAddonInfo('profile')).decode('utf-8')
sys.path.append( os.path.join( PATH,'resources','lib'))
RESOURCES   = PATH+'/resources/'
FANART      = None

import efilmy as ef
import filmwebapi as fa

ef.COOKIEFILE=os.path.join(DATAPATH,'efilmy.cookie')

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
    # meta={}
    # if infoLabels and infoLabels.get('year'):
    #     mg = metahandlers.MetaData()
    #     simpleyear=infoLabels.get('year','')
    #     simplename=infoLabels.get('title','').split('[')[0].strip()
    #     meta = mg.get_meta('movie', name=simplename ,year=simpleyear)

    #       print meta
    #     print infoLabels
    #     
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
def updateMetadata(item,use_filmweb='true',itemType='f'):
    if use_filmweb=='true':
        title= item.get('title','')
        year = item.get('year','')
        print title,year
        data = fa.searchFilmweb(title.decode('utf-8'),year.strip(),itemType)
        if data:
            item.update(data)
    item['title'] += item.get('audio','')
    return item 
        

def ListMovies(ex_link):
    use_filmweb_f = my_addon.getSetting('filmweb_f')
    filmy,pagination = ef.get_content(ex_link)
    if pagination[0]:
        addLinkItem(name='[COLOR blue]<< Poprzednia strona <<[/COLOR]', url=pagination[0], mode='__page__M', IsPlayable=False)
    items=len(filmy)
    for f in filmy:
        f=updateMetadata(f,use_filmweb_f,'f')
        addLinkItem(name=f.get('title'), url=f.get('url'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True,itemcount=items)
    if pagination[1]:
        addLinkItem(name='[COLOR blue]>> Następna strona >>[/COLOR]', url=pagination[1], mode='__page__M', IsPlayable=False)

def ListSearch(ex_link):
    out_m,out_s=ef.search(ex_link.replace(' ','+'))
    use_filmweb_s = my_addon.getSetting('filmweb_s')
    use_filmweb_f = my_addon.getSetting('filmweb_f')
    for f in out_m:
        f=updateMetadata(f,use_filmweb_f,'f')
        addLinkItem(name=f.get('title'), url=f.get('url'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True)
    
    for f in out_s:
        f=updateMetadata(f,use_filmweb_s,'s')
        addDir(name=f.get('title'), ex_link=f.get('url'), mode='getEpisodes', iconImage=f.get('img'), infoLabels=f)


def ListSeriale(page):
    print 'ListSeriale',page
    use_filmweb_s = my_addon.getSetting('filmweb_s')
    strona=int(page)
    filmy = ef.get_Serial_list(strona)
    
    if strona>0:
        addLinkItem(name='[COLOR blue]<< Poprzednia strona <<[/COLOR]', url=ex_link, mode='__page__S', page=strona-1, IsPlayable=False)
    items=len(filmy)
    for f in filmy:
        f=updateMetadata(f,use_filmweb_s,'s')
        addDir(name=f.get('title'), ex_link=f.get('url'), mode='getEpisodes', iconImage=f.get('img'), infoLabels=f)
    addLinkItem(name='[COLOR blue]>> Następna strona  >>[/COLOR]', url=ex_link, mode='__page__S', page=strona+1, IsPlayable=False,itemcount=items)


def ListEpisodes(ex_link):
    episodes = ef.get_Episode_list(ex_link)
    for f in episodes:
        addLinkItem(name=f.get('title'), url=f.get('url'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True)
        

def getLinks(ex_link):
    linksL = ef.getVideoLinks(ex_link)
    print '#######',linksL
    if len(linksL):
        lables = [x.get('msg') for x in linksL]
        s = xbmcgui.Dialog().select('Linki',lables)
        link=linksL[s].get('href') if s>-1 else ''
        if not link:
            link = ef.getLink_show_player(**linksL[s])
    
    if 'vidzer' in link:
         stream_url=link
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
            
    
xbmcplugin.setContent(addon_handle, 'movies')	


mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]
page = args.get('page',[1])[0]

if mode is None:
    addDir(name="[COLOR blue]Filmy[/COLOR]",ex_link='http://www.efilmy.tv/filmy.html', mode='ListMovies',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="Top Filmów",ex_link='', mode='Top_filmy',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name=" => [I]Kategorie Filmów[/I]",ex_link='cat', mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name=" => [I]Rok produkcji[/I]",ex_link='year', mode='GatunekRok',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="[COLOR blue]Seriale[/COLOR]",ex_link='',page=0, mode='ListSeriale',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="Top Seriali",ex_link='', mode='Top_seriale',iconImage='DefaultFolder.png',fanart=FANART)
    addDir(name="[B][COLOR yellow]D[COLOR blue]L[COLOR red]A [COLOR lightgreen]D[COLOR purple]Z[COLOR gold]I[COLOR blue]E[COLOR red]C[COLOR lightgreen]I[/COLOR][/B]",ex_link='http://www.efilmy.tv/kategoria,6,Familijne.html', mode='ListMovies',iconImage='DefaultFolder.png',fanart=FANART)
    
    addDir('[COLOR green]Szukaj[/COLOR]','',mode='Szukaj')
    addLinkItem('[COLOR gold]-=Opcje=-[/COLOR]','','Opcje',IsPlayable=False)

    
elif mode[0] == 'Opcje':
    my_addon.openSettings()   
    #xbmc.executebuiltin('XBMC.Container.Refresh()')
    
elif mode[0] == '__page__M':
    url = build_url({'mode': 'ListMovies', 'foldername': '', 'ex_link' : ex_link})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)
elif mode[0] == '__page__S':
    url = build_url({'mode': 'ListSeriale', 'foldername': '', 'ex_link' : '' ,'page':page})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)

elif mode[0].startswith('Top_'):
    what = mode[0].split('_')[-1]
    Label=['tydzien', '2 tygodnie', 'miesiąc','3 miesiące']
    Day = ['7','14','31','93']
    s = xbmcgui.Dialog().select('Top %s'%what,Label)
    d=Day[s] if s>-1 else Day[0]
    url = 'http://www.efilmy.net/%s.php?cmd=popularne&dni=%s'%(what,d)
    
    items = ef.get_top(url)
    if what == 'filmy':
        use_filmweb_f = my_addon.getSetting('filmweb_f')
        for f in items:
            f=updateMetadata(f,use_filmweb_f,'f')
            addLinkItem(name=f.get('title'), url=f.get('url'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True)
    else:
        for f in items:
            addDir(name=f.get('title'), ex_link=f.get('url'), mode='getEpisodes', iconImage=f.get('img'), infoLabels=f)

elif mode[0] == 'ListMovies':
    ListMovies(ex_link)

elif mode[0] == 'ListSeriale':
    ListSeriale(page)

elif mode[0] == 'getEpisodes':
    ListEpisodes(ex_link)

elif mode[0] == 'getLinks':
    getLinks(ex_link)

elif mode[0] == 'ListSearch':
    ListSearch(ex_link)



elif mode[0] == 'GatunekRok':
    data = ef.get_movie_cat_year(ex_link)

    if data:
        label = [x[0].strip() for x in data]
        url = [x[1].strip() for x in data]
        ret = xbmcgui.Dialog().select('Wybierz: '+ex_link,label)
        if ret>-1:
            url = build_url({'mode': 'ListMovies', 'foldername': '', 'ex_link' : url[ret]})
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
            addDir(name=entry, ex_link=entry.replace(' ','+'), mode='ListSearch', fanart=None, contextmenu=contextmenu) 

        
elif mode[0] =='SzukajNowe':
    d = xbmcgui.Dialog().input('Szukaj, Podaj tytuł filmu/serialu/bajki', type=xbmcgui.INPUT_ALPHANUM)
    if d:
        HistoryAdd(d)
        ListSearch(d)

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

