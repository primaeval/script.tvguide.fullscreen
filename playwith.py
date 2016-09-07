import sys
import xbmc,xbmcaddon,xbmcvfs
import sqlite3
import datetime,time
import subprocess

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')

channel = sys.argv[1]
start = sys.argv[2]

path = xbmc.translatePath('special://profile/addon_data/script.tvguide.fullscreen/source.db')
try:
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
except Exception as detail:
    xbmc.log("EXCEPTION: (script.tvguide.fullscreen)  %s" % detail, xbmc.LOGERROR)

c = conn.cursor()
c.execute('SELECT stream_url FROM custom_stream_url WHERE channel=?', [channel])
row = c.fetchone()
if row:
    url = row[0]
    ADDON.setSetting('playing.with.channel',channel)
    ADDON.setSetting('playing.with.start',start)
    folder = ADDON.getSetting('autoplaywith.folder')
    now = datetime.datetime.now()
    timestamp = str(time.mktime(now.timetuple()))
    command = ADDON.getSetting('autoplaywith.play')
    xbmc.log(repr(command))
    if command:
        retcode = subprocess.call([command, timestamp])
    core = ADDON.getSetting('autoplaywith.player')
    xbmc.log(repr(core))
    if core:
        xbmc.executebuiltin('PlayWith(%s)' % core)
    xbmc.executebuiltin('PlayMedia(%s)' % url)
    time.sleep(5)
    xbmc.Player().stop()