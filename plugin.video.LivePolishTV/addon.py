# -*- coding: utf-8 -*-

import sys,re,os
import urllib,urllib2
import urlparse
import xbmc,xbmcgui,xbmcaddon
import xbmcplugin
import json 
from copy import deepcopy

# THIS CODE CAN BE USED ONLY FOR NON-COMMERCIAL PURPOSE!


base_url        = sys.argv[0]
addon_handle    = int(sys.argv[1])
args            = urlparse.parse_qs(sys.argv[2][1:])
my_addon        = xbmcaddon.Addon()

PATH        = my_addon.getAddonInfo('path')
RESOURCES   = PATH+'/resources/'
sys.path.append( os.path.join( PATH, "lib" ) )


import looknijtv as ltv
import telewizjada as tel
import matchsport as ms
import iklub
import ihtv

# ____________________________
def getUrl(url,data=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link
    
def addLinkItem(name, url, mode, epgname=None, iconimage=None, infoLabels=False, IsPlayable=True,fanart=None):
    u = build_url({'mode': mode, 'foldername': name, 'ex_link' : url})
    
    if iconimage==None:
        iconimage='DefaultFolder.png'
    liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    if epgname:
        commands = []
        commands.append(( 'Program TV', 'RunPlugin(plugin://plugin.video.LivePolishTV?mode=TELEWIZJADA_EPG&ex_link=%s)'%epgname ))
        liz.addContextMenuItems( commands )    
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

def m3u2list(url):
    url = 'https://drive.google.com/uc?export=download&id=0B0PmlVIxygktR3dvSnByTTZtNFE'
    response = getUrl(getUrl(url))
    out = []
    matches=re.compile('^#EXTINF:-?[0-9]*(.*?),(.*?)\n(.*?)$',re.I+re.M+re.U+re.S).findall(response)
    
    renTags={'tvg-id':'tvid',
             'audio-track':'audio-track',
             'group-title':'group',
             'tvg-logo':'img'}
                 
    for params, title, url in matches:
        one  = {"title": title, "url": url}
        match_params =re.compile(' (.+?)="(.*?)"',re.I+re.M+re.U+re.S).findall(params)
        for field, value in match_params:
            one[renTags.get(field.strip().lower(),'bad')] = value.strip()
        if not one.get('tvid'):
            one['tvid']=title
        one['img'] = 'http://moje-filmy.tk/'+one['img']
        one['urlepg']=''
        one = tel.fixForEPG(one)
        out.append(one)
    
    pol = [ o for o in out if o.get('audio-track') == 'pol']
    out = pol
    s=[]
    gourps = set([ o['group'] for o in out])
    order_groups = ['Popularny', 'Informacje', 'Dla Dzieci','Film', 'Dokument',  'Dla Kobiet',  'Sport', 'Muzyka', 'XXX']
    for g in order_groups:
        print '!!!',g
        tmp = [ o for o in out if o.get('group') == g]
        #tmp = sorted(tmp, key=lambda k: k['title'],reverse=True) 
        #for a in tmp:
        #    print a.get('title')
        s.extend(tmp)
    out=s
    return out

def playUrl(name, url, iconimage=None):
    listitem = xbmcgui.ListItem(path=url, thumbnailImage=iconimage)
    listitem.setInfo(type="Video", infoLabels={ "Title": name })
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)

   
def get_tvpLiveStreams(url):
    data=getUrl(url)
    livesrc="/sess/tvplayer.php?object_id=%s"
    
    id_title=re.compile('data-video_id="(.*?)" title="(.*?)">').findall(data)
    img_alt = re.compile('<span class="img"><img src="(.*?)" alt="(.*?)" />').findall(data)
    len(id_title)
    len(img_alt)
    out=[]
    for i in range(len(id_title)):
        video_id = id_title[i][0]
        title = img_alt[i][1].decode('utf-8') + ' : ' + id_title[i][1].decode('utf-8')
        img = img_alt[i][0]
        out.append({'title':title,'img':img,
                    'url':url+livesrc % video_id})
    return out   

def playLiveVido(ex_link='http://tvpstream.tvp.pl/sess/tvplayer.php?object_id=15349841'):
    data=getUrl(ex_link)
    live_src = re.compile("0:{src:'(.*?)'", re.DOTALL).findall(data)
    if live_src:
        listitem = xbmcgui.ListItem(path=live_src[0])
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem)  
    
        
        
#-------------------------------------------	
#
#
# settings_replace = lambda k,v,z: re.sub(r'(?P<id>id="%s") value="(.*)"'%k ,'\g<id> value="%s"'%v, z)
def __update_file(settings_file,new_path):
    pass
#    tree = et.parse(settings_file)        
#    tree.find('setting/[@id="m3uPath"]').attrib["value"]=new_path
#    tree.find('setting/[@id="m3uPathType"]').attrib["value"]='0'
#    tree.find('setting/[@id="epgUrl"]').attrib["value"]="http://epg.iptvlive.org"
#    tree.find('setting/[@id="epgPathType"]').attrib["value"]='1'
#    tree.find('setting/[@id="logoFromEpg"]').attrib["value"]='2'
#    tree.write(settings_file)
    
def update_prv_simpleiptv(pvr_path,m3uPath):
    #pvr_path='C:/Users\\ramic/AppData/Roaming/Kodi/userdata/addon_data/pvr.iptvsimple'
    settings_file=os.path.join(pvr_path,'settings.xml')
    if os.path.exists(settings_file):
        print 'updating settings.xml file'
        __update_file(settings_file,m3uPath)
        return 'Updated %s' %(settings_file)
    else:
        print 'creating settings file'
        xmlcontent="""
<settings>
    <setting id="epgCache" value="true" />
    <setting id="epgPath" value="" />
    <setting id="epgPathType" value="1" />
    <setting id="epgTSOverride" value="true" />
    <setting id="epgTimeShift" value="0.000000" />
    <setting id="epgUrl" value="" />
    <setting id="logoBaseUrl" value="" />
    <setting id="logoFromEpg" value="2" />
    <setting id="logoPath" value="" />
    <setting id="logoPathType" value="1" />
    <setting id="m3uCache" value="true" />
    <setting id="m3uPath" value="" />
    <setting id="m3uPathType" value="0" />
    <setting id="m3uUrl" value="" />
    <setting id="sep1" value="" />
    <setting id="sep2" value="" />
    <setting id="sep3" value="" />
    <setting id="startNum" value="1" />
</settings>
"""
        try:
            os.makedirs(pvr_path)
            with open(settings_file,'w') as f:
                f.write(xmlcontent)
            __update_file(settings_file,m3uPath)
            return 'Created %s' %(settings_file)
        except:
            return 'Problem z uworzeniem settings.xml'
 
#
#
#
#repl = lambda k,v,z: re.sub(r'(?P<id>id="%s") value="(.*)"'%k ,'\g<id> value="%s"'%v, z)
def addon_enable_and_set(addonid='pvr.iptvsimple',settings={'m3uPath': 'dupa'}):
    print '_addon_enable_and_set ID=%s' % addonid
    xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","id":1,"params":{"addonid":"%s", "enabled":true}}'%addonid )
    xbmc.sleep(500)
    msg=''
    try:
        pvr_addon = xbmcaddon.Addon(addonid)
        for k,v in settings.items():
            print 'k=%s v=%s' % (k,v)
            pvr_addon.setSetting(k,v)
        msg='PVR aktywny in uaktualniony'
    except:
        msg='[COLOR red]ERROR[/COLOR] PVR nie uaktualniony, zrob to recznie'
    return msg
    
   
xbmcplugin.setContent(addon_handle, 'movies')	

mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]


if mode is None:
    #addDir('LIVE TV: looknij',iconImage=RESOURCES+'logo-looknij.png')
    #addDir('LIVE TV: telewizjada',iconImage=RESOURCES+'logo_telewizjada.png')
    addDir('LIVE TV: tvp.info','http://tvpstream.tvp.pl',iconImage=RESOURCES+'tvp-info.png')    
    addDir('LIVE TV: moje-filmy.tk',iconImage=RESOURCES+'moje-filmy.png')
    addDir('LIVE TV: iklub.net',iconImage='')
    addDir('LIVE TV: match-sport',iconImage='')
    addDir('LIVE TV: ihtv',iconImage='')
    
    url = build_url({'mode': 'Opcje'})
    li = xbmcgui.ListItem(label = '[COLOR blue]-> aktywuj PVR Live TV[/COLOR]', iconImage='DefaultScript.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li)

elif mode[0] == 'Opcje':
    path =  my_addon.getSetting('path')
    if not path:
        DATAPATH    = xbmc.translatePath(my_addon.getAddonInfo('profile')).decode('utf-8')
        my_addon.setSetting('path',DATAPATH)
    my_addon.openSettings()   

elif mode[0] == 'palyLiveVideo':
    playLiveVido(ex_link)

elif mode[0] == 'playUrl':
    playUrl(fname,ex_link)

        
    
# LOOKNIJ
elif mode[0]=='play_looknij':
    stream_url = ltv.decode_url(ex_link)
    if stream_url:
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
    else:
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=stream_url))

elif mode[0]=='play_ihtv':
    stream_url = ihtv.decode_url(ex_link)
    print '###play_ihtv',stream_url
    if stream_url:
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
    else:
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=stream_url)) 
        
elif mode[0]=='play_iklub':
    stream_url=''
    links = iklub.decode_url(ex_link)
    print 'play_iklub',links
    if len(links)==1:
        stream_url = links[0]
    elif len(links)>1:
        t = ['Link %d'%(i+1) for i in range(len(links))]
        s = xbmcgui.Dialog().select("Sources", t)
        if s>-1:
            stream_url=links[s]
    if stream_url:       
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
    else:
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=stream_url))
        
elif mode[0]=='play_match-sport':
    stream_url = ms.decode_url(ex_link)
    print 'play_match-sport',stream_url
    if stream_url:
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
    else:
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=stream_url)) 
elif mode[0]=='play_telewizjada':
    video_link,_id = ex_link.split('|')
    print PATH
    stream_url = tel.decode_url(video_link,int(_id))
    if stream_url:
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
    else:
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=stream_url))
elif mode[0]=='TELEWIZJADA_EPG':
    print ex_link
    programTV=tel.get_epg(ex_link)
    if programTV:
        ret = xbmcgui.Dialog().select('Program', programTV.split('\n'))

elif mode[0] == 'UPDATE_IPTV':
    fname = my_addon.getSetting('fname')
    path =  my_addon.getSetting('path')
    epgTimeShift = my_addon.getSetting('epgTimeShift')
    epgUrl = my_addon.getSetting('epgUrl')
    m3uPath = os.path.join(path,fname) 
    if os.path.exists(m3uPath):
        xbmc.executebuiltin('StopPVRManager')
        xbmc.executebuiltin('PVR.StopManager')
        new_settings={'m3uPath': m3uPath,'m3uPathType':'0','epgUrl':epgUrl,'epgTimeShift':epgTimeShift,'epgPathType':'1','logoFromEpg':'2'}
        msg=addon_enable_and_set(addonid='pvr.iptvsimple',settings=new_settings)
        
        xbmcgui.Dialog().notification('', msg, xbmcgui.NOTIFICATION_INFO, 1000)
  
        version = int(xbmc.getInfoLabel("System.BuildVersion" )[0:2])
        print 'Kodi version: %d, checking if PVR is active' % version
        json_response = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.GetSettingValue","params":{"setting":"pvrmanager.enabled"},"id":9}')
        decoded_data = json.loads(json_response)
        pvrmanager = decoded_data['result']['value']
    
        if not pvrmanager:
            xbmcgui.Dialog().ok('[COLOR red]Telewizja nie jest aktywna![/COLOR] ','Telewizja PVR nie jest aktywaowana', 'Aktywuj i uruchom ponownie jak Telewizja sie nie pojawi')
            # http://kodi.wiki/view/Window_IDs
            xbmc.executebuiltin('ActivateWindow(10021)')
        
        json_response = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.GetSettingValue","params":{"setting":"pvrmanager.enabled"},"id":9}')
        decoded_data = json.loads(json_response)
        pvrmanager = decoded_data['result']['value']
        if pvrmanager:
            xbmc.executebuiltin('StartPVRManager')
            xbmc.executebuiltin('PVR.StartManager')
            xbmc.executebuiltin('PVR.SearchMissingChannelIcons')
            xbmc.executebuiltin('Notification(PVR Manager, PVR Manager (re)started, 5000)')
            xbmc.sleep(1000)
        xbmc.executebuiltin('Container.Refresh')

    else:
        xbmcgui.Dialog().notification('ERROR', '[COLOR red[Lista m3u jeszcze nie istnieje![/COLOR]', xbmcgui.NOTIFICATION_ERROR, 3000)    


elif mode[0] == 'BUID_M3U':
    #http://192.168.1.3/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22method%22:%22Addons.ExecuteAddon%22,%22params%22:{%22addonid%22:%22plugin.video.LivePolishTV%22,%22params%22:[%22mode=BUID_M3U%22]},%22id%22:1}
    
    fname = my_addon.getSetting('fname')
    path =  my_addon.getSetting('path')
    service = my_addon.getSetting('service')
    print '$$$$$$$$ service', service

    error_msg=""
    if not fname:
        error_msg +="Podaj nazwe pliku "
    if not path:
        error_msg +="Podaj katalog docelowy "
    if not service:
         error_msg +="Wybierz jakies source"
        
    if error_msg:
        xbmcgui.Dialog().notification('[COLOR red]ERROR[/COLOR]', error_msg, xbmcgui.NOTIFICATION_ERROR, 1000)
        pvr_path=  xbmc.translatePath(os.path.join('special://userdata/','addon_data','pvr.iptvsimple'))
        #print pvr_path
        if os.path.exists(os.path.join(pvr_path,'settings.xml')):
            print 'settings.xml exists'
    else:
        outfilename = os.path.join(path,fname)     
        pDialog = xbmcgui.DialogProgressBG()
        pDialog.create('Tworze liste programow TV [%s]'%(fname), 'Uzyj z [COLOR blue]PVR IPTV Simple Client[/COLOR]')
        
        out_all = []
        pDialog.update(0,message='Szukam: [%s]'%service)
        if  service=='Telewizjada':
            out_all = tel.get_root_telewizjada(addheader=True)
        elif service=='Moje-Fimy':
            out_all =  m3u2list('')
        elif service=='Looknij':
            out_all = ltv.get_root_looknji(addheader=True)
        elif service=='iklub':
            out_all = iklub.get_root(addheader=True)            
        elif service=='ihtv':
            out_all = ihtv.get_root(addheader=True)    
        N=len(out_all)
        out_sum=[]
        pDialog.update(0,message= 'Znalazlem!  %d' % N  )
        
        for i,one in enumerate(out_all):
            progress = int((i)*100.0/N)
            message = '%d/%d %s'%(i,N-1,one.get('title','')) 
            pDialog.update(progress, message=message)
            #print "%d\t%s" % (progress,message)
            try:
                if service=='Telewizjada':
                    one['url'] = tel.decode_url(one.get('url',''),one.get('id',''))
                if service=='Looknij':
                    one['url'] = ltv.decode_url(one.get('url',''))
                if service=='Moje-Fimy':
                    pass # no modification is needed
                if service=='iklub':
                    one['url'] = iklub.decode_url(one.get('url',''))
                if service=='ihtv':
                    one['url'] = ihtv.decode_url(one.get('url',''))
                    
                if one['url']:
                    if isinstance(one['url'],list):
                        for url in one['url']:
                            print url
                            one_n=deepcopy(one)
                            one_n['url'] = url 
                            out_sum.append(one_n)
                    else:
                        out_sum.append(one)
            except:
                pass
        if out_sum:
            tel.build_m3u(out_sum,outfilename)
            pDialog.update(progress, message=outfilename)
            xbmcgui.Dialog().notification('Lista zapisana', outfilename, xbmcgui.NOTIFICATION_INFO, 10000)
            xbmcgui.Dialog().ok('[COLOR green]Lista zapisana[/COLOR] ','[COLOR blue]'+outfilename+'[/COLOR]','Uaktualnij ustawienia [COLOR blue]PVR IPTV Simple Client[/COLOR] i (re)aktywuj Live TV')
            
        pDialog.close()
    my_addon.openSettings()      

elif mode[0] == 'folder':
    if fname == 'LIVE TV: tvp.info':
        out = get_tvpLiveStreams(ex_link)
        #xbmcgui.Dialog().ok('Jestem w Live',out[0]['title'].encode('utf-8'))
        for one in out:
           addLinkItem(one['title'].encode('utf-8'), one['url'], 'palyLiveVideo', iconimage=one['img'])

    elif fname == 'LIVE TV: looknij':
        content = ltv.get_root_looknji()
        for one in content:
            addLinkItem(one.get('title',''), one.get('url',''), 'play_looknij', iconimage=one.get('img'))

    elif fname == 'LIVE TV: telewizjada':
        content = tel.get_root_telewizjada()
        for one in content:
            ex_link="%s|%s" % (one.get('url',''),one.get('id'))
            addLinkItem(one.get('title',''), ex_link, 'play_telewizjada', one.get('epgname',None),iconimage=one.get('img'))
    elif fname == 'LIVE TV: moje-filmy.tk':
        content = m3u2list('')
        for one in content:
            addLinkItem(one.get('title',''),  one['url'], 'playUrl', one.get('epgname',None),iconimage=one.get('img'))
    elif fname == 'LIVE TV: iklub.net':
        content = iklub.get_root()
        for one in content:
            addLinkItem(one.get('title',''),  one['url'], 'play_iklub', one.get('epgname',None),iconimage=one.get('img'))
    elif fname == 'LIVE TV: match-sport':
        content = ms.get_root()
        for one in content:
            addLinkItem(one.get('title',''),  one['url'], 'play_match-sport', one.get('epgname',None),iconimage=one.get('img'))
    elif fname == 'LIVE TV: ihtv':
        content = ihtv.get_root()
        for one in content:
            addLinkItem(one.get('title',''),  one['url'], 'play_ihtv', one.get('epgname',None),iconimage=one.get('img'))
         
               
xbmcplugin.endOfDirectory(addon_handle)
