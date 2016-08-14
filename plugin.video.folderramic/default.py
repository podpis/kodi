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
DATAPATH    = xbmc.translatePath(my_addon.getAddonInfo('profile')).decode('utf-8')

FAVORITE    = os.path.join(DATAPATH,'favorites.json')

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
xbmcplugin.setContent(addon_handle, 'plugin')

#addon_path=r'c:\users\ramic\appdata\roaming\Kodi\addons\plugin.video.alltube'

def get_addon_xml(addon_path):
    with open(os.path.join(addon_path,'addon.xml'),'r') as f:
        data = f.read()
    metadata={}
    if data:
        addon = re.compile('<addon(.*?)>',re.DOTALL).search(data)
        if addon:
            id = re.search('id="(.*?)"',addon.group(1))
            name = re.search('name="(.*?)"',addon.group(1))
            providername = re.search('provider-name="(.*?)"',addon.group(1))
            version = re.search('version="(.*?)"',addon.group(1))
            metadata['id'] = id.group(1) if id else ''       
            metadata['name'] = name.group(1) if name else ''            
            metadata['providername'] = providername.group(1) if providername else ''            
            metadata['version'] = version.group(1) if version else ''            
        extension = re.compile('<extension(.*?)>',re.DOTALL).search(data)
        if extension:
            library = re.search('library="(.*?)"',extension.group(1))
            metadata['library'] = library.group(1) if library else ''
    return metadata
    
def get_video_plugins():
    addons_path = os.path.join(PATH,'..')
    out = []
    all_addons =  os.listdir(addons_path)
    for addon in all_addons:
        addon_path = os.path.join(addons_path,addon)
        if addon.startswith('plugin.video') and  os.path.isdir(addon_path):
            data = get_addon_xml(addon_path)
            data['url']='plugin://'+data.get('id')
            data['img']=os.path.join(addon_path,'icon.png')
            if addonName not in data['name']:
                out.append(data)
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
        yes = xbmcgui.Dialog().yesno("??","Usuń wszystkie filmy z Wybranych?")
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
            yes = xbmcgui.Dialog().yesno("??",remItem.get('title'),"Usuń %d pozycji z Wybranych?" % len(to_remove))
        else:
            yes = True
        if yes:
            for i in reversed(to_remove):
                jdata.pop(i)
            with open(FAVORITE, 'w') as outfile:
                json.dump(jdata, outfile, indent=2, sort_keys=True)
    xbmc.executebuiltin('XBMC.Container.Refresh')  

elif mode[0] == 'run':
    xbmc.executebuiltin('XBMC.Container.Refresh')  

xbmcplugin.endOfDirectory(addon_handle)
    