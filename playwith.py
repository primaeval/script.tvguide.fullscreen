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
    '''
    xbmc.log(repr(folder))
    if folder:
        f = xbmcvfs.File('%s/%s.nfo' % (folder,timestamp), "wb")
        f.write(u'\ufeff'.encode("utf8"))
        s = "url=%s\n" % url
        f.write(s.encode("utf8"))
        s = "channel.id=%s\n" % self.currentProgram.channel.id
        f.write(s.encode("utf8"))
        s = "channel.title=%s\n" % self.currentProgram.channel.title
        f.write(s.encode("utf8"))
        s = "channel.logo=%s\n" % self.currentProgram.channel.logo
        f.write(s.encode("utf8"))
        s = "program.title=%s\n" % self.currentProgram.title
        f.write(s.encode("utf8"))
        s = "program.startDate=%s\n" % self.currentProgram.startDate
        f.write(s.encode("utf8"))
        s = "program.endDate=%s\n" % self.currentProgram.endDate
        f.write(s.encode("utf8"))
        s = "program.description=%s\n" % self.currentProgram.description
        f.write(s.encode("utf8"))
        s = "program.imageLarge=%s\n" % self.currentProgram.imageLarge
        f.write(s.encode("utf8"))
        s = "program.imageSmall=%s\n" % self.currentProgram.imageSmall
        f.write(s.encode("utf8"))
        s = "program.episode=%s\n" % self.currentProgram.episode
        f.write(s.encode("utf8"))
        s = "program.season=%s\n" % self.currentProgram.season
        f.write(s.encode("utf8"))
        s = "program.is_movie=%s\n" % self.currentProgram.is_movie
        f.write(s.encode("utf8"))
        s = "autoplays.before=%s\n" % ADDON.getSetting('autoplays.before')
        f.write(s.encode("utf8"))
        s = "autoplays.after=%s\n" % ADDON.getSetting('autoplays.after')
        f.write(s.encode("utf8"))
    '''
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