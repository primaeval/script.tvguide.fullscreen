import sys
import xbmc,xbmcaddon
import sqlite3

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')

xbmc.log(repr(sys.argv))
channel = sys.argv[1]
start = sys.argv[2]

if plugin.get_setting('playing.channel') != channel:
    quit()
elif plugin.get_setting('playing.start') != start:
    quit()
plugin.set_setting('playing.channel','')
plugin.set_setting('playing.start','')

xbmc.executebuiltin('PlayerControl(Stop)')
'''
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
    #xbmc.executebuiltin('PlayMedia(%s)' % url)
    xbmc.executebuiltin('PlayerControl(Stop)')
'''    