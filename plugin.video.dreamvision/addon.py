# -*- coding: utf-8 -*-

import xbmcplugin
import sys
from resources.libs import classes, common

play = classes.player()
submenu = common.getArg('submenu')
args = common.getArg('args')

if submenu is None:
    play.getMenu()
else:
    play.handleSubMenu(submenu, args)
xbmcplugin.endOfDirectory(int(sys.argv[1]))