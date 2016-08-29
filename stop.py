import sys
import xbmc,xbmcaddon
import sqlite3

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')

channel = sys.argv[1]
start = sys.argv[2]

if ADDON.getSetting('playing.channel') != channel:
    quit()
elif ADDON.getSetting('playing.start') != start:
    quit()
ADDON.setSetting('playing.channel','')
ADDON.setSetting('playing.start','')

xbmc.executebuiltin('PlayerControl(Stop)')