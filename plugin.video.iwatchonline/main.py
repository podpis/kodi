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
cache = StorageServer.StorageServer("iwatchonline")

import resources.lib.iwatchonline as iwatchonline
import resources.lib.strings as strings

base_url        = sys.argv[0]
addon_handle    = int(sys.argv[1])
args            = urlparse.parse_qs(sys.argv[2][1:])

my_addon        = xbmcaddon.Addon()
my_addon_id     = my_addon.getAddonInfo('id')
addonName       = my_addon.getAddonInfo('name')

PATH        = my_addon.getAddonInfo('path')
DATAPATH    = xbmc.translatePath(my_addon.getAddonInfo('profile')).decode('utf-8')
RESOURCES   = PATH+'/resources/'
FANART      = None
 
__language__ = my_addon.getLocalizedString
iwatchonline.COOKIEFILE=os.path.join(DATAPATH,'cookie.iwatch')

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
    contextMenuItems.append((slan("Information"), 'XBMC.Action(Info)'))
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
        contextMenuItems.append((slan("Information"), 'XBMC.Action(Info)'),)
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

def slan(string_id):
    try:
        print 
        return my_addon.getLocalizedString(strings.STRINGS[string_id]).encode('utf-8', 'ignore')
    except Exception as e:
        print 'Failed String Lookup: %s (%s)' % (string_id, e)
    return string_id

    
def build_url(query):
    return base_url + '?' + urllib.urlencode(encoded_dict(query))

## sub functions

def ListMovies(ex_link):
    print ex_link
    filmy,pagination = iwatchonline.scanMainpage(ex_link)
    print 'ListMovies',pagination
    if pagination[0]:
        addLinkItem(name=slan("[COLOR blue]<< previous page <<[/COLOR]"), url=pagination[0], mode='__page__M', IsPlayable=False)
    items=len(filmy)
    for f in filmy:
        addLinkItem(name=f.get('title'), url=f.get('url'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True,itemcount=items)
    if pagination[1]:
        addLinkItem(name=slan("[COLOR blue]>> next page >>[/COLOR]"), url=pagination[1], mode='__page__M', IsPlayable=False)


def ListTVShows(ex_link):
    filmy,pagination = iwatchonline.scanMainpage(ex_link)
    print 'ListTVShows',pagination
    if pagination[0]:
        addLinkItem(name=slan("[COLOR blue]<< previous page <<[/COLOR]"), url=pagination[0], mode='__page__S', IsPlayable=False)
    items=len(filmy)
    for f in filmy:
        addDir(name=f.get('title'), ex_link=f.get('url'), mode='ListEpisodes', iconImage=f.get('img'), infoLabels=f,itemcount=items)
    if pagination[1]:
        addLinkItem(name=slan("[COLOR blue]>> next page >>[/COLOR]"), url=pagination[1], mode='__page__S', IsPlayable=False)

def ListEpisodes(ex_link):
    episodes = iwatchonline.scanTVShows(ex_link)
    for f in episodes:
        addLinkItem(name=f.get('title'), url=f.get('url'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True)



def ListSearch(ex_link):
    filmy = iwatchonline.search(ex_link) #'searchquery=india&searchin=m'
    items=len(filmy)
    if 'searchin=m' in ex_link:
        for f in filmy:
            addLinkItem(name=f.get('title'), url=f.get('url'), mode='getLinks', iconimage=f.get('img'), infoLabels=f, IsPlayable=True,itemcount=items)
    else:
        for f in filmy:
            addDir(name=f.get('title'), ex_link=f.get('url'), mode='ListEpisodes', iconImage=f.get('img'), infoLabels=f,itemcount=items)    

def getLinks(ex_link):
    linksL = iwatchonline.getVideoLinks(ex_link)
    stream_url=''
    print '#######',linksL
    if len(linksL):
        if len(linksL)>1:
            lables = [x.get('msg') for x in linksL]
            s = xbmcgui.Dialog().select(slan('Available Sources'),lables)
        else:
            s=0
        print 's',s
        link=linksL[s].get('href') if s>-1 else ''
        host=linksL[s].get('host') if s>-1 else ''        
        if link:
            link = iwatchonline.getLinkUrl(link)
            print link
            if 'cda.pl' in host:
                print 'CDA'
                print link
                stream_url = cdaresolver.getVideoUrls(link)
                if type(stream_url) is list:
                    qualityList = [x[0] for x in stream_url]
                    selection = xbmcgui.Dialog().select(slan('Select video quality'), qualityList)
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

def linkdata(quality,language,sort,gener=False):
    data={}
    if quality:
        data['quality']=quality
    if language:
        data['language']=language
    if sort:
        data['sort']=sort
    if gener:
        data['gener']=gener
    print '$$$ linkdata',urllib.urlencode(data) 
    return urllib.urlencode(data)
        
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
my_addon.setSetting('set','set')
language = my_addon.getSetting('language')
quality = my_addon.getSetting('quality')
sort = my_addon.getSetting('sort')
genre = my_addon.getSetting('genre')

genreT = my_addon.getSetting('genreT')
sortT = my_addon.getSetting('sortT')

mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]
page = args.get('page',[1])[0]

if mode is None:
    addDir(name="[COLOR blue][B]="+slan('Movies')+"=[/B][/COLOR]",ex_link='https://www.iwatchonline.lol/movies?', mode='ListMovies',iconImage='DefaultFolder.png',fanart=FANART)
    addLinkItem("  [COLOR lightblue]"+slan('Set Quality')+"[/COLOR] [COLOR blue][B]"+quality+"[/B][/COLOR]",'',mode='setQuality',IsPlayable=False)
    addLinkItem("  [COLOR lightblue]"+slan('Set Language')+"[/COLOR] [COLOR blue][B]"+language+"[/B][/COLOR]",'',mode='setLanguage',IsPlayable=False)
    addLinkItem("  [COLOR lightblue]"+slan('Set Genre')+"[/COLOR] [COLOR blue][B]"+genre+"[/B][/COLOR]",'',mode='setGenre',IsPlayable=False)
    addLinkItem("  [COLOR lightblue]"+slan('Sort by')+"[/COLOR] [COLOR blue][B]"+sort+"[/B][/COLOR]",'',mode='setSort',IsPlayable=False)
    
    addDir('  [COLOR blue]'+slan('Search Movies')+'[/COLOR]','searchquery=%s&searchin=m',mode='Szukaj')
    addDir(name="[COLOR green][B]="+slan('TV Shows')+"=[/B][/COLOR]",ex_link='https://www.iwatchonline.lol/tv-show?', mode='ListTVShows',iconImage='DefaultFolder.png',fanart=FANART)
    addLinkItem("  [COLOR lightgreen]"+slan('Set Genre')+"[/COLOR] [COLOR green][B]"+genreT+"[/B][/COLOR]",'T',mode='setGenre',IsPlayable=False)
    addLinkItem("  [COLOR lightgreen]"+slan('Sort by')+"[/COLOR] [COLOR green][B]"+sortT+"[/B][/COLOR]",'T',mode='setSort',IsPlayable=False)
    addDir('  [COLOR green]'+slan('Search TV Shows')+'[/COLOR]','searchquery=%s&searchin=t',mode='Szukaj')

elif mode[0] =='setSort':
    label=['[COLOR white][B]All[/B][/COLOR]','Popular','Featured','IMDB Score','Rotten Score','Metacritc Score']
    value=['','popular','featured','imdb','rotten','metacritc']
    if ex_link: #remove for T tvshows Rotten score
        label.pop(4)
        value.pop(4)
    s = xbmcgui.Dialog().select(slan('Select video quality'),label)
    s = s if s>-1 else 0
    my_addon.setSetting('sort'+ex_link,value[s])
    xbmc.executebuiltin('XBMC.Container.Refresh')
    
elif mode[0] =='setGenre':
    data = iwatchonline.getGenre()
    data[0] = [(''),('[COLOR white][B]All[/B][/COLOR]')]
    if data:
        label = [x[1].strip() for x in data]
        value = [x[0].strip() for x in data]
        s = xbmcgui.Dialog().select(slan('Select Genre'),label)
        s = s if s>-1 else 0
        my_addon.setSetting('genre'+ex_link,value[s])
    xbmc.executebuiltin('XBMC.Container.Refresh')

elif mode[0] =='setQuality':
    label=['[COLOR white][B]All[/B][/COLOR]','Latest HD Movies','Latest DVD Movies']
    value=['','hd','dvd']
    s = xbmcgui.Dialog().select(slan('Select video quality'),label)
    s = s if s>-1 else 0
    my_addon.setSetting('quality',value[s])
    xbmc.executebuiltin('XBMC.Container.Refresh')

elif mode[0] =='setLanguage':
    #label=iwatchonline.getLanguages()
    label= ['[COLOR white][B]All[/B][/COLOR]','Polish','English','French','Russian','Hindi','Spanish','German','Arabic','Bulgarian','Chinese','Croatian','Dutch','Finnish',
    'Greek','Hebrew','Hungarian','Icelandic','Italian','Japanese','Korean','Norwegian','Persian','Portuguese','Punjabi','Romanian','Swedish',
    'Turkish','Ukrainian','Danish','Indonesian','Tibetan','Belgium','Thailand','Laos','Pashto','Albanian','Malaysian','M\xc4\x81ori','Austria',
    'Urdu','Czech','Malay','Tamil','Mandarin','Cantonese','Vietnam','Filipino','Tagalog','Lithuanian','Estonian','Somali','Marathi']
    s = xbmcgui.Dialog().select('Video Language',label)
    value = label[s] if s>0 else ''
    my_addon.setSetting('language',value)
    xbmc.executebuiltin('XBMC.Container.Refresh')      
    
elif mode[0] == 'Opcje':
    my_addon.openSettings()   

elif mode[0] == '__page__M':
    url = build_url({'mode': 'ListMovies', 'foldername': '', 'ex_link' : ex_link ,'page':page})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)
elif mode[0] == '__page__S':
    url = build_url({'mode': 'ListTVShows', 'foldername': '','ex_link' : ex_link ,'page':page})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)


elif mode[0] == 'ListMovies':
    data=linkdata(quality,language,sort,genre)     
    ListMovies(ex_link+data)

elif mode[0] == 'ListTVShows':
    data=linkdata(quality=None,language=None,sort=sortT,gener=genreT)
    ListTVShows(ex_link)
    
elif mode[0] == 'ListEpisodes':
    ListEpisodes(ex_link)

elif mode[0] == 'getLinks':
    getLinks(ex_link)

elif mode[0] == 'ListSearch':
    ListSearch(ex_link)

elif mode[0] =='Szukaj':
    addDir('[COLOR green]'+slan("New Search")+'[/COLOR]',ex_link,mode='SzukajNowe')
    historia = HistoryLoad()
    if not historia == ['']:
        for entry in historia:
            contextmenu = []
            contextmenu.append((slan("Remove"), 'XBMC.Container.Refresh(%s)'% build_url({'mode': 'SzukajUsun', 'foldername' : entry,'ex_link': ex_link})),)
            contextmenu.append((slan("Remove all"), 'XBMC.Container.Update(%s)' % build_url({'mode': 'SzukajUsunAll','ex_link': ex_link})),)
            addDir(name=entry, ex_link=ex_link%urllib.quote_plus(entry), mode='ListSearch', page=1, fanart=None, contextmenu=contextmenu) 

        
elif mode[0] =='SzukajNowe':
    d = xbmcgui.Dialog().input(slan("Search, type movie title"), type=xbmcgui.INPUT_ALPHANUM)
    if d:
        HistoryAdd(d)
        print ex_link%urllib.quote_plus(d)
        ListSearch(ex_link%urllib.quote_plus(d))

elif mode[0] =='SzukajUsun':
    HistoryDel(fname)
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'%  build_url({'mode': 'Szukaj','ex_link': ex_link}))

elif mode[0] == 'SzukajUsunAll':
    HistoryClear()
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'%  build_url({'mode': 'Szukaj','ex_link': ex_link}))

elif mode[0] == 'folder':
    pass

else:
    xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=''))        


xbmcplugin.endOfDirectory(addon_handle)

