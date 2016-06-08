# -*- coding: utf-8 -*-
import os,re,urllib
import xbmc,xbmcaddon,xbmcgui,xbmcvfs

addonInfo    = xbmcaddon.Addon().getAddonInfo
openFile     = xbmcvfs.File
deleteFile   = xbmcvfs.delete
dataPath     = xbmc.translatePath(addonInfo('profile')).decode('utf-8')
image        = xbmcgui.ControlImage
windowDialog = xbmcgui.WindowDialog()
keyboard     = xbmc.Keyboard

def UserCaptcha(response):
    try:
        i = os.path.join(dataPath,'captcha.png')
        f = openFile(i, 'w')
        f.write(response)
        f.close()
        f = image(450,5,375,115, i)
        d = windowDialog
        d.addControl(f)
        deleteFile(i)
        d.show()
        k = xbmc.Keyboard('', 'Wpisz tekst z obrazka')
        k.doModal()
        c = k.getText() if k.isConfirmed() else None
        if c == '': c = None
        d.removeControl(f)
        d.close()
        return c
    except:
        return

