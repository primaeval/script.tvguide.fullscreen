import sys
import xbmc,xbmcaddon
import sqlite3
import subprocess

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')
'''
channel = sys.argv[1]
start = sys.argv[2]

if ADDON.getSetting('playing.with.channel') != channel:
    quit()
elif ADDON.getSetting('playing.with.start') != start:
    quit()
ADDON.setSetting('playing.with.channel','')
ADDON.setSetting('playing.with.start','')
'''
command = ADDON.getSetting('autoplaywith.stop')
if command:
    retcode = subprocess.call([command])
xbmc.executebuiltin('PlayerControl(Stop)')