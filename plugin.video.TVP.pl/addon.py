# -*- coding: utf-8 -*-

import sys,re
import urllib,urllib2
import urlparse
import xbmc,xbmcgui,xbmcaddon
import xbmcplugin

#import urlresolver
#import base64
from bs4 import BeautifulSoup
import vodTVPapi as vod


base_url        = sys.argv[0]
addon_handle    = int(sys.argv[1])
args            = urlparse.parse_qs(sys.argv[2][1:])
my_addon        = xbmcaddon.Addon()

BASE_URL    = 'http://kabarety.tvp.pl' 
DZIE_URL    = 'http://dziekibogu.tvp.pl'
PATH        = my_addon.getAddonInfo('path')
RESOURCES   = PATH+'/resources/'

# --- wiadomosci
def tvp_news(name,URL):
    content = getUrl(URL)
    vido_id = re.compile('data-video-id="(.+?)"', re.DOTALL).findall(content)[0]
    url_player='http://wiadomosci.tvp.pl/sess/tvplayer.php?&object_id=' + vido_id
    content = getUrl(url_player)
    poster_link = re.compile("poster:'(.+?)\'", re.DOTALL).findall(content)[0]
    title_link = re.compile('title: "(.+?)",', re.DOTALL).findall(content)[0]    
    vido_link = re.compile("1:{src:\'(.+?)\'", re.DOTALL).findall(content)
    if not vido_link:
        vido_link = re.compile("0:{src:\'(.+?)\'", re.DOTALL).findall(content)
        title_link += ' (Live)'
    li = xbmcgui.ListItem(name +' ' + title_link, iconImage='DefaultVideo.png')
    li.setThumbnailImage(poster_link)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=vido_link[0], listitem=li)


# ____________________________

def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

def addLinkItem(name, url, mode, iconimage=None, infoLabels=False, IsPlayable=True,fanart=None):
    u = build_url({'mode': mode, 'foldername': name, 'ex_link' : url})
    if iconimage==None:
        iconimage='DefaultFolder.png'
    liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    if not infoLabels:
        infoLabels={"Title": name}
    liz.setInfo(type="Video", infoLabels=infoLabels)
    if IsPlayable:
        liz.setProperty('IsPlayable', 'true')
    if fanart:
        liz.setProperty('fanart_image',fanart)
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz)
    return ok


def addDir(name,ex_link=None,mode='folder',iconImage='DefaultFolder.png',fanart=''):
    url = build_url({'mode': mode, 'foldername': name, 'ex_link' : ex_link})
    li = xbmcgui.ListItem(name, iconImage=iconImage)
    if fanart:
        li.setProperty('fanart_image', fanart )
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)


def scanTVPsource(ex_link='/1342039/top10/'):
    if ex_link=='':
        return 0
    ALL=[]
    content = getUrl(BASE_URL+ex_link)            
    soup=BeautifulSoup(content,)
    
    # parse the search page using SoupStrainer and lxml
    #strainer = SoupStrainer('div', attrs={'class': 'pagination'})
    #soup = BeautifulSoup(content, parse_only=strainer)    
    
    strony=soup.find('div',{'class':"pagination"})
    if strony:
        strony = strony.find_all('li')
        prev_page=strony[0].a.get('href')
        next_page=strony[-1].a.get('href')
        last_page=strony[-2].a.get('href').split('-')[-1]
        if not next_page=='#':  
            addLinkItem('== Sortuj ==',ex_link, '_sort_',IsPlayable=False)
        if not prev_page=='#':
            addLinkItem('<< Poprzednia Strona <<' , prev_page, '__page__',IsPlayable=False)
        if not next_page=='#':
            addLinkItem('>> Nastepna Strona %s/%s >>' %(next_page.split('-')[-1],last_page), next_page, '__page__',IsPlayable=False)
        #strainer = SoupStrainer('div', attrs={'class': 'item block'})
        #soup = BeautifulSoup(content, parse_only=strainer)  
        
    skecze = soup.find_all('div',{'class':"item block"})
    for skecz in skecze:
        img = skecz.img.get('src')   
        content = skecz.find('div',{'class':"itemContent"})
        title = content.text.strip().encode('utf-8')
        href = content.a.get('href')
        ALL.append({'href':href,'title':title,'img':img})
        addLinkItem(title, href, '__tvp_kabarety_resolve_play', iconimage=img)
    return 1



def ResolveTVPandPlay(ex_link='/1343773/tomson-baron-i-paranienormalni-tonight'):
    url_player=BASE_URL+ex_link   
    content = getUrl(url_player)
    #src = re.compile("<iframe(.*?)src=\"(.+?)\"(.*?)</iframe>", re.DOTALL).findall(content[:])[0][1]
    soup=BeautifulSoup(content,)
    src=soup.find('iframe',{'class':'tvplayer'}).get('src')
    content = getUrl('http://tvpstream.tvp.pl'+src)
    vido_link = re.compile("1:{src:\'(.+?)\'", re.DOTALL).findall(content)
    if not vido_link:
        vido_link = re.compile("0:{src:\'(.+?)\'", re.DOTALL).findall(content)
    listitem = xbmcgui.ListItem(path=vido_link[0])
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem)      
    
def get_tvpLiveStreams(url):
    data=getUrl(url)
    livesrc="/sess/tvplayer.php?object_id=%s"
    soup=BeautifulSoup(data)
    out=[]
    zrodla = soup.find_all('div',{"class":"button"})
    for z in zrodla:
        video_id = z.get('data-video_id')
        title = z.img.get('alt') + ' : ' + z.get('title')
        img = z.img.get('src')
        out.append({'title':title,'img':img,
                    'url':url+livesrc % video_id})
    return out   

def playLiveVido(ex_link='http://tvpstream.tvp.pl/sess/tvplayer.php?object_id=15349841'):
    data=getUrl(ex_link)
    live_src = re.compile("0:{src:'(.*?)'", re.DOTALL).findall(data)
    if live_src:
        listitem = xbmcgui.ListItem(path=live_src[0])
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem)  


def vodtvp_Informacje_Publicystyka():
    addDir('Wiadomości',ex_link='22672029',mode='vodTVP',iconImage='https://s.tvp.pl/images/3/7/b/uid_37bb32af5d6a78eb11f0ceb85e2e6ac01447946809413_width_218_play_0_pos_0_gs_0.jpg')
    addDir('Panorama',ex_link='22672017',mode='vodTVP',iconImage='https://s.tvp.pl/images/0/0/6/uid_006933b2d603550f0dc0e8b86bf604751448010129661_width_218_play_0_pos_0_gs_0.jpg')
    addDir('Teleexpress',ex_link='22672041',mode='vodTVP',iconImage='https://s.tvp.pl/images/4/1/4/uid_414630010fdb28fba3a1dab5c13d31101448010259841_width_218_play_0_pos_0_gs_0.jpg')
    addDir('Serwis Info',ex_link='22672079',mode='vodTVP',iconImage='https://s.tvp.pl/images/5/c/3/uid_5c38f1ddddbd576c0d3b3d0de33be6c41448010407181_width_218_play_0_pos_0_gs_0.png')
    addDir('Agrobiznes',ex_link='22672105',mode='vodTVP',iconImage='https://s.tvp.pl/images/b/7/8/uid_b78d8b4658ba508758116242d49d6e6b1448010537460_width_218_play_0_pos_0_gs_0.jpg')
    addDir('Minęła dwudziesta',ex_link='22673971',mode='vodTVP',iconImage='https://s.tvp.pl/images/f/9/1/uid_f91f32e961eb0309182f60146d0799d01448010719625_width_218_play_0_pos_0_gs_0.png')
    addDir('AAA',ex_link='3994794',mode='vodTVP',iconImage='https://s.tvp.pl/images/f/9/1/uid_f91f32e961eb0309182f60146d0799d01448010719625_width_218_play_0_pos_0_gs_0.png')


#-------------------------------------------	

xbmcplugin.setContent(addon_handle, 'movies')	

mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]


if mode is None:
    addDir('Wiadomości','http://wiadomosci.tvp.pl/',mode='_news_',iconImage=RESOURCES+'wiadomosci.png')
    addDir('Teleexperss','http://teleexpress.tvp.pl/',mode='_news_',iconImage=RESOURCES+'teleexpress.png')
    addDir('Panorama','http://panorama.tvp.pl/',mode='_news_',iconImage=RESOURCES+'panorama.png')
    addDir('TVP info Live','http://tvpstream.tvp.pl',iconImage=RESOURCES+'tvp-info.png')    
    addDir('Kabarety TVP')
    addDir('Dzięki Bogu już weekend',ex_link='10237279',mode='vodTVP',iconImage='http://s.tvp.pl/images/b/6/6/uid_b66006e90129a44f228baccebfa295241456936112117_width_218_play_0_pos_0_gs_0.jpg')
    #addDir('Informacje i Publicystyka',ex_link='',mode='_infoP')
    addDir('[COLOR blue]vod.TVP.pl[/COLOR]')


elif mode[0] == '_infoP':
    vodtvp_Informacje_Publicystyka()
    
elif mode[0] == '_news_': 
    tvp_news(fname,ex_link)

elif mode[0] == '__page__':
    url = build_url({'mode': 'folder', 'foldername': '', 'ex_link' : ex_link})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)
    
elif mode[0] == '__pageD__':
    url = build_url({'mode': 'update_DziekiBogu', 'foldername': '', 'ex_link' : ex_link})
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)
    
elif mode[0] == '__tvp_kabarety_resolve_play': 
    ResolveTVPandPlay(ex_link)

elif mode[0] == 'palyLiveVideo':
    playLiveVido(ex_link)


elif mode[0] == '_sort_':
    #xbmcgui.Dialog().ok('Jestem w sortuje','fajnie')
    content = getUrl(BASE_URL+ex_link)            
    soup=BeautifulSoup(content)    
    sort = soup.find_all('select',{'onchange':"getComboA(this)"})
    labels=[]
    hrefs=[]
    for one in sort:
        opcje = one.find_all('option')
        for o in opcje:
            labels.append(o.get_text())
            hrefs.append(o.get('value'))
    if labels and hrefs:
        ret = xbmcgui.Dialog().select('Sortuj', labels)
        if ret>-1:
            url = build_url({'mode': 'folder', 'foldername': '', 'ex_link' : hrefs[ret]})
            xbmc.executebuiltin('XBMC.Container.Refresh(%s)'% url)
    
elif mode[0]=='vodTVP_play':
    print 'vodTVP_play'
    print ex_link
    stream_url = vod.vodTVP_GetStreamUrl(ex_link)
    print stream_url
    if stream_url:
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
    else:
        xbmcgui.Dialog().ok('ERROR','URL jest niedostepny')
        
elif mode[0]=='vodTVP':
    (katalog,episodes) = vod.vodTVPapi(ex_link)
    if len(episodes):
        for e in episodes:
            addLinkItem(e.get('title',''), e.get('filename',''), 'vodTVP_play', 
                        infoLabels=e,iconimage=e.get('img',None),fanart=e.get('fanart',None))
    elif len(katalog):
        for one in katalog:
            addDir(one['title'].title(),ex_link=one['id'],mode='vodTVP',iconImage=one['img'])
  
        
elif mode[0] == 'folder':
    if fname=='Kabarety TVP':
        addDir('TOP 10','/1342039/top10/')
        addDir('Skecze','/883/wideo/skecze/')
        addDir('Festiwale','/4982024/wideo/festiwale/')
        addDir('Teraz Ogladane','/5264287/teraz-ogladane/')
    elif fname == 'TVP info Live':
        out = get_tvpLiveStreams(ex_link)
        #xbmcgui.Dialog().ok('Jestem w Live',out[0]['title'].encode('utf-8'))
        for one in out:
           addLinkItem(one['title'].encode('utf-8'), one['url'], 'palyLiveVideo', iconimage=one['img'])
  
    elif fname == '[COLOR blue]vod.TVP.pl[/COLOR]':
        Kategorie = vod.vodTVP_root()
        for k in Kategorie:
            addDir(k.get('title','').title().encode('utf-8'),str(k.get('id','')),mode='vodTVP')
        
    else:
        scanTVPsource(ex_link)
       
        
xbmcplugin.endOfDirectory(addon_handle)
