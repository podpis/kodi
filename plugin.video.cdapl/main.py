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
MEDIA       = RESOURCES+'/media/'


## COMMON Functions
def getUrl(url,data=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link
    
def addLinkItem(name, url, mode, iconImage=None, infoLabels=False, IsPlayable=False,fanart=None,totalItems=1):
    u = build_url({'mode': mode, 'foldername': name, 'ex_link' : url})
    #u = urllib.urlencode(encoded_dict({'mode': mode, 'foldername': name, 'ex_link' : url}))
    if iconImage==None:
        iconImage='DefaultFolder.png'
    liz = xbmcgui.ListItem(name, iconImage=iconImage, thumbnailImage=iconImage)
    
    if not infoLabels:
        infoLabels={"title": name}
    liz.setInfo(type="video", infoLabels=infoLabels)
    #liz.setContentLookup(False)
    if IsPlayable:
        liz.setProperty('IsPlayable', 'True')
    if fanart:
        liz.setProperty('fanart_image',fanart)
    liz.setProperty('mimetype', 'video/x-msvideo')
    contextMenuItems = []
    contextMenuItems.append(('Informacja', 'XBMC.Action(Info)'))
    if infoLabels.has_key('trailer'):
        contextMenuItems.append(('Zwiastun', 'XBMC.PlayMedia(%s)'%infoLabels.get('trailer')))
        
    liz.addContextMenuItems(contextMenuItems, replaceItems=False)           
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz,isFolder=False,totalItems=totalItems)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED, label2Mask = "%D, %P, %R")
    return ok

def addDir(name,ex_link=None,json_file='', mode='walk',iconImage=None,fanart='',infoLabels=False,totalItems=1,contextmenu=None):
    url = build_url({'mode': mode, 'foldername': name, 'ex_link' : ex_link, 'json_file' : json_file})
    #li = xbmcgui.ListItem(name.encode("utf-8"), iconImage=iconImage)
    #MEDIA
    li = xbmcgui.ListItem(label=name,iconImage='DefaultFolder.png')
    if iconImage==None:
        iconImage='DefaultFolder.png'
    elif not iconImage.startswith('http'):  # local source
         iconImage = MEDIA + iconImage
    li = xbmcgui.ListItem(name, iconImage=iconImage, thumbnailImage=iconImage)

    if not infoLabels:
       infoLabels={"title": name}

    li.setInfo(type="Video", infoLabels=infoLabels)
    
    if fanart:
        li.setProperty('fanart_image', fanart )
    if contextmenu:
        contextMenuItems=contextmenu
        li.addContextMenuItems(contextMenuItems, replaceItems=True)    
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_DATE, label2Mask = "%D, %P, %R")
    return ok


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
    xbmcplugin.addSortMethod( handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE )
    xbmcplugin.addSortMethod( handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING )
    xbmcplugin.addSortMethod( handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR  )
    xbmcplugin.addSortMethod( handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_GENRE )
    xbmcplugin.addSortMethod( handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_STUDIO  )
    xbmcplugin.addSortMethod( handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )


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
        title,year,label=cda.cleanTitle(title_org)
        data = fa.searchFilmweb(title.strip(),year.strip())
        if data:
            item.update(data)
            item['OriginalTitle']=title_org
            if label:
                item['label']=label
            item['title'] += item.get('label','')+ item.get('msg','')
    return item

    

## COMMON Functions

def selectQuality(stream_url,quality):
    msg = u'Wybierz jakość video [albo ustaw automat w opcjach]'
    stream_selected=''
    if type(stream_url) is list:
        qualityList = [x[0] for x in stream_url]
        if quality > 0:
            user_selection = ['','Najlepsza','1080p','720p','480p','360p'][quality]
            if user_selection=='Najlepsza':
                stream_selected = cda.getVideoUrls(stream_url[0][1],4)  # najepsza - pierwszy link
            elif user_selection in qualityList:
                stream_selected = cda.getVideoUrls(stream_url[qualityList.index(user_selection)][1],4)
            else:
                msg = u'Problem z automatycznym wyborem ... wybierz jakosc'
            
        if not stream_selected:    
            selection = xbmcgui.Dialog().select(msg, qualityList)
            if selection>-1:
                stream_selected = cda.getVideoUrls(stream_url[selection][1],4)
            else:
                stream_selected=''
    else:
        stream_selected = stream_url
    return stream_selected
  

def decodeVideo(ex_link):
    stream_url = cda.getVideoUrls(ex_link)
    quality = my_addon.getSetting('quality')
    stream_url = selectQuality(stream_url,int(quality))
    print '$'*10
    print stream_url
    if stream_url:
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))

def playVideoRemote(ex_link):
    xbmcgui.Dialog().notification('Remote video requested', ex_link , xbmcgui.NOTIFICATION_INFO, 5000)
    stream_url = cda.getVideoUrls(ex_link)
    
    quality = my_addon.getSetting('quality_remote')
    stream_url = selectQuality(stream_url,int(quality))
    
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
    
## USER FOLDERS        

def userFolder(userF='K1'):
    enabled = my_addon.getSetting(userF)
    if enabled=='true':
        title = my_addon.getSetting(userF+'_filtr0')
        
        list_of_special_chars = [
        ('Ą', b'a'),
        ('ą', b'a'),
        ('Ę', b'e'),
        ('ę', b'e'),
        ('Ó', b'o'),
        ('ó', b'o'),
        ('Ć', b'c'),
        ('ć', b'c'),
        ('Ł', b'l'),
        ('ł', b'l'),
        ('Ń', b'n'),
        ('ń', b'n'),
        ('Ś', b's'),
        ('ś', b's'),
        ('Ź', b'z'),
        ('ź', b'z'),
        ('Ż', b'z'),
        ('ż', b'z'),
        (' ','_')]
        fraza = title
        for a,b in list_of_special_chars:
            fraza = fraza.replace(a,b)
        fraza = fraza.lower()
        
        sel = my_addon.getSetting(userF+'_filtr1')
        dlugoscL = ["all","krotkie","srednie","dlugie"]
        dlugosc = dlugoscL[int(sel)]

        sel = my_addon.getSetting(userF+'_filtr2')
        jakoscL = ["all","480p","720p","1080p"]
        jakosc= jakoscL[int(sel)]
        
        sel = my_addon.getSetting(userF+'_filtr3')
        sortujL=["best","date","popular","rate","alf"]
        sortuj=sortujL[int(sel)]
        
        filmweb = my_addon.getSetting(userF+'_fwmeta')

        url='http://www.cda.pl/video/show/%s?duration=%s&section=vid&quality=%s&section=&s=%s&section='%(fraza,dlugosc,jakosc,sortuj)
        return {'url':url,'title': '[COLOR blue]%s[/COLOR]'%title.title(),'metadata':filmweb }
    return False

def userFolderADD():
    folder_list=[]
    for userF in ['K1','K2','K3','K4','K5','K6']:
        one = userFolder(userF)
        if one:     # json_file zawiera info czy sciagac meta czy nie
            addDir(one.get('title'),ex_link=one.get('url'), mode='cdaSearch', json_file=one.get('metadata'),iconImage='Szukaj_cda.png')

def updateMetadata_filmwebID(item):
    if my_addon.getSetting('filmweb_isID')=='true' and item.get('filmweb',False):
        # sprawdz czy update jest wymagany:
        #if not item.get('img','') and not item.get('plot',''):
        data=fa.getFilmInfoFull(str(item.get('filmweb')))
        item.update(data)    
    item['title'] += item.get('label','')+ item.get('msg','')       # dodatkowe info gdy zdefiniowane
    return item
    

def mainWalk(ex_link,json_file):
    items=[]
    folders=[]
    #print ex_link 
    if ex_link=='' or ex_link.startswith('/'):       #jsonWalk
        data = cda.ReadJsonFile(json_file)
        items,folders = cda.jsconWalk(data,ex_link)
    if 'folder' in ex_link:                        
        items,folders = cda.get_UserFolder_content( 
                                urlF        = ex_link,
                                recursive   = True,
                                filtr_items = {} )
    elif 'obserwowani' in ex_link:
        items,folders = cda.get_UserFolder_obserwowani(ex_link)
    
    N_folders=len(items)
    for f in folders:
        tmp_json_file = f.get('jsonfile',json_file) # use new json file
        title = f.get('title') + f.get('count','') 
        f['plot'] = f.get('plot','') + '\n' + f.get('update','')
        addDir(title,ex_link=f.get('url'), json_file=tmp_json_file, mode='walk', iconImage=f.get('img',''),infoLabels=f,fanart=f.get('fanart',''),totalItems=N_folders)
    N_items=len(items)
    for item in items:
        item=updateMetadata_filmwebID(item)
        addLinkItem(name=item.get('title').encode("utf-8"), url=item.get('url'), mode='decodeVideo', iconImage=item.get('img'), infoLabels=item, IsPlayable=True,fanart=item.get('img'),totalItems=N_items)
    
    setView()
    return 1


def logincda():
    u = my_addon.getSetting('user')
    p = my_addon.getSetting('pass')
    if u and p:
        if cda.CDA_login(u,p,RESOURCES+'cookie.cda'):
            cda.COOKIEFILE=RESOURCES+'cookie.cda'
            addDir('[B]Moje cda.pl[/B]',ex_link='', json_file='', mode='MojeCDA', iconImage='cdaMoje.png',infoLabels=False)
       
if os.path.exists(RESOURCES+'cookie.cda'):
    cda.COOKIEFILE=RESOURCES+'cookie.cda'

## MAIN LOOP 
   
xbmcplugin.setContent(addon_handle, 'movies')	

mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]
json_file = args.get('json_file',[''])[0]

if mode is None:
    logincda()  # perform login
    mainWalk("",os.path.join(PATH,'root.json'))
    userFolderADD()
    addDir('[COLOR green]Szukaj[/COLOR]',ex_link='', mode='cdaSearch',iconImage='Szukaj_cda.png')
    addLinkItem('[COLOR gold]-=Opcje=-[/COLOR]','','Opcje',iconImage=MEDIA+'Opcje.png')
    
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True) #,cacheToDisc=True)
    

elif mode[0]=='cdaSearch':
    use_filmweb=json_file if json_file else 'false'
    if not ex_link:
        use_filmweb = my_addon.getSetting('filmweb_search')
        d = xbmcgui.Dialog().input('Szukaj, Podaj tytuł', type=xbmcgui.INPUT_ALPHANUM)
        if d:
            ex_link='http://www.cda.pl/video/show/'+d.replace(' ','_')

    items,nextpage = cda.searchCDA(ex_link)
    N_items=len(items)
    if items:
        for item in items:
            item=updateMetadata(item,use_filmweb)
            print item
            addLinkItem(name=item.get('title').encode("utf-8"), url=item.get('url'), mode='decodeVideo', iconImage=item.get('img'), infoLabels=item, IsPlayable=True,fanart=item.get('img'),totalItems=N_items)
        if nextpage:
            addDir('[COLOR gold]Następna strona >> [/COLOR] ',ex_link=nextpage, json_file=use_filmweb, mode='cdaSearch',iconImage='next.png')
    setView()
    x=xbmcplugin.endOfDirectory(addon_handle,succeeded=True)

elif mode[0] == 'MojeCDA':
    u = my_addon.getSetting('user')
    if u:
        addDir('Folder główny',ex_link='http://www.cda.pl/'+u+'/folder-glowny?type=pliki', json_file='', mode='walk', iconImage='cdaMoje.png')
        addDir('Ulubione',ex_link='http://www.cda.pl/'+u+'/ulubione/folder-glowny?type=pliki', json_file='', mode='walk', iconImage='cdaUlubione.png')
        addDir('Obserwowani @użytkownicy',ex_link='http://www.cda.pl/'+u+'/obserwowani', json_file='', mode='walk', iconImage='cdaObserwowani.png') 
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True) #,cacheToDisc=True)

elif mode[0] == 'decodeVideo':
    decodeVideo(ex_link)

elif mode[0] == 'play':
    playVideoRemote(ex_link)

elif mode[0] == 'Opcje':
    my_addon.openSettings()   
    xbmc.executebuiltin('XBMC.Container.Refresh()')

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
 