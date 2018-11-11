import sys
import xbmc,xbmcaddon,xbmcvfs,xbmcgui
import sqlite3
import datetime
import time
import subprocess
from subprocess import Popen
import re
import os

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

def windows():
    if os.name == 'nt':
        return True
    else:
        return False


def android_get_current_appid():
    with open("/proc/%d/cmdline" % os.getpid()) as fp:
        return fp.read().rstrip("\0")



def ffmpeg_location():
    ffmpeg_src = xbmc.translatePath(ADDON.getSetting('autoplaywiths.ffmpeg'))

    if xbmc.getCondVisibility('system.platform.android'):
        ffmpeg_dst = '/data/data/%s/ffmpeg' % android_get_current_appid()

        if (ADDON.getSetting('autoplaywiths.ffmpeg') != ADDON.getSetting('ffmpeg.last')) or (not xbmcvfs.exists(ffmpeg_dst) and ffmpeg_src != ffmpeg_dst):
            xbmcvfs.copy(ffmpeg_src, ffmpeg_dst)
            ADDON.setSetting('ffmpeg.last',ADDON.getSetting('autoplaywiths.ffmpeg'))

        ffmpeg = ffmpeg_dst
    else:
        ffmpeg = ffmpeg_src

    if ffmpeg:
        try:
            st = os.stat(ffmpeg)
            if not (st.st_mode & stat.S_IXUSR):
                try:
                    os.chmod(ffmpeg, st.st_mode | stat.S_IXUSR)
                except:
                    pass
        except:
            pass
    if xbmcvfs.exists(ffmpeg):
        return ffmpeg
    else:
        xbmcgui.Dialog().notification("TVGF", "ffmpeg exe not found!")

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

ffmpeg = ffmpeg_location()
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
        is_movie = row["is_movie"]
        foldertitle = re.sub("\?",'',title)
        foldertitle = re.sub(":|<>\/",'',foldertitle)
        subfolder = "TVShows"
        if is_movie == 'Movie':
            subfolder = "Movies"
        folder = "%s%s/%s/" % (folder, subfolder, foldertitle)
        if not xbmcvfs.exists(folder):
            xbmcvfs.mkdirs(folder)
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
    time.sleep(1)
    player.stop()
    time.sleep(1)

    # Play with your own preferred player and paths
    if url:
        name = "%s - %s - %s" % (channel,title,time.strftime('%Y-%m-%d %H-%M'))
        name = re.sub("\?",'',name)
        name = re.sub(":|<>\/",'',name)
        name = name.encode("cp1252")
        filename = xbmc.translatePath("%s%s.ts" % (folder,name))
        seconds = 3600*4
        cmd = [ffmpeg, "-y", "-i", url, "-c", "copy", "-t", str(seconds), filename]
        log(cmd)
        p = Popen(cmd,shell=windows())
    quit()
