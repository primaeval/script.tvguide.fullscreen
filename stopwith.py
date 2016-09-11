import sys
import xbmc,xbmcaddon,xbmcvfs
import sqlite3
import subprocess

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')

channel = sys.argv[1]
start = sys.argv[2]

if ADDON.getSetting('playing.channel') != channel:
    quit()

if ADDON.getSetting('playing.start') != start:
    quit()

ADDON.setSetting('playing.channel','')
ADDON.setSetting('playing.start','')

script = "special://profile/addon_data/script.tvguide.fullscreen/stopwith.py"
if xbmcvfs.exists(script):
    xbmc.executebuiltin('RunScript(%s,%s,%s)' % (script,channel,start))
xbmc.Player().stop()
