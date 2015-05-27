import sys,os,re
import urllib,urllib2
import urlparse
import xbmc,xbmcgui,xbmcaddon
import xbmcplugin
import urlresolver
import json
from bs4 import BeautifulSoup
import base64

BASE_URL='http://seansik.tv'

LANG_TAB = {1: "Napisy",
            2: "Lektor",
            8: "Lektor IVO",
            3: "Dubbing",
            4: "PL",
            5: "ENG",
            6: "Japonski",
            7: "Oryginal",
            9: "Napisy eng"}

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


def ChooseAndPlay(ex_link):
    content = getUrl(BASE_URL+ex_link)
    idx0=content.find('window.video_mgr.setSasa(')
    idx1=content[idx0:].find('});')
    sasa=content[idx0:idx0+idx1]
    sasa=sasa.replace('window.video_mgr.setSasa(','')+'}'
    jfilmy = json.loads(sasa)
    soup=BeautifulSoup(content)
    translationList =soup.find_all('div',{'class':"translationList"})
    _Lables=[]
    _Links=[]
    for tlist in translationList:
        Lang_id=tlist.get('id').split('_')[-1]
        sources=tlist.find_all(style="cursor:pointer;")
        for s in sources:
            ok=1
            key = s.get('data-vid_key')
            label = LANG_TAB[int(Lang_id)].encode('utf-8')
            for span in s.find_all('span'):
                label = label + ' ' + span.get_text().encode('utf-8').strip()
            if key in jfilmy.keys():
                decoded = base64.b64decode(jfilmy[key])
                if decoded.startswith('http'):
                    src = decoded
                elif decoded.startswith('<iframe'):
                    src = BeautifulSoup(base64.b64decode(jfilmy[key])).iframe.get('src')
                else:
                    ok=0
                if ok:
                    _Lables.append(label)    
                    _Links.append(src)
    dialog = xbmcgui.Dialog()
    ret = dialog.select('Choose a playlist', _Lables)
    if ret>-1:
        media_url = urlresolver.resolve(_Links[ret])
        listitem = xbmcgui.ListItem(path=media_url)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem)    


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

def addFilmLinks(ex_link):
    if ex_link=='':
        return 0
    #dialog = xbmcgui.Dialog()
    #dialog.ok('Choose a playlist',BASE_URL+ex_link )
    content = getUrl(BASE_URL+ex_link)            
    soup=BeautifulSoup(content)                    
    pozycje = soup.find_all('div',{'itemtype':"http://schema.org/SearchResultsPage"})
    for p in pozycje:
        img = p.find('img').get('src')
        if not img.startswith('http'):
            img = BASE_URL+img
        sublink = p.a.get('href')
        infoLabels={}
        infoLabels['title'] = p.a.text.strip().encode('utf-8')
        infoLabels['plot'] = '\n'.join([x.strip() for x in p.text.split('\n') if not x==''])   
        if sublink.startswith('/film'): #final link
            addLinkItem(infoLabels['title'],sublink,'ChooseAndPlay',img,infoLabels)
        else:
            addDir(infoLabels['title'],sublink,img)

def Sortuj():
    dialog = xbmcgui.Dialog()
    Lista=['new desc','new asc','title desc','title asc','popular desc','popular asc','vote desc','vote asc']
    ret = dialog.select('Choose a playlist', Lista)
    if ret>-1:
        SORT='&sort=%s&order=%s' % (Lista[ret].split()[0],Lista[ret].split()[1])
    else:
        SORT=''
    return SORT
        

def addSeriesSeasons(ex_link='/series/162'):
    if ex_link=='':
        return 0
    content = getUrl(BASE_URL+ex_link)            
    soup=BeautifulSoup(content)
    seasons = soup.find_all('div',{'itemprop':"season"})
    len(seasons)
    ALL=[]
    for season in seasons:
        SN = int(season.find('meta',{'itemprop':"seasonNumber"}).get('content'))
        episodes = season.find_all('tr',{'itemprop':"episode"})
        len(episodes)
        for ep in episodes:
            EPN = ep.find('meta',{'itemprop':"episodeNumber"})
            if not EPN:
                continue;
            EN = int(EPN.get('content'))
            href = ep.find('meta',{'itemprop':"url"}).get('content')
            title = ep.b.text.strip()
            label = 'S%02dE%02d - %s' %(SN,EN,title.encode('utf-8'))
            ALL.append( (label,href))
    for title,url in ALL[::-1]:
        addLinkItem(title,url,'ChooseAndPlay')

#-------------------------------------------	
   
def Sortowanie(_sort,order=True):
    if order=='true':
        sort_order='&order=desc'
    else:
        sort_order='&order=asc'
    if _sort.startswith('Data dodania'):
        sort = '&sort=new'+sort_order
    elif _sort.startswith('Tytul'):
        sort = '&sort=title'+sort_order
    elif _sort.startswith('Odslony'):
        sort = '&sort=popular'+sort_order
    elif _sort.startswith('Oceny'):
        sort = '&sort=vote'+sort_order
    else:
        sort=''
    return sort        

def Jakosc(a):
    if a.startswith('DVD+'):
        out = '&quality=2.3'
    elif a.startswith('HD'):
        out = '&quality=3'
    else:
        out=''
    return out      

def Translation(a):
    if a.startswith('Dubbing/Polski'):
        out = '&translation=3.4'
    elif a.startswith('Lektor/Dubbing/Polski '):
        out = '&translation=2.3.4'
    else:
        out=''
    return out   
 
 
xbmcplugin.setContent(addon_handle, 'movies')	

mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]

SORT    = Sortowanie(my_addon.getSetting('sort'),my_addon.getSetting('sort_order')) 
QUALITY = Jakosc(my_addon.getSetting('quality'))   
TRANSL  = Translation(my_addon.getSetting('translation'))

if mode is None:
    addDir('Filmy','/act/list/type/film',iconImage='DefaultMovies.png')
    addDir('Seriale','/act/list/type/series',iconImage='DefaultTVShows.png')
    addDir('Kabaret','/act/list?title=kabaret')
    addDir('Junior','/act/junior')
    addDir('Szukaj','')
    url = build_url({'mode': 'Opcje'})
    li = xbmcgui.ListItem(label = '-=Opcje=-', iconImage='DefaultScript.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li)

   
elif mode[0] == 'ChooseAndPlay':
    ChooseAndPlay(ex_link)
elif mode[0] == 'Opcje':
    my_addon.openSettings()

elif mode[0] == 'folder':
    if fname == 'Szukaj':
        dialog = xbmcgui.Dialog()
        d = dialog.input('Szukaj, Podaj tytul filmu/serialu/bajki', type=xbmcgui.INPUT_ALPHANUM)
        link='/act/list?title='+d.replace(' ','%20')
        addFilmLinks(link)
    elif ex_link.startswith('/series'):
        addSeriesSeasons(ex_link)
    elif ex_link:
        addFilmLinks(ex_link+SORT+QUALITY+TRANSL)
        


xbmcplugin.endOfDirectory(addon_handle)