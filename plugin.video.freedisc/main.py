# -*- coding: utf-8 -*-

import sys,re,os
import urllib,urllib2
import urlparse
import xbmc,xbmcgui,xbmcaddon
import xbmcplugin
import json, htmlentitydefs

try:
   import StorageServer
except:
   import storageserverdummy as StorageServer
cache = StorageServer.StorageServer("freedisk")


import resources.lib.freedisc as freedisc


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

FAVORITE    = os.path.join(DATAPATH,'favorites.json')


## COMMON Functions
def getUrl(url,data=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link
    
def addLinkItem(name, url, mode, page=1, iconimage=None, infoLabels=False, contextO=['F_ADD'], IsPlayable=True,fanart=FANART,itemcount=1):
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
    
    content=urllib.quote_plus(json.dumps(infoLabels))
    if 'F_ADD' in contextO:
        contextMenuItems.append(('[COLOR green]Dodaj do Wybranych[/COLOR]', 'RunPlugin(plugin://%s?mode=favoritesADD&ex_link=%s)'%(my_addon_id,content)))
    if 'F_REM' in contextO:
        contextMenuItems.append(('[COLOR red]Usuń z Wybranych[/COLOR]', 'RunPlugin(plugin://%s?mode=favoritesREM&ex_link=%s)'%(my_addon_id,content)))
    if 'F_DEL' in contextO:
        contextMenuItems.append(('[COLOR red]Usuń Wszystko[/COLOR]', 'RunPlugin(plugin://%s?mode=favoritesREM&ex_link=all)'%(my_addon_id)))
    
    liz.addContextMenuItems(contextMenuItems, replaceItems=False)        
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz,isFolder=False,totalItems=itemcount)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%R, %Y, %P")
    return ok

def addDir(name,ex_link=None, page=1, mode='folder',iconImage='DefaultFolder.png', infoLabels=None, fanart=FANART, contextO=['F_ADD'], contextmenu=None):
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
        
        content=urllib.quote_plus(json.dumps(infoLabels))
        if 'F_ADD' in contextO:
            contextMenuItems.append(('[COLOR green]Dodaj do Wybranych[/COLOR]', 'RunPlugin(plugin://%s?mode=favoritesADD&ex_link=%s)'%(my_addon_id,content)))
        if 'F_REM' in contextO:
            contextMenuItems.append(('[COLOR red]Usuń z Wybranych[/COLOR]', 'RunPlugin(plugin://%s?mode=favoritesREM&ex_link=%s)'%(my_addon_id,content)))
        if 'F_DEL' in contextO:
            contextMenuItems.append(('[COLOR red]Usuń Wszystko[/COLOR]', 'RunPlugin(plugin://%s?mode=favoritesREM&ex_link=all)'%(my_addon_id)))
        
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



def html_entity_decode_char(m):
    ent = m.group(1)
    if ent.startswith('x'):
        return unichr(int(ent[1:],16))
    try:
        return unichr(int(ent))
    except Exception, exception:
        if ent in htmlentitydefs.name2codepoint:
            return unichr(htmlentitydefs.name2codepoint[ent])
        else:
            return ent

def html_entity_decode(string):
    string = string.decode('UTF-8')
    s = re.compile("&#?(\w+?);").sub(html_entity_decode_char, string)
    return s.encode('UTF-8')
    
def ReadJsonFile(jfilename):
    content = '[]'
    if os.path.exists(jfilename):    # local content
        with open(jfilename,'r') as f:
            content = f.read()
            if not content:
                content ='[]'
    data=json.loads(html_entity_decode(content))

    return data

## sub functions
    

def ListMovies(ex_link):
    if ex_link=='FAVORITE':
        items = ReadJsonFile(FAVORITE)
    elif ex_link.startswith('search'):
        items=freedisc.search(ex_link.split('|')[-1].strip())
    else:
        # print '$$$$$$$$$$$$$$$$$$$$$$$$$',ex_link
        items = freedisc.scanUser(ex_link)
   
    contextO=['F_ADD']
    if fname=='[COLOR khaki]Wybrane[/COLOR]':
        contextO=['F_REM','F_DEL']

            
    for item in items:
        if item.get('folder'):
            addDir(name=item.get('title',''),ex_link=item.get('href'), mode='ListMovies',iconImage=item.get('img'),infoLabels=item,contextO=contextO)
        else:
            addLinkItem(name=item.get('title'), url=item.get('href'), mode='getLinks', iconimage=item.get('img'), infoLabels=item, contextO=contextO, IsPlayable=True)
    

def getLinks(ex_link):
    stream_url = freedisc.getVideoUrls(ex_link)
    #print stream_url
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
            
    
xbmcplugin.setContent(addon_handle, 'video')	


mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]
page = args.get('page',[1])[0]

if mode is None:
    addDir(name="[COLOR blue]Ranking freedisc.pl (7dni)[/COLOR]",ex_link='http://freedisc.pl/ranking/week', mode='ListMovies',iconImage='DefaultFolder.png',fanart=FANART)
    addDir('[COLOR khaki]Wybrane[/COLOR]',ex_link='FAVORITE', mode='ListMovies',  iconImage='DefaultFolder.png',fanart=FANART)
    addDir('[COLOR green]Szukaj[/COLOR]','',mode='Szukaj')


elif mode[0] == '__page__M':
    url = build_url({'mode': 'ListMovies', 'foldername': '', 'ex_link' : ex_link})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)
    

elif mode[0] == 'ListMovies':
    ListMovies(ex_link)

elif mode[0] == 'getLinks':
    getLinks(ex_link)

elif mode[0] == 'Opcje':
    my_addon.openSettings()   


elif mode[0] == 'favoritesADD':
    jdata = ReadJsonFile(FAVORITE)
    new_item=json.loads(ex_link)
    # fix label/msg from title
    new_item['title'] = new_item.get('title','').replace(new_item.get('label',''),'').replace(new_item.get('msg',''),'')
    dodac = [x for x in jdata if new_item['title']== x.get('title','')]
    if dodac:
        xbmc.executebuiltin('Notification([COLOR pink]Już jest w Wybranych[/COLOR], ' + new_item.get('title','').encode('utf-8') + ', 200)')
    else:
        jdata.append(new_item)
        if not os.path.exists(FAVORITE):
            os.makedirs(os.path.dirname(FAVORITE))
        with open(FAVORITE, 'w') as outfile:
            json.dump(jdata, outfile, indent=2, sort_keys=True)
            xbmc.executebuiltin('Notification(Dodano Do Wybranych, ' + new_item.get('title','').encode('utf-8') + ', 200)')

elif mode[0] == 'favoritesREM':
    if ex_link=='all':
        yes = xbmcgui.Dialog().yesno("??","Usuń wszystkie filmy z Wybranych?")
        if yes:
            os.remove(FAVORITE)
    else:
        jdata = ReadJsonFile(FAVORITE)
        remItem=json.loads(ex_link)
        to_remove=[] 
        for i in xrange(len(jdata)):
            if jdata[i].get('title') in remItem.get('title'):
                to_remove.append(i)
        if len(to_remove)>1:
            yes = xbmcgui.Dialog().yesno("??",remItem.get('title'),"Usuń %d pozycji z Wybranych?" % len(to_remove))
        else:
            yes = True
        if yes:
            for i in reversed(to_remove):
                jdata.pop(i)
            with open(FAVORITE, 'w') as outfile:
                json.dump(jdata, outfile, indent=2, sort_keys=True)
    xbmc.executebuiltin('XBMC.Container.Refresh')  

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
    d = xbmcgui.Dialog().input('Szukaj, Podaj tytuł', type=xbmcgui.INPUT_ALPHANUM)
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

