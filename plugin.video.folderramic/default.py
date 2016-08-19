# -*- coding: utf-8 -*-

import sys,os,re,json
import urllib
import urlparse
import xbmcgui,xbmcvfs
import xbmcplugin,xbmcaddon

my_addon        = xbmcaddon.Addon()
my_addon_id     = my_addon.getAddonInfo('id')
addonName       = my_addon.getAddonInfo('name')
PATH            = my_addon.getAddonInfo('path')
DATAPATH        = xbmc.translatePath(my_addon.getAddonInfo('profile')).decode('utf-8')

FAVORITE        = os.path.join(DATAPATH,'favorites.json')

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
xbmcplugin.setContent(addon_handle, 'plugin')


def get_video_plugins():
    print 'get_video_plugins'
    print 'my_addon', my_addon
    print 'my_addon_id [%s]'%my_addon_id    

    addons_path = xbmc.translatePath(os.path.join('special://','home','addons'))
    out = []
    all_addons =  os.listdir(addons_path)
    for addon in all_addons:
        
        if addon.startswith('plugin.video') and addon != my_addon_id:
            data={}
            #print '%s \t\t %s'%(my_addon_id,addon)
            try:
                tmp_addon =  xbmcaddon.Addon(addon)
                data['name'] = tmp_addon.getAddonInfo('name')
                data['url']='plugin://'+tmp_addon.getAddonInfo('id')
                data['img']=tmp_addon.getAddonInfo('icon')
                out.append(data)
            except:
                print 'TRY ERROR %s',addon
                
    return out

def addDirL(name,ex_link=None,mode='folder',pluggin=True,iconImage='DefaultFolder.png',contextO=[''],fanart='',isFolder=True):
    if pluggin:
        url = ex_link
    else:
        url = build_url({'mode': mode, 'foldername': name, 'ex_link' : ex_link, 'img':iconImage})
    li = xbmcgui.ListItem(name, iconImage=iconImage)
    if fanart:
        li.setProperty('fanart_image', fanart )
    contextMenuItems=[]
    
    if 'F_REM' in contextO:
        contextMenuItems.append(('[COLOR red]Usuń plugin z list[/COLOR]', 'RunPlugin(plugin://%s?mode=delPlugin&ex_link=%s)'%(my_addon_id,urllib.quote_plus(name))))
    if 'F_DEL' in contextO:
        contextMenuItems.append(('[COLOR red]Usuń Wszystko z list[/COLOR]', 'RunPlugin(plugin://%s?mode=delPlugin&ex_link=all)'%(my_addon_id)))
    if my_addon.getSetting('hide_addplugin')=='false':
        contextMenuItems.append(('Ukryj [I]\'Dodaj Plugins\'[/I]', 'RunPlugin(plugin://%s?mode=hidePlugin&ex_link=T)'%(my_addon_id)))
    else:
        contextMenuItems.append(('Pokaż [I]\'Dodaj Plugins\'[/I]', 'RunPlugin(plugin://%s?mode=hidePlugin&ex_link=F)'%(my_addon_id)))
    contextMenuItems.append(('[B]Zmień nazwę pluginu[/B]', 'RunPlugin(plugin://%s?mode=renamePlugin&ex_link=)'%(my_addon_id)))
    
    li.addContextMenuItems(contextMenuItems, replaceItems=False)        
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=isFolder)

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

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

my_addon.setSetting('set','set')
mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]
img = args.get('img',[''])[0]

if mode is None:
    jdata = ReadJsonFile(FAVORITE)
    for k in jdata:
        addDirL(k.get('title',''),k.get('url',''),mode='run',iconImage=k.get('img',''),contextO=['F_REM','F_DEL'])

    if my_addon.getSetting('hide_addplugin')=='false' or len(jdata)==0:
        addDirL('Dodaj Plugins','',mode='getPlugins',pluggin=False,iconImage='DefaultAddon.png')

elif mode[0] == 'getPlugins':
    out = get_video_plugins()
    for one in out:
        addDirL(one.get('name'),one.get('url'),mode='addPlugin',pluggin=False,iconImage=one.get('img'),isFolder=False)

elif mode[0] == 'hidePlugin':
    if ex_link =='T':
        my_addon.setSetting('hide_addplugin','true')
    else:
        my_addon.setSetting('hide_addplugin','false')
    xbmc.executebuiltin('XBMC.Container.Refresh')     

elif mode[0] == 'renamePlugin':
    new_name = xbmcgui.Dialog().input('Podaj nową nazwe pluginu [%s]'%addonName, type=xbmcgui.INPUT_ALPHANUM)
    if new_name and new_name != addonName:
        try:
            import xml.etree.ElementTree as ET
            import time
            xml_path = os.path.join(xbmc.translatePath(PATH),'addon.xml')
            tree = ET.parse(xml_path)
            tree.getroot().set('name',new_name)
            tree.write(xml_path)
            xbmc.executebuiltin('Notification([COLOR green]Nazwa zmieniona [/COLOR],[B]wymagany restart![/B] )')
            xbmc.executebuiltin("XBMC.UpdateLocalAddons()")
        except:
            xbmc.executebuiltin('Notification([COLOR red]Problem[/COLOR], )')
    
    
elif mode[0] == 'addPlugin':
    jdata = ReadJsonFile(FAVORITE)
    #print fname,ex_link,img
    new_item={'title':fname,'url':ex_link,'img':img}
    dodac = [x for x in jdata if new_item['title']== x.get('title','')]
    if dodac:
        xbmc.executebuiltin('Notification([COLOR pink]Już jest dodany:[/COLOR] ' + new_item.get('title','').encode('utf-8') + ', )')
    else:
         jdata.append(new_item)
         with open(FAVORITE, 'w') as outfile:
             json.dump(jdata, outfile, indent=2, sort_keys=True)
             xbmc.executebuiltin('Notification(Dodano plugin: ' + new_item.get('title','').encode('utf-8') + ', )')

elif mode[0] == 'delPlugin':
    if ex_link=='all':
        yes = xbmcgui.Dialog().yesno("Usuń","Usunąć wszystkie pluginy z listy?")
        if yes:
            os.remove(FAVORITE)
    else:
        jdata = ReadJsonFile(FAVORITE)
        remItem=urllib.unquote_plus(ex_link)
        to_remove=[] 
        for i in xrange(len(jdata)):
            if jdata[i].get('title') == remItem:
                to_remove.append(i)
        if len(to_remove)>1:
            yes = xbmcgui.Dialog().yesno("Usuń",remItem.get('title'),"Usunąć %d pozycji?" % len(to_remove))
        else:
            yes = True
        if yes:
            for i in reversed(to_remove):
                jdata.pop(i)
            with open(FAVORITE, 'w') as outfile:
                json.dump(jdata, outfile, indent=2, sort_keys=True)
    xbmc.executebuiltin('XBMC.Container.Refresh')  

elif mode[0] == 'run':
    pass
    #xbmc.executebuiltin('XBMC.Container.Refresh')
    #xbmc.executebuiltin('XBMC.ActivateWindow(10025,"%s",return)'%ex_link)

xbmcplugin.endOfDirectory(addon_handle)
    