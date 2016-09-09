import sys
import xbmc,xbmcaddon,xbmcvfs
import sqlite3
import datetime
import time
import subprocess

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')

channel = sys.argv[1]
start = sys.argv[2]

def adapt_datetime(ts):
    return time.mktime(ts.timetuple())

def convert_datetime(ts):
    try:
        return datetime.datetime.fromtimestamp(float(ts))
    except ValueError:
        return None

sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter('timestamp', convert_datetime)

ADDON.setSetting('playing.with.channel',channel)
ADDON.setSetting('playing.with.start',start)

script = "special://profile/addon_data/script.tvguide.fullscreen/playwith.py"
if xbmcvfs.exists(script):
    xbmc.executebuiltin('RunScript(%s,%s,%s)' % (script,channel,start))

core = ADDON.getSetting('autoplaywith.player')
if not core:
    quit()

path = xbmc.translatePath('special://profile/addon_data/script.tvguide.fullscreen/source.db')
try:
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
except Exception as detail:
    xbmc.log("EXCEPTION: (script.tvguide.fullscreen)  %s" % detail, xbmc.LOGERROR)
c = conn.cursor()
c.execute('SELECT stream_url FROM custom_stream_url WHERE channel=?', [channel])
row = c.fetchone()
url = ""
if row:
    url = row[0]
if not url:
    quit()

xbmc.executebuiltin('PlayWith(%s)' % core)
xbmc.executebuiltin('PlayMedia(%s)' % url)