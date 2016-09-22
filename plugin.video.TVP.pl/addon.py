# -*- coding: utf-8 -*-

import os,sys
import urllib,urllib2
import re,json
import urlparse
import xbmc,xbmcgui,xbmcaddon
import xbmcplugin

import lib.vodTVPapi as vod

base_url        = sys.argv[0]
addon_handle    = int(sys.argv[1])
args            = urlparse.parse_qs(sys.argv[2][1:])
my_addon        = xbmcaddon.Addon()
my_addon_id     = my_addon.getAddonInfo('id')

PATH        = my_addon.getAddonInfo('path')
DATAPATH    = xbmc.translatePath(my_addon.getAddonInfo('profile')).decode('utf-8')
RESOURCES   = PATH+'/resources/'
FAVORITE    = os.path.join(DATAPATH,'favorites.json')

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


def addDir(name,ex_link=None,mode='folder',contextO=['F_ADD'],iconImage='DefaultFolder.png',fanart=''):
    url = build_url({'mode': mode, 'foldername': name, 'ex_link' : ex_link})
    li = xbmcgui.ListItem(name, iconImage=iconImage)
    if fanart:
        li.setProperty('fanart_image', fanart )
    content=urllib.quote_plus(json.dumps({'title':name,'id':ex_link,'img':iconImage}))
    contextMenuItems=[]
    if 'F_ADD' in contextO:
        contextMenuItems.append(('[COLOR green]Dodaj do Wybranych[/COLOR]', 'RunPlugin(plugin://%s?mode=favoritesADD&ex_link=%s)'%(my_addon_id,content)))
    if 'F_REM' in contextO:
        contextMenuItems.append(('[COLOR red]Usuń z Wybranych[/COLOR]', 'RunPlugin(plugin://%s?mode=favoritesREM&ex_link=%s)'%(my_addon_id,content)))
    if 'F_DEL' in contextO:
        contextMenuItems.append(('[COLOR red]Usuń Wszystko[/COLOR]', 'RunPlugin(plugin://%s?mode=favoritesREM&ex_link=all)'%(my_addon_id)))
    li.addContextMenuItems(contextMenuItems, replaceItems=False)     
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def tvp_news(name,URL='http://wiadomosci.tvp.pl/'):
    content = getUrl(URL)
    vido_id = re.compile('data-video-id="(.+?)"', re.DOTALL).findall(content)[0]
    url_player='http://wiadomosci.tvp.pl/sess/tvplayer.php?&object_id=' + vido_id
    content = getUrl(url_player)
    poster_link = re.compile("poster:'(.+?)\'", re.DOTALL).findall(content)
    poster_link = poster_link[0] if poster_link else ''
    title_link = re.compile('title: "(.+?)",', re.DOTALL).findall(content)
    title_link = title_link[0] if title_link else ''
    vido_link = re.compile("1:{src:\'(.+?)\'", re.DOTALL).findall(content)
    if not vido_link:
        vido_link = re.compile("0:{src:\'(.+?)\'", re.DOTALL).findall(content)
        if vido_link:
           vido_link = vod.m3u_quality(vido_link[0])
        title_link += ' (Live) '
  
    for vl in vido_link:
        url = vl
        title2 = ''
        if isinstance(vl,dict):
            url = vl.get('url',vl)
            title2='[B]'+vl.get('title','')+'[/B]'
        li = xbmcgui.ListItem(name +' ' + title_link + title2, iconImage='DefaultVideo.png')
        li.setThumbnailImage(poster_link)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

def get_tvpLiveStreams(url='http://tvpstream.tvp.pl'):
    data=getUrl(url)
    livesrc="/sess/tvplayer.php?object_id=%s"
    id_title = re.compile('data-video_id="(.*?)" title="(.*?)"').findall(data)
    img = re.compile('<img src="(.*?)" alt="(.*?)"').findall(data) 
    out=[]
    for idtitle,imgalt in zip(id_title,img):
        print idtitle,imgalt
        video_id = idtitle[0]
        title = imgalt[1].title() + ': ' + idtitle[1]
        img = imgalt[0] 
        out.append({'title':title.decode('utf-8'),'img':img,
                    'url':url+livesrc % video_id})
    return out

def playLiveVido(ex_link='http://tvpstream.tvp.pl/sess/tvplayer.php?object_id=26771385'):
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
    addDir('Po prostu. Program Tomasza Sekielskiego',ex_link='9525905',mode='vodTVP',iconImage='')
    addDir('Polityka przy kawie',ex_link='2625476',mode='vodTVP',iconImage='http://s.tvp.pl/images/2/1/7/uid_217cbf307a79ac55e7b5c48389a59b6b1286463046834_width_218_play_0_pos_0_gs_0.jpg')
    addDir('Publicystyka Najnowsze',ex_link='8306415',mode='vodTVP',iconImage='')

def vodtvp_Kabarety_TVP():
    addDir('TOP 10',ex_link='1342039',mode='vodTVP')
    addDir('Skecze',ex_link='883',mode='vodTVP')
    addDir('Festiwale',ex_link='4982024',mode='vodTVP')
    addDir('Teraz Ogladane',ex_link='5264287',mode='vodTVP')
    addDir('Kabaretowy Klub Dwójki',ex_link='4066916',mode='vodTVP')
    addDir('Dzięki Bogu już weekend',ex_link='10237279',mode='vodTVP',iconImage='http://s.tvp.pl/images/b/6/6/uid_b66006e90129a44f228baccebfa295241456936112117_width_218_play_0_pos_0_gs_0.jpg')
    addDir('N jak Neonówka',ex_link='5775029',mode='vodTVP')
    addDir('Kabaretożercy',ex_link='2625743',mode='vodTVP')

def vodtvp_RIO():
    addDir('Transmisje',ex_link='23578493',mode='vodTVP')
    addDir('Wideo',ex_link='23578509',mode='vodTVP') #19369963
    addDir('Dyscypliny',ex_link='24035157',mode='vodTVP')
   
    
def settings_getProxy():
    protocol =  my_addon.getSetting('protocol')
    ipaddress = my_addon.getSetting('ipaddress')
    ipport = my_addon.getSetting('ipport')
    if 'http' in protocol and ipport and ipaddress:
        return {protocol: '%s:%s'%(ipaddress,ipport)}
    else:
        return {}

def settings_setProxy(proxy={'http':'10.10.10.10:50'}):
    protocol = proxy.keys()[0]
    ipaddress,ipport = proxy[protocol].split(':') 
    my_addon.setSetting('protocol',protocol)
    my_addon.setSetting('ipaddress',ipaddress)
    my_addon.setSetting('ipport',ipport)
   
def ReadJsonFile(jfilename):
    if os.path.exists(jfilename):
        with open(jfilename,'r') as f:
            content = f.read()
            if not content:
                content ='[]'
    else:
        content = '[]'
    data=json.loads(content)
    return data



xbmcplugin.setContent(addon_handle, 'movies')	
my_addon.setSetting('set','set')
mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]

if mode is None:
    #addDir('[B][COLOR blue]Rio 2016[/COLOR][/B]',ex_link='',mode='_RIO',contextO=[],iconImage=RESOURCES+'rio-tvp-logo.png')
    addDir('Wiadomości','http://wiadomosci.tvp.pl/',mode='_news_',contextO=[],iconImage=RESOURCES+'wiadomosci.png')
    addDir('Teleexperss','http://teleexpress.tvp.pl/',mode='_news_',contextO=[],iconImage=RESOURCES+'teleexpress.png')
    addDir('Panorama','http://panorama.tvp.pl/',mode='_news_',contextO=[],iconImage=RESOURCES+'panorama.png')
    addDir('TVP info Live','http://tvpstream.tvp.pl',contextO=[],iconImage=RESOURCES+'tvp-info.png')    
    addDir('Kabarety TVP',ex_link='',mode='_Kabarety',contextO=[],iconImage=RESOURCES+'kabaretytvp.png')
    addDir('Informacje i Publicystyka',ex_link='',mode='_infoP',contextO=[],iconImage=RESOURCES+'publicystykatvp.png')
    addDir('Astronarium',ex_link='http://www.astronarium.pl/odcinki/',mode='Astronarium',contextO=[],iconImage='http://www.astronarium.pl/pliki/astronarium_logo_small.jpg')

    addDir('[COLOR blue]vod.TVP.pl[/COLOR]',contextO=[],iconImage=RESOURCES+'vodtvp.png')
    addDir('[COLOR lightblue]vod.Wybrane[/COLOR]',ex_link=FAVORITE, mode='favorites',contextO=[],iconImage=RESOURCES+'wybrane.png')
    
# elif mode[0] == '_RIO':
#     vodtvp_RIO()   

elif mode[0] == 'Astronarium': 
    import lib.astronarium as astronarium
    out=astronarium.getEpisodes(ex_link)
    for one in out:
        addLinkItem(one['title'], one['url'], 'Astronarium_play', iconimage=one['img'])  
elif mode[0] == 'Astronarium_play':
    import lib.astronarium as astronarium
    src = astronarium.getVideo(ex_link)
    if src:
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=src))  
    else:
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=''))  
        
elif mode[0] == '_news_': 
    tvp_news(fname,ex_link)
elif mode[0] == '_infoP':
    vodtvp_Informacje_Publicystyka()
elif mode[0] == '_Kabarety':
    vodtvp_Kabarety_TVP()

elif mode[0] == 'palyLiveVideo':
    playLiveVido(ex_link)

elif mode[0] == 'favorites':
    jdata = ReadJsonFile(FAVORITE)
    for k in jdata:
        addDir(k.get('title','').title().encode('utf-8'),str(k.get('id','')),mode='vodTVP',contextO=['F_REM','F_DEL'],iconImage=k.get('img',''))
        
elif mode[0] == 'favoritesADD':
    print ex_link
    jdata = ReadJsonFile(FAVORITE)
    new_item=json.loads(ex_link)
    dodac = [x for x in jdata if new_item['title']== x.get('title','')]
    if dodac:
        xbmc.executebuiltin('Notification([COLOR pink]Już jest w Wybranych[/COLOR], ' + new_item.get('title','').encode('utf-8') + ', 200)')
    else:
        jdata.append(new_item)
        with open(FAVORITE, 'w') as outfile:
            json.dump(jdata, outfile, indent=2, sort_keys=True)
            xbmc.executebuiltin('Notification(Dodano Do Wybranych, ' + new_item.get('title','').encode('utf-8') + ', 200)')

elif mode[0] == 'favoritesREM':
    if ex_link=='all':
        yes = xbmcgui.Dialog().yesno("??","Usuń wszystkie filmy z Wybranych?")
        if yes:
            os.remove(FAVORITE)
    else:
        print 'favoritesREM'
        jdata = ReadJsonFile(FAVORITE)
        remItem=json.loads(ex_link)
        to_remove=[] 
        for i in xrange(len(jdata)):
            if int(jdata[i].get('id')) == int(remItem.get('id')):
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
     
    
elif mode[0]=='vodTVP_play':
    print 'vodTVP_play'
    print ex_link
    stream_url = vod.vodTVP_GetStreamUrl(ex_link)
    print stream_url
    # Proxy
    if 'material_niedostepny' in stream_url:
        y=xbmcgui.Dialog().yesno("[COLOR orange]Problem[/COLOR]", '[B]Ograniczenia Licencyjne, material jest niedostępny[/B]','Spróbowac użyć serwera proxy ??')
        if y:
            import lib.twork as tw

            stream_url=''
            timeout=  int(my_addon.getSetting('timeout'))
            dialog  = xbmcgui.DialogProgress()
            dialog.create('Szukam darmowych serwerów proxy ...')
            proxies=vod.getProxies()
            proxy = settings_getProxy()
            if proxy:
                proxies.insert(0,proxy)
                
            dialog.create('Znalazłem %d serwerów proxy'%len(proxies))
            print 'PROXY STARTING'
            
            threads = [tw.Thread(vod.vodTVP_GetStreamUrl, ex_link,proxy,timeout) for proxy in proxies ]
            [i.start() for i in threads]
            dialog.update(0,'Sprawdzam %d serwery ... '%(len(threads)))
            while any([i.isAlive() for i in threads]):
                xbmc.sleep(1000)    #ms
                done = [t for t in threads if not t.isAlive()]
                dialog.update(int(1.0*len(done)/len(proxies)*100),'Sprawdzam, negatywnie odpowiedziało: %d, proszę czekać'%(len(done)))
                print '%d / %d'%(len(done),len(threads))
                for t in done:
                    stream_url = t.result
                    if isinstance(stream_url,list) or (stream_url and not 'material_niedostepny' in stream_url): 
                        print 'PROXY YES FOUND'
                        print 'setting default'
                        settings_setProxy(t._args[1])
                        break
                    else:
                        print 'NO [%s]'%stream_url
                        stream_url=''
                if stream_url or dialog.iscanceled():
                    break

                
            dialog.close()
            print 'AFTER PROXY'
            print stream_url
    
    if isinstance(stream_url,list):
        label= [x.get('title') for x in stream_url]
        if len(label)>1:
            s = xbmcgui.Dialog().select('Wybierz', label)
            stream_url = stream_url[s].get('url') if s>-1 else ''
        else:
            stream_url = stream_url[0].get('url')
                    
    if stream_url:
        #if stream_url.endswith('m3u8'):
        #    stream_url += '|X-Forwarded-For=127.0.0.1|User-Agent=Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0'
        print '%%%',stream_url
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
    else:
        #xbmcgui.Dialog().ok('ERROR','URL jest niedostepny')
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=''))
        #settings_setProxy({'None':'0.0.0.0:0'}) 
 
# elif mode[0]=='vodTVP_play':
#     print 'vodTVP_play'
#     print ex_link
#     stream_url = vod.vodTVP_GetStreamUrl(ex_link)
#     print stream_url
#     # Proxy
#     if 'material_niedostepny' in stream_url:
#         y=xbmcgui.Dialog().yesno("[COLOR orange]Problem[/COLOR]", '[B]Ograniczenia Licencyjne, material jest niedostępny[/B]','Spróbowac użyć serwera proxy ??')
#         if y:
#             stream_url=''
#             timeout=  int(my_addon.getSetting('timeout'))
#             dialog  = xbmcgui.DialogProgress()
#             proxy = settings_getProxy()
#             if proxy:
#                 dialog.create('Ustawiony serwer proxy','Sprawdzam: %s'%(proxy.values()[0]))
#                 stream_url = vod.vodTVP_GetStreamUrl(ex_link,proxy,timeout=int(timeout)) 
#                 if isinstance(stream_url,list) or (stream_url and not 'material_niedostepny' in stream_url): 
#                     pass
#                 else:
#                     stream_url=''
#             if len(stream_url)==0:
#                 dialog.create('Szukam darmowych serwerów proxy ...')
#                 proxies=vod.getProxies()
#                 dialog.create('Znalazłem %d serwerów proxy'%len(proxies))
#                 for i,proxy in enumerate(proxies):
#                     dialog.update(int(1.0*i/len(proxies)*100),'(%s) Sprawdzam: %s'%(i+1,proxy.values()[0]))
#                     stream_url = vod.vodTVP_GetStreamUrl(ex_link,proxy,timeout=int(timeout))
#                     if isinstance(stream_url,list) or (stream_url and not 'material_niedostepny' in stream_url): 
#                         settings_setProxy(proxy)
#                         break
#                     
#             dialog.close()
#             # print 'AFTER PROXY'
#             # print stream_url
#     
#     if isinstance(stream_url,list):
#         label= [x.get('title') for x in stream_url]
#         if len(label)>1:
#             s = xbmcgui.Dialog().select('Wybierz', label)
#             stream_url = stream_url[s].get('url')
#         else:
#             stream_url = stream_url[0].get('url')
#                     
#     if stream_url:
#         #if stream_url.endswith('m3u8'):
#         #    stream_url += '|X-Forwarded-For=127.0.0.1|User-Agent=Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0'
#         print '%%%',stream_url
#         xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
#     else:
#         xbmcgui.Dialog().ok('ERROR','URL jest niedostepny')
#         settings_setProxy({'None':'0.0.0.0:0'})  
      
elif mode[0]=='vodTVP':
    (katalog,episodes) = vod.vodTVPapi(ex_link)
    if len(episodes):
        for e in episodes:
            addLinkItem(e.get('title',''), e.get('filename',''), 'vodTVP_play', 
                        infoLabels=e,iconimage=e.get('img',None),fanart=e.get('fanart',None))
    elif len(katalog):
        for one in katalog:
            addDir(one['title'],ex_link=one['id'],mode='vodTVP',iconImage=one['img'])
  
        
elif mode[0] == 'folder':
    if fname == 'TVP info Live':
        out = get_tvpLiveStreams(ex_link)
        for one in out:
           addLinkItem(one['title'].encode('utf-8'), one['url'], 'palyLiveVideo', iconimage=one['img'])
  
    elif fname == '[COLOR blue]vod.TVP.pl[/COLOR]':
        Kategorie = vod.vodTVP_root()
        for k in Kategorie:
            addDir(k.get('title','').title().encode('utf-8'),str(k.get('id','')),mode='vodTVP')
        
    else:
        scanTVPsource(ex_link)
      
       
xbmcplugin.endOfDirectory(addon_handle)
