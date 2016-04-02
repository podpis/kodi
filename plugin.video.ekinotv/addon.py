import sys,os,re
import urllib,urllib2
import urlparse
import xbmc,xbmcgui,xbmcaddon
import xbmcplugin
import urlresolver



import ekino as EK

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
my_addon = xbmcaddon.Addon()



def addDir(name,kat='',wer='',page='1',ex_link=None,iconImage='DefaultFolder.png'):
    url = build_url({'mode': 'folder', 'foldername': name, 'ex_link' : ex_link,'kat' : kat,'wer' : wer,'page' : page})
    li = xbmcgui.ListItem(name, iconImage=iconImage)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)


def ChooseAndPlay(ex_link):
    (_Lables,_Links)=EK.get_sources(ex_link)
    if _Lables:
        dialog = xbmcgui.Dialog()
        ret = dialog.select('Choose a source', _Lables)
        if ret>-1:
            media_url = urlresolver.resolve(_Links[ret])
            print media_url
            listitem = xbmcgui.ListItem(path=media_url)
            xbmcplugin.setResolvedUrl(addon_handle, True, listitem)    


def addLinkItem(name, url, mode, iconimage=None, infoLabels={}, IsPlayable=True, fanart=None, kat='',wer='',page='1'):
    u = build_url({'mode': mode, 'foldername': name, 'ex_link' : url,'kat' : kat,'wer' : wer,'page' : page})
    if iconimage==None:
        iconimage='DefaultFolder.png'
    liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setLabel2(infoLabels.get('title2',''))
    if not infoLabels:
        infoLabels={"Title": name}
    liz.setInfo(type="Video", infoLabels=infoLabels)
    liz.setLabel2(infoLabels.get('code',''))
    if IsPlayable:
        liz.setProperty('IsPlayable', 'true')
    if fanart:
        liz.setProperty('fanart_image',fanart)
    contextMenuItems = []
    contextMenuItems.append(('Informacja', 'XBMC.Action(Info)'))
    liz.addContextMenuItems(contextMenuItems, replaceItems=False)     
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%Y,%P")
    return ok

def addFilmLinks(kat,wer,page,ex_link):
    pozycje= EK.skanuj_filmy(kat=kat,wer=wer, page=page,url=ex_link)
    if int(page)>1:
        addLinkItem('[COLOR gold]<< Poprzednia Strona %d <<[/COLOR]' %(int(page)-1), url=ex_link , mode='__page__', kat=kat,wer=wer,page= int(page)-1, IsPlayable=False)
    for p in pozycje:
        addLinkItem(name=p['title'],url=p['href'],mode='ChooseAndPlay',iconimage=p['img'],infoLabels=p,fanart=p['img'])
    
    addLinkItem('[COLOR gold]>> Nastepna Strona %d >>[/COLOR]' %(int(page)+1), url=ex_link , mode='__page__', kat=kat,wer=wer,page= int(page)+1, IsPlayable=False)


def testPlay(ex_link):
    if 'openload.co/stream' in ex_link:
        media_url=ex_link
    else:
        media_url = urlresolver.resolve(ex_link)

    print '==testPlay'
    print media_url
    if media_url:
        listitem = xbmcgui.ListItem(path=media_url)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
    
 
 
xbmcplugin.setContent(addon_handle, 'movies')	

mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]
kat = args.get('kat',[''])[0]
wer = args.get('wer',[''])[0]
page = args.get('page',[''])[0]

def get_WERSJE():
    _WERSJE=['Napisy','Lektor','Dubbing','ENG','PL']
    WERSJE=''
    for w in _WERSJE:
        if my_addon.getSetting(w)=='true':
            if WERSJE:
                WERSJE += ','
            WERSJE += w
    return WERSJE

WERSJE  = get_WERSJE()


if mode is None:
    addDir('[COLOR blue]Filmy[/COLOR]',kat='',wer=WERSJE)
    addDir('Filmy HD',kat='35',wer=WERSJE)
    addDir('Filmy Dla Dzieci HD',kat='2,3,5,6',wer=WERSJE)
    addDir('Filmy [Kategoria]',kat='',wer=WERSJE)
    #addDir('[COLOR blue]Seriale[/COLOR]',kat='',ex_link='http://ekino-tv.pl/serie/',wer='')
   
    addDir('[COLOR green]Szukaj[/COLOR]','')
    url = build_url({'mode': 'Opcje'})
    li = xbmcgui.ListItem(label = '-=Opcje=-', iconImage='DefaultScript.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li)

elif mode[0] == '__page__':
    url = build_url({'mode': 'folder', 'foldername': '', 'ex_link' : ex_link,'kat' : kat,'wer' : wer,'page' : page})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)

elif mode[0] == 'testPlay':
    testPlay(ex_link)  
elif mode[0] == 'ChooseAndPlay':
    print ex_link
    ChooseAndPlay(ex_link)
elif mode[0] == 'Opcje':
    my_addon.openSettings()
    url = build_url({'mode': '', 'foldername': '', 'ex_link' : '', 'page': 1})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)

elif mode[0] == 'folder':
    if 'Szukaj' in fname:
        dialog = xbmcgui.Dialog()
        d = dialog.input('Szukaj, Podaj tytul filmu', type=xbmcgui.INPUT_ALPHANUM)
        pozycje = EK.szukaj(d.replace(' ','%20'))
        print len(pozycje)
        for p in pozycje:
            addLinkItem(p['title'],p['href'],'ChooseAndPlay',p['img'],p)
    elif fname=='Filmy [Kategoria]':
        data = EK.getCategories()
        ret = xbmcgui.Dialog().select('Wybierz:', data[0])
        if ret>-1:
           addFilmLinks(data[1][ret],wer,page,ex_link) 
    elif ex_link.startswith('/series'):
        addSeriesSeasons(ex_link)
    elif ex_link:
        addFilmLinks(kat,wer,page,ex_link)
        


xbmcplugin.endOfDirectory(addon_handle)