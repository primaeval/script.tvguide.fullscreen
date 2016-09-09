import sys
import xbmc,xbmcaddon,xbmcvfs
import sqlite3
import datetime
import time
import subprocess

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')
xbmc.log(repr(sys.argv))
channel = sys.argv[1]
start = sys.argv[2]

'''
def adapt_datetime(ts):
    # http://docs.python.org/2/library/sqlite3.html#registering-an-adapter-callable
    return time.mktime(ts.timetuple())


def convert_datetime(ts):
    try:
        return datetime.datetime.fromtimestamp(float(ts))
    except ValueError:
        return None

sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter('timestamp', convert_datetime)  

path = xbmc.translatePath('special://profile/addon_data/script.tvguide.fullscreen/source.db')
try:
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
except Exception as detail:
    xbmc.log("EXCEPTION: (script.tvguide.fullscreen)  %s" % detail, xbmc.LOGERROR)
    
  

c = conn.cursor()

startDate = datetime.datetime.fromtimestamp(float(start))
xbmc.log(repr(startDate))
#c.execute('SELECT * FROM programs')
c.execute('SELECT * FROM programs WHERE channel=? AND start_date = ?', [channel,startDate])
row = c.fetchone()
xbmc.log(repr(("row",row)))



c.execute('SELECT stream_url FROM custom_stream_url WHERE channel=?', [channel])
row = c.fetchone()
if row:
    url = row[0]
'''
    
ADDON.setSetting('playing.with.channel',channel)
ADDON.setSetting('playing.with.start',start)
#folder = ADDON.getSetting('autoplaywith.folder')
#now = datetime.datetime.now()
#timestamp = str(time.mktime(now.timetuple()))
#command = ADDON.getSetting('autoplaywith.play')
#if command:
#    retcode = subprocess.call([command, timestamp],creationflags=subprocess.SW_HIDE, shell=True)
script = "special://profile/addon_data/script.tvguide.fullscreen/playwith.py"
#TODO if script exists
if xbmcvfs.exists(script):
    xbmc.executebuiltin('RunScript(%s,%s,%s)' % (script,channel,start))
core = ADDON.getSetting('autoplaywith.player')
if core:
    xbmc.executebuiltin('PlayWith(%s)' % core)
    xbmc.executebuiltin('PlayMedia(%s)' % url)
    time.sleep(5)
    xbmc.Player().stop()