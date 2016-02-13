# -*- coding: utf-8 -*-
import sys,re,os
import urllib,urllib2
import urlparse
import xbmc,xbmcgui,xbmcaddon
import xbmcplugin
import json 

from resources.lib import cdapl as cda

## submodules
# import cdapl as cda

base_url        = sys.argv[0]
addon_handle    = int(sys.argv[1])
args            = urlparse.parse_qs(sys.argv[2][1:])
my_addon        = xbmcaddon.Addon()

PATH        = my_addon.getAddonInfo('path')
RESOURCES   = PATH+'/resources/'

## COMMON Functions
def getUrl(url,data=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36')
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
        infoLabels={"title": name}
    liz.setInfo(type="video", infoLabels=infoLabels)
    if IsPlayable:
        liz.setProperty('IsPlayable', 'true')
    if fanart:
        liz.setProperty('fanart_image',fanart)
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz,isFolder=False)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%D, %P")
    return ok

def addDir(name,ex_link=None,json_file='', mode='walk',iconImage='DefaultFolder.png',fanart=''):
    url = build_url({'mode': mode, 'foldername': name, 'ex_link' : ex_link, 'json_file' : json_file})
    #li = xbmcgui.ListItem(name.encode("utf-8"), iconImage=iconImage)
    li = xbmcgui.ListItem(name, iconImage=iconImage)
    if fanart:
        li.setProperty('fanart_image', fanart )
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)


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
    

## COMMON Functions

def decodeVideo(ex_link):
    stream_url = cda.getVideoUrls(ex_link)
    if type(stream_url) is list:
        qualityList = [x[0] for x in stream_url]
        selection = xbmcgui.Dialog().select("Quality [can be set default]", qualityList)
        if selection>-1:
            stream_url = cda.getVideoUrls(stream_url[selection][1],4)
        else:
            stream_url=''
    print stream_url    
    
    if stream_url:
        xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
    


def mainWalk(ex_link,json_file):
    items=[]
    folders=[]
    if ex_link=='' or ex_link.startswith('/'):       #jsonWalk
        data = cda.ReadJsonFile(json_file)
        items,folders = cda.jsconWalk(data,ex_link)
    if 'folder' in ex_link:                        
        items,folders = cda.get_UserFolder_content( 
                                urlF        = ex_link,
                                recursive   = True,
                                filtr_items = {} )
        
    for f in folders:
        tmp_json_file = f.get('jsonfile',json_file) # use new json file
        addDir(f.get('title'),ex_link=f.get('url'), json_file=tmp_json_file, mode='walk', iconImage=f.get('img',''),fanart=f.get('fanart',''))
    for item in items:
        addLinkItem(name=item.get('title').encode("utf-8"), url=item.get('url'), mode='decodeVideo', iconimage=item.get('img'), infoLabels=item, IsPlayable=True,fanart=None)

 
## MAIN LOOP 
   
xbmcplugin.setContent(addon_handle, 'movies')	

mode = args.get('mode', None)
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]
json_file = args.get('json_file',[''])[0]

if mode is None:
    mainWalk("",os.path.join(PATH,'root.json'))
    #addDir('TEST',ex_link=u'',json_file=os.path.join(PATH,'document.json'), mode='walk', iconImage=RESOURCES+'logo-looknij.png')


elif mode[0] == 'decodeVideo':
    decodeVideo(ex_link)

elif mode[0] == 'Opcje':
    my_addon.openSettings()   

elif mode[0] == 'walk':
    mainWalk(ex_link,json_file) 

elif mode[0] == 'folder':
    if fname == 'TEST':
        pass
   

        

xbmcplugin.endOfDirectory(addon_handle)
