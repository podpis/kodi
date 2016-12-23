# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import re
import sys
import os
import base64
import hashlib
import urlparse
import urllib
import urllib2
import urlresolver

addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
addonID = addon.getAddonInfo('id')
addon_handle = int(sys.argv[1])
addon_url     = sys.argv[0]
addon_args = urlparse.parse_qs(sys.argv[2][1:])
USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) ' + addonname + ' Gecko/2008092417 Firefox/3.0.3'
moviesDataFile = 'data.dat'
moviesDataFilePath = xbmc.translatePath(os.path.join('special://home', 'addons', addonID, 'resources', 'libs', moviesDataFile))


import json, urllib2

VERSION='2.0.9'
KODI = xbmc.getInfoLabel("System.BuildVersion")
PASS= 'hgf6652fcs43355hje62'

class apiObject:
    SERVER = 'https://api.alientv.pro'

    def __init__(self, password=PASS, kodi=KODI, wizard=VERSION):
        self.password=password
        self.action = None
        self.action_params = None
        self.kodi_version = kodi
        self.wizard_version = wizard
        self.download_id = None
        self.install_date = None
        self.name = None
        self.full_install = None
        self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) AlienWizard/' + wizard + ' Gecko/2008092417 Firefox/3.0.3'

    def setPassword(self, password):
        if(password == ''):
            password=None
        self.password = password
        return self

    def getPassword(self):
        return self.password

    def setAction(self, action):
        if(action == ''):
            action=None
        self.action = action
        return self

    def getAction(self):
        return self.action

    def setActionParams(self, params):
        if(params == ''):
            params=None
        self.action_params = params
        return self

    def getActionParams(self):
        return self.action_params

    def setKodiVersion(self, version):
        if(version == ''):
            version=None
        self.kodi_version = version
        return self

    def getKodiVersion(self):
        return self.kodi_version

    def setWizardVersion(self, version):
        if(version == ''):
            version=None
        self.wizard_version = version
        return self

    def getWizardVersion(self):
        return self.wizard_version

    def setDownloadId(self, id):
        if(id == ''):
            id=None
        self.download_id = id
        return self

    def getDownloadId(self):
        return self.download_id

    def setInstallDate(self, date):
        if(date == ''):
            date=None
        self.install_date = date
        return self

    def getInstallDate(self):
        return self.install_date

    def setName(self, name):
        if(name == ''):
            name=None
        self.name = name
        return self

    def getName(self):
        return self.name

    def setFullInstall(self, bool):
        if(bool == ''):
            bool=None
        self.full_install = bool
        return self

    def getFullInstall(self):
        return self.full_install

    def createActionParams(self):
        params = '{'
        if self.name != None:
            params +=  '\"name\":\"'+self.name+'\"'
            self.name = None
        if self.full_install != None:
            params +=  ',\"full_install\":\"'+self.full_install+'\"'
            self.full_install = None
        params +=  '}'
        self.action_params = params
        return self

    def getRequest(self, returnResponse = True, decodeUTF = True):
        data = json.dumps(self.__dict__)
        req = urllib2.Request(self.SERVER, data=data)
        req.add_header('User-Agent', self.user_agent)
        try:
            con = urllib2.urlopen(req, timeout = 45)
            if returnResponse != True:
                return con
            resp = con.read()
            con.close()
            if decodeUTF:
                resp = resp.decode('utf-8')
            return resp
        except urllib2.HTTPError, e:
            if e.code == 404:
                raise Exception('NotFound')
            else:
                raise Exception(e)

PASSWORD='hgf6652fcs43355hje62'

def sendRequestFor(action, returnObject=False, returnResponse=True):
    obj = apiObject(PASSWORD, KODI, VERSION)
    obj.setAction(action)
    if returnObject == False:
        return obj.getRequest(returnResponse)
    return obj

def addDir(name, url, args = None, isFolder = False, iconImage=None, isPlayable = False, infos = None):
    if iconImage == None:
        if isFolder == True:
            iconImage='DefaultFolder.png'
        else:
            iconImage = 'DefaultVideo.png'
    if args is not None:
        args = '&args='+base64.b64encode(args)
    else:
        args = ''
    liz = xbmcgui.ListItem(name, iconImage=iconImage, thumbnailImage=iconImage)
    liz.setArt({'poster': iconImage, 'thumb': iconImage, 'icon': iconImage, 'fanart': iconImage, 'banner': iconImage})
    if isPlayable: liz.setProperty('IsPlayable', 'true')
    if infos is not None:
        contextMenuItems = []
        if 'trailer' in infos and infos['trailer'] != '':
            contextMenuItems.append(('[COLOR red]Zobacz zwiastun[/COLOR]', 'XBMC.PlayMedia(%s)' % (infos['trailer'])))
        if 'labels' in infos:
            liz.setInfo(type="video", infoLabels=infos['labels'])
            contextMenuItems.append(('[COLOR red]O filmie[/COLOR]', 'XBMC.Action(Info)'))
        liz.addContextMenuItems(contextMenuItems)
        liz.addStreamInfo('video', {})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=''+addon_url+url+args, listitem=liz, isFolder=isFolder)


def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', USER_AGENT)
    try:
        response = urllib2.urlopen(req)
        content = response.read()
        response.close()
    except:
        content = ''
    return content

def md5(file):
    hash = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()

def getExternalFile(name):
    content = sendRequestFor('file', True).setName(name).createActionParams().getRequest(True, False)
    return content

def m3u2list(url):
    m3u_content = getUrl(url)
    out = []
    matches = re.compile('^#EXTINF:-?[0-9]*(.*?),(.*?)\n(.*?)$', re.I + re.M + re.U + re.S).findall(m3u_content)
    renTags = {'tvg-id': 'tvid', 'audio-track': 'audio-track', 'group-title': 'group', 'tvg-logo': 'img'}

    for params, title, url in matches:
        one = {"title": title, "url": url.split('<')[0]}
        match_params = re.compile(' (.+?)="(.*?)"', re.I + re.M + re.U + re.S).findall(params)
        for field, value in match_params:
            one[renTags.get(field.strip().lower(), 'bad')] = value.strip()
        if not one.get('tvid'):
            one['tvid'] = title

        one['urlepg'] = ''
        one['url'] = one['url'].strip()
        one['title'] = one['title'].strip()
        out.append(one)
    return out

def getArg(name):
    arg = addon_args.get(name, None)
    if arg is not None:
        return arg[0]
    return arg

def decryptFile(file):
    dec = []
    fp = open(file, "rb")
    content = fp.read()
    fp.close()
    enc = content.decode('hex')
    addonID='plugin.video.dreamvision'
    for i in range(len(enc)):
        dec.append(chr((256 + ord(enc[i]) - ord(addonID[i % len(addonID)])) % 256))
    return "".join(dec)
    

def getResourcesDir():
    return xbmc.translatePath(os.path.join('special://home', 'addons', addonID, 'resources'))

def buildUrl(submenu, args):
    main = str(addon_handle)+'?submenu='+submenu
    if args is not None:
        main += '&args='+args.encode('base64')
    return main

def getIcon(name):
    icon = os.path.join(getResourcesDir(), 'icons', name+'.png')
    if os.path.isfile(icon):
        return icon
    return None

def unicodePLchar(string):
    mapping = {'#038;':'', '&nbsp;':'', '&lt;br/&gt;':' ', '&#34;':'"',
               '&#39;':'\'', '&#039;':'\'', '&#8221;':'"', '&#8222;':'"',
               '&#8211;':'-', '&ndash;':'-', '&quot;':'"', '&amp;quot;':'"',
               '&oacute;':'ó', '&Oacute;':'Ó', '&amp;oacute;':'ó', '&amp;Oacute;':'Ó',
               '\u0105':'ą', '\u0104':'Ą', '\u0107':'ć', '\u0106':'Ć', '\u0119':'ę',
               '\u0118':'Ę', '\u0142':'ł', '\u0141':'Ł', '\u0143':'ń', '\u0144':'Ń',
               '\u00f3':'ó', '\u00d3':'Ó', '\u015b':'ś', '\u015a':'Ś', '\u017a':'ź',
               '\u0179':'Ź', '\u017c':'ż', '\u017b':'Ż', '&lt;h5&gt;':'', '&lt;/h5&gt;':''}
    for k, v in mapping.iteritems():
        string = string.replace(k, v)
    return string

def checkMoviesDataFile():
    sum = ''
    if os.path.isfile(moviesDataFilePath):
        sum = md5(moviesDataFilePath)
    req = getExternalFile(urllib.urlencode({moviesDataFile:sum}))
    if req != '':
        dataFile = open(moviesDataFilePath, "wb")
        dataFile.write(req)
        dataFile.close()

def resolveURL(links):
    stream_url = ''
    if isinstance(links, list):
        hosts = [urlparse.urlparse(x).netloc for x in links]
        selection = xbmcgui.Dialog().select("Dostępne hosty", hosts)
    else:
        selection = 0
    if selection > -1:
        try:
            if isinstance(links, list):
                stream_url = urlresolver.resolve(links[selection])
            else:
                stream_url = urlresolver.resolve(str(links))
        except Exception, e:
            stream_url = False
            xbmcgui.Dialog().ok(addonname, 'Error while resolving movie url: [%s]' % str(e))
    return stream_url
