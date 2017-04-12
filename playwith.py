import sys
import xbmc,xbmcaddon,xbmcvfs
import sqlite3
import datetime
import time
import subprocess
from subprocess import Popen
import re
from vpnapi import VPNAPI


def log(what):
    xbmc.log(repr(what))

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

ADDON.setSetting('playing.channel',channel)
ADDON.setSetting('playing.start',start)

path = xbmc.translatePath('special://profile/addon_data/script.tvguide.fullscreen/source.db')
try:
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
except Exception as detail:
    xbmc.log("EXCEPTION: (script.tvguide.fullscreen)  %s" % detail, xbmc.LOGERROR)

ffmpeg = ADDON.getSetting('autoplaywiths.ffmpeg')
if ffmpeg:
    folder = ADDON.getSetting('autoplaywiths.folder')
    c = conn.cursor()
    c.execute('SELECT stream_url FROM custom_stream_url WHERE channel=?', [channel])
    row = c.fetchone()
    url = ""
    if row:
        url = row[0]
    if not url:
        quit()
    startDate = datetime.datetime.fromtimestamp(float(start))
    c.execute('SELECT DISTINCT * FROM programs WHERE channel=? AND start_date = ?', [channel,startDate])
    for row in c:
        title = row["title"]
        season = row["season"]
        episode = row["episode"]
        if season and episode:
            title += " S%sE%s" % (season, episode)
        endDate = row["end_date"]
        duration = endDate - startDate
        before = int(ADDON.getSetting('autoplaywiths.before'))
        after = int(ADDON.getSetting('autoplaywiths.after'))
        extra = (before + after) * 60
        #TODO start from now
        seconds = duration.seconds + extra
        if seconds > (3600*4):
            seconds = 3600*4
        break
    player = xbmc.Player()
    player.play(url)
    count = 30
    url = ""
    while count:
        count = count - 1
        time.sleep(1)
        if player.isPlaying():
            url = player.getPlayingFile()
            break
    player.stop()

    # Play with your own preferred player and paths
    if url:
        name = "%s - %s - %s" % (channel,title,time.strftime('%Y-%m-%d %H-%M'))
        name = re.sub("\?",'',name)
        name = re.sub(":|<>\/",'',name)
        name = name.encode("cp1252")
        filename = xbmc.translatePath("%s%s.ts" % (folder,name))
        #seconds = 30
        cmd = [ffmpeg, "-y", "-i", url, "-c", "copy", "-t", str(seconds), filename]
        p = Popen(cmd,shell=True)
    quit()

script = "special://profile/addon_data/script.tvguide.fullscreen/playwith.py"
if xbmcvfs.exists(script):
    xbmc.executebuiltin('RunScript(%s,%s,%s)' % (script,channel,start))

core = ADDON.getSetting('autoplaywiths.player')
if not core:
    quit()

c = conn.cursor()
c.execute('SELECT stream_url FROM custom_stream_url WHERE channel=?', [channel])
row = c.fetchone()
url = ""
if row:
    url = row[0]
if not url:
    quit()
else:
    if xbmc.getCondVisibility("System.HasAddon(service.vpn.manager)"):
        try:
            if ADDON.getSetting('vpnmgr.connect') == "true":
                vpndefault = False
                if ADDON.getSetting('vpnmgr.default') == "true":
                    vpndefault = True
                api = VPNAPI()
                if url[0:9] == 'plugin://':
                    api.filterAndSwitch(url, 0, vpndefault, True)
                else:
                    if vpndefault: api.defaultVPN(True)
        except:
            pass

xbmc.executebuiltin('PlayWith(%s)' % core)
xbmc.executebuiltin('PlayMedia(%s)' % url)