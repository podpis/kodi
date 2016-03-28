# -*- coding: utf-8 -*-

import sys,os,re
import urllib,urllib2
import urlparse
import xbmc,xbmcgui,xbmcaddon
import xbmcplugin
import urlresolver


import resources.lib.naszeKinoEu as nk
import resources.lib.cdaresolver as cdaresolver

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


def ChooseAndPlay(ex_link,kat=''):
    data = nk.get_movie_links(ex_link)
    if len(data.keys())==1:
        hosts,links = nk.host_link(data.values()[0])
    elif kat and kat in data.keys():
        hosts,links = nk.host_link(data[kat])
    else:
        dialog = xbmcgui.Dialog()
        selection = dialog.select('Odcinki:', data.keys())
        if selection>-1: 
            hosts,links = nk.host_link(data[data.keys()[selection]])
        else:
            return False
            
    dialog = xbmcgui.Dialog()
    ret = dialog.select('Choose a source', hosts)
    if ret>-1:
        if 'cda' in hosts[ret]:
            print 'CDA'
            stream_url = cdaresolver.getVideoUrls(links[ret])
            if type(stream_url) is list:
                qualityList = [x[0] for x in stream_url]
                selection = xbmcgui.Dialog().select("Quality [can be set default]", qualityList)
                if selection>-1:
                    stream_url = cdaresolver.getVideoUrls(stream_url[selection][1])
                else:
                    stream_url=''
        else:        
            stream_url = urlresolver.resolve(links[ret])
        
        if stream_url:
            xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
        else:
            xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=stream_url))
            
def ShowLinks(ex_link):
    out = nk.get_movie_links(ex_link)
    items = sorted(out.keys(),key=nk.natural_keys)
    for item in items:
        addLinkItem(name=item.encode('utf-8'),url=ex_link,kat=item.encode('utf-8'),mode='ChooseAndPlay')
    

def addLinkItem(name, url, mode, iconimage=None, infoLabels={}, IsPlayable=True, isFolder=False, fanart=None, kat='',wer='',page='1'):
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
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz, isFolder=isFolder)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%Y,%P")
    return ok

def addFilmLinks(kat,wer,page,ex_link):
    pozycje = nk.get_movie_relative(ex_link,page)
    if int(page)>1:
        addLinkItem('[COLOR gold]<< Poprzednia Strona %d <<[/COLOR]' %(int(page)-1), url=ex_link , mode='__page__', kat=kat,wer=wer,page= int(page)-1, IsPlayable=False)
    for p in pozycje:
        if kat=='serial' or re.search('serial|tv-show|sezon',p.get('title','')):
            addLinkItem(name=p.get('title','').encode('utf-8'),url=p.get('url',''),mode='ShowLinks',isFolder=True,iconimage=p['img'],infoLabels=p,fanart=p['img'])
        else:
            addLinkItem(name=p.get('title','').encode('utf-8'),url=p.get('url',''),mode='ChooseAndPlay',iconimage=p['img'],infoLabels=p,fanart=p['img'])
        
    if len(pozycje)>25:
        addLinkItem('[COLOR gold]>> Nastepna Strona %d >>[/COLOR]' %(int(page)+1), url=ex_link , mode='__page__', kat=kat,wer=wer,page= int(page)+1, IsPlayable=False)

 
xbmcplugin.setContent(addon_handle, 'movies')	

mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]
kat = args.get('kat',[''])[0]
wer = args.get('wer',[''])[0]
page = args.get('page',[''])[0]


if mode is None:
    addDir('[COLOR blue]Polecane Filmy[/COLOR]')
    addDir('[COLOR blue]Ostatnio dodane odcinki seriali[/COLOR]')
    
    addDir('Bajki',ex_link='http://nasze-kino.eu/gatunek/18/-bajki-/1')
    addDir('Filmy',ex_link='http://nasze-kino.eu/gatunek/46/-filmy-/1')
    addDir('Seriale',kat='serial',ex_link='http://nasze-kino.eu/gatunek/45/-seriale-/1')
    addDir('Stare-Kino',ex_link='http://nasze-kino.eu/gatunek/62/-stare-kino-/1')
    addDir('TV-Shows',kat='serial',ex_link='http://nasze-kino.eu/gatunek/25/-tv-shows-/1')

    addDir('[COLOR green]GATUNEK[/COLOR]')
    addDir('[COLOR green]JAKOŚĆ[/COLOR]')
    addDir('[COLOR green]WERSJA[/COLOR]')
    #addDir('[COLOR green]Szukaj[/COLOR]','')
    #url = build_url({'mode': 'Opcje'})
    #li = xbmcgui.ListItem(label = '-=Opcje=-', iconImage='DefaultScript.png')
    #xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li)

elif mode[0] == '__page__':
    url = build_url({'mode': 'folder', 'foldername': '', 'ex_link' : ex_link,'kat' : kat,'wer' : wer,'page' : page})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)


elif mode[0] == 'ChooseAndPlay':
    ChooseAndPlay(ex_link,kat)

elif mode[0] == 'ShowLinks':
    ShowLinks(ex_link)
    
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
    elif fname=='[COLOR blue]Polecane Filmy[/COLOR]':
        pozycje = nk.polecane_filmy()
        for p in pozycje:
            addLinkItem(name=p.get('title','').encode('utf-8'),url=p.get('url',''),mode='ChooseAndPlay',iconimage=p.get('img',''),infoLabels=p,fanart=p.get('img',''))
    elif fname=='[COLOR blue]Ostatnio dodane odcinki seriali[/COLOR]':
        pozycje = nk.ostatnio_dodane_seriale()
        for p in pozycje:
            addLinkItem(name=p.get('title','').encode('utf-8'),url=p.get('url',''),mode='ShowLinks',isFolder=True, iconimage=p.get('img',''),infoLabels=p,fanart=p.get('img',''))
    elif fname=='[COLOR green]GATUNEK[/COLOR]':
        data = nk.header()
        for one in data['gatunek']:
            addDir(one.get('title').encode('utf-8'),ex_link=one.get('url'))
    elif fname=='[COLOR green]JAKOŚĆ[/COLOR]':
        data = nk.header()
        for one in data['jakosc']:
            addDir(one.get('title').encode('utf-8'),ex_link=one.get('url'))
    elif fname=='[COLOR green]WERSJA[/COLOR]':
        data = nk.header()
        for one in data['wersja']:
            addDir(one.get('title').encode('utf-8'),ex_link=one.get('url'))            
    elif ex_link:
        addFilmLinks(kat,wer,page,ex_link)
        


xbmcplugin.endOfDirectory(addon_handle)