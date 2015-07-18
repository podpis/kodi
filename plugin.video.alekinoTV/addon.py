import sys
import urllib,urllib2
import urlparse
import xbmc,xbmcgui,xbmcaddon
import xbmcplugin

import alekinoTv as AK

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
my_addon = xbmcaddon.Addon()

def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

def addDir(name,ex_link=None,iconImage='DefaultFolder.png'):
    url = build_url({'mode': 'folder', 'foldername': name, 'ex_link' : ex_link})
    li = xbmcgui.ListItem(name, iconImage=iconImage)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def addLinkItem(name, url, mode, iconimage=None, infoLabels=False, IsPlayable=True):
    u = build_url({'mode': mode, 'foldername': name, 'ex_link' : url})
    if iconimage==None:
        iconimage='DefaultFolder.png'
    liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    if not infoLabels:
        infoLabels={"Title": name}
    liz.setInfo(type="Video", infoLabels=infoLabels)
    if IsPlayable:
        liz.setProperty('IsPlayable', 'true')
    #liz.setProperty('fanart_image',fanart)
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz)
    return ok



#-------------------------------------------	
    
def filtr_FilmyHD():
    if my_addon.getSetting('filmy_hd')=='true':
        return '/hd'
    else:
        return ''
        
def filtr_Filmy(default=''):
    filtr=[]    
    if default:
        filtr.append(default)
    if my_addon.getSetting('filmy_hd')=='true':
        filtr.append('quality%5B0%5D=hd')         
    if my_addon.getSetting('filmy_lektor')=='true':
        filtr.append('types%5B0%5D=1')
    if my_addon.getSetting('filmy_dubbing')=='true':
        filtr.append('types%5B0%5D=2')
    if my_addon.getSetting('filmy_napisy')=='true':
        filtr.append('types%5B0%5D=3')
    if my_addon.getSetting('filmy_polskie')=='true':
        filtr.append('types%5B0%5D=4')    
    if my_addon.getSetting('filmy_eng')=='true':
        filtr.append('types%5B0%5D=5')
    return '&'.join(filtr)
 
xbmcplugin.setContent(addon_handle, 'movies')	

mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]


FILTR_FILMY = filtr_Filmy()
FILTR_FILMY_JUNIOR = filtr_Filmy('genres[0]=49')
FILMY_HD = filtr_FilmyHD()

en_exlink = lambda a,b,c: '%s|%s|%d' % (a,b,c)
de_exlink = lambda x: x.split('|')


def addFilmyContent(ex_link):
    (subpage,filtr,page)= ex_link.split('|')
    #dialog = xbmcgui.Dialog()
    #d = dialog.ok('filtr', ex_link)
    Items = AK.listItemsFilmy(subpage,filtr,page)
    if int(page)>1:
       addLinkItem('<< Poprzednia  Strona %d <<' %(int(page)-1), en_exlink(subpage,filtr,int(page)-1), '__page__', IsPlayable=False)
    for k in Items:
        addLinkItem(k.get('Title','').title() , k.get('href',''), 'play',k.get('img',''), infoLabels=k)
    addLinkItem('>> Nastepna Strona %d >>' %(int(page)+1), en_exlink(subpage,filtr,int(page)+1), '__page__', IsPlayable=False)
    
if mode is None:

    addDir('Filmy',         '/filmy%s|%s|1' %(FILMY_HD,FILTR_FILMY) )          #subpage|filtr|page
    addDir('Filmy Junior',  '/filmy%s|%s|1' %(FILMY_HD,FILTR_FILMY_JUNIOR) )   #subpage|filtr|page
    addDir('Filmy (kategorie)')
    addDir('Szukaj','')
    url = build_url({'mode': 'Opcje'})
    li = xbmcgui.ListItem(label = '-=Opcje=-', iconImage='DefaultScript.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li)

elif mode[0] == '__page__':
    url = build_url({'mode': 'folder', 'foldername': '', 'ex_link' : ex_link})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)

elif mode[0] =='play':
    url = AK.getVidoLink(ex_link)
    if url:
        listitem = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem) 
    else:
        dialog = xbmcgui.Dialog()
        d = dialog.ok('ERROR', 'Brak filmu? sprawdz:', 'alekino.tv%s'%ex_link)

elif mode[0] == 'Opcje':
    my_addon.openSettings()

elif mode[0] == 'folder':
    if fname == 'Szukaj':
        dialog = xbmcgui.Dialog()
        d = dialog.input('Szukaj, Podaj tytul filmu', type=xbmcgui.INPUT_ALPHANUM)
        Items=AK.alekinoSzukaj(d.replace(' ','%20'))
        for k in Items:
            addLinkItem(k.get('Title','').title() , k.get('href',''), 'play',k.get('img',''), infoLabels=k)
        #addFilmLinks(link)
    elif fname == 'Filmy (kategorie)':
        Items=AK.filmyKategorie(subpage="/filmy")
        for k in Items:
            tmp_filtr_filmy = filtr_Filmy(k.get('Filtr',''))
            addDir(k.get('Title',''),         '/filmy%s|%s|1' %(FILMY_HD,tmp_filtr_filmy) )
    else:
       addFilmyContent(ex_link)
    

xbmcplugin.endOfDirectory(addon_handle)