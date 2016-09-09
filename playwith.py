import sys
import xbmc,xbmcaddon,xbmcvfs
import sqlite3
import datetime
import time
import subprocess

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')

channel = sys.argv[1]
start = sys.argv[2]

ADDON.setSetting('playing.with.channel',channel)
ADDON.setSetting('playing.with.start',start)

script = "special://profile/addon_data/script.tvguide.fullscreen/playwith.py"
if xbmcvfs.exists(script):
    xbmc.executebuiltin('RunScript(%s,%s,%s)' % (script,channel,start))
    
core = ADDON.getSetting('autoplaywith.player')
if core:
    xbmc.executebuiltin('PlayWith(%s)' % core)
    xbmc.executebuiltin('PlayMedia(%s)' % url)
    time.sleep(5)
    xbmc.Player().stop()