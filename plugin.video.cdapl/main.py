# -*- coding: utf-8 -*-
import sys,re,os
import urllib,urllib2
import urlparse
import xbmc,xbmcgui,xbmcaddon
import xbmcplugin
import json 

from resources.lib import cdapl as cda
from resources.lib import filmwebapi as fa


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
    
def addLinkItem(name, url, mode, iconimage=None, infoLabels=False, IsPlayable=False,fanart=None,totalItems=1):
    u = build_url({'mode': mode, 'foldername': name, 'ex_link' : url})
    #u = urllib.urlencode(encoded_dict({'mode': mode, 'foldername': name, 'ex_link' : url}))
    if iconimage==None:
        iconimage='DefaultFolder.png'
    liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    
    if not infoLabels:
        infoLabels={"title": name}
    liz.setInfo(type="video", infoLabels=infoLabels)
    liz.setContentLookup(False)
    if IsPlayable:
        liz.setProperty('IsPlayable', 'True')
    if fanart:
        liz.setProperty('fanart_image',fanart)
    contextMenuItems = []
    contextMenuItems.append(('Informacja', 'XBMC.Action(Info)'))
    liz.addContextMenuItems(contextMenuItems, replaceItems=False)           
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz,isFolder=False,totalItems=totalItems)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED, label2Mask = "%D, %P, %R")
    return ok

def addDir(name,ex_link=None,json_file='', mode='walk',iconImage='DefaultFolder.png',fanart='',totalItems=1,contextmenu=None):
    url = build_url({'mode': mode, 'foldername': name, 'ex_link' : ex_link, 'json_file' : json_file})
    #li = xbmcgui.ListItem(name.encode("utf-8"), iconImage=iconImage)
    li = xbmcgui.ListItem(name, iconImage=iconImage)
    if fanart:
        li.setProperty('fanart_image', fanart )
    if contextmenu:
        contextMenuItems=contextmenu
        li.addContextMenuItems(contextMenuItems, replaceItems=True)         
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)


def setView():
    if my_addon.getSetting('auto-view') == 'true':
        view_mode = my_addon.getSetting('view_mode')
        view_modes = {
            '0': '502',  # List
            '1': '51',   # Big List
            '2': '500',  # Thumbnails
            '3': '501',  # Poster Wrap
            '4': '508',  # Fanart
            '5': '504',  # Media info
            '6': '503',  # Media info 2
            '7': '515'   # Media info 3
        }
        xbmc.executebuiltin('Container.SetViewMode(%s)' % view_modes[view_mode])

    xbmcplugin.addSortMethod( handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
    xbmcplugin.addSortMethod( handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL )
    xbmcplugin.addSortMethod( handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING )
    xbmcplugin.addSortMethod( handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_DATE )
    xbmcplugin.addSortMethod( handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
    xbmcplugin.addSortMethod( handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_GENRE )


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
    

def updateMetadata(item,use_filmweb=True):
    if use_filmweb=='true':
        title_org = item.get('title')
        title,year=cda.cleanTitle(title_org)
        data = fa.searchFilmweb(title.strip(),year.strip())
        if data:
            item.update(data)
            item['OriginalTitle']=title_org
            item['title']=u'%s (%d)' %(data.get('title'),data.get('year',''))
    return item


## COMMON Functions

def decodeVideo(ex_link):
    stream_url = cda.getVideoUrls(ex_link)
    if type(stream_url) is list:
        qualityList = [x[0] for x in stream_url]
        selection = xbmcgui.Dialog().select("Quality [can be set default]", qualityList)
        if selection>-1:
            stream_url = cda.getVideoUrls(stream_url[selection][1],4)
        else:
            stream_url=''
    print stream_url    
    
    if stream_url:
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))

def playVideoRemote(ex_link):
    xbmcgui.Dialog().notification('Remote video requested', ex_link , xbmcgui.NOTIFICATION_INFO, 5000)
    stream_url = cda.getVideoUrls(ex_link)
    if type(stream_url) is list:
        qualityList = [x[0] for x in stream_url]
        selection = xbmcgui.Dialog().select("Quality [can be set default]", qualityList)
        if selection>-1:
            stream_url = cda.getVideoUrls(stream_url[selection][1],4)
        else:
            stream_url=''
    
    if not stream_url:
        return False
        
    liz=xbmcgui.ListItem('Remote video')
    liz.setInfo( type="Video", infoLabels={ "Title": 'Remote video', } )
    try:
        # videoList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        # videoList.clear()
        # videoList.add(stream_url)
        # xbmc.Player().play(videoList)
        xbmcPlayer = xbmc.Player()
        xbmcPlayer.play(stream_url, liz)
        #xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
    except Exception as ex:
        xbmcgui.Dialog().ok('Problem z odtworzeniem.', 'Wystąpił nieznany błąd', str(ex))

    return 1
        


def mainWalk(ex_link,json_file):
    items=[]
    folders=[]
    print ex_link 
    if ex_link=='' or ex_link.startswith('/'):       #jsonWalk
        data = cda.ReadJsonFile(json_file)
        items,folders = cda.jsconWalk(data,ex_link)
    if 'folder' in ex_link:                        
        items,folders = cda.get_UserFolder_content( 
                                urlF        = ex_link,
                                recursive   = True,
                                filtr_items = {} )
    N_folders=len(items)
    for f in folders:
        tmp_json_file = f.get('jsonfile',json_file) # use new json file
        addDir(f.get('title'),ex_link=f.get('url'), json_file=tmp_json_file, mode='walk', iconImage=f.get('img',''),fanart=f.get('fanart',''),totalItems=N_folders)
    N_items=len(items)
    for item in items:
        addLinkItem(name=item.get('title').encode("utf-8"), url=item.get('url'), mode='decodeVideo', iconimage=item.get('img'), infoLabels=item, IsPlayable=False,fanart=item.get('img'),totalItems=N_items)
    
    if N_folders : setView()
    return 1

## MAIN LOOP 
   
xbmcplugin.setContent(addon_handle, 'movies')	

mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]
json_file = args.get('json_file',[''])[0]

if mode is None:
    mainWalk("",os.path.join(PATH,'root.json'))
    addDir('[COLOR blue]Filmy HD Lektor | Dubbing[/COLOR]',ex_link=u'http://www.cda.pl/video/show/film_lektor_pl_dubbing/p1?duration=dlugie&section=&quality=720p&section=&s=date&section=', mode='cdaSearch')
    addDir('[COLOR blue]Serial HD Lektor | Dubbing[/COLOR]',ex_link=u'http://www.cda.pl/video/show/serial_lektor_pl_dubbing/p1?duration=srednie&section=&quality=720p&section=&s=date&section=', mode='cdaSearch')
    addDir('[COLOR blue]Szukaj[/COLOR]',ex_link='', mode='cdaSearch')
    addLinkItem('[COLOR blue]-=Opcje=-[/COLOR]','','Opcje')
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True)
    

elif mode[0]=='cdaSearch':
    if not ex_link:
        use_filmweb = my_addon.getSetting('filmweb_search')
        d = xbmcgui.Dialog().input('Szukaj, Podaj tytul', type=xbmcgui.INPUT_ALPHANUM)
        if d:
            ex_link='http://www.cda.pl/video/show/'+d.replace(' ','_')
    elif 'serial_' in ex_link:
        use_filmweb=my_addon.getSetting('filmweb_serial')
    elif 'film_' in ex_link:
        use_filmweb=my_addon.getSetting('filmweb_film')
    
    items,nextpage = cda.searchCDA(ex_link)
    N_items=len(items)
    if items:
        for item in items:
            item=updateMetadata(item,use_filmweb)
            addLinkItem(name=item.get('title').encode("utf-8"), url=item.get('url'), mode='decodeVideo', iconimage=item.get('img'), infoLabels=item, IsPlayable=False,fanart=item.get('img'),totalItems=N_items)
        if nextpage:
            addDir('[COLOR green]Następna strona >> [/COLOR] ',ex_link=nextpage, mode='cdaSearch')
        setView()
    x=xbmcplugin.endOfDirectory(addon_handle,succeeded=True)
    

elif mode[0] == 'decodeVideo':
    decodeVideo(ex_link)

elif mode[0] == 'play':
    playVideoRemote(ex_link)

elif mode[0] == 'Opcje':
    my_addon.openSettings()   

elif mode[0] == 'walk':
    mainWalk(ex_link,json_file) 
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True)

    
elif mode[0] == 'folder':
    pass
   

# <category label="Jakość vioeo" >
#     <setting label="nie działa" type="lsep"/>
#     <setting id="auto_select" type="enum" label="Wybieraj jakość filmu" entries="0|1" values="ręcznie|automatycznie" default="0"/>
#     <setting id="resolution" type="labelenum" label=" jakość filmu do:" subsetting="true" visible="eq(-1,1)" values="najlepsza|360p|480p|720p|1080p" default="najlepsza" />
# </category>
 