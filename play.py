import sys
import xbmc
import sqlite3

xbmc.log(repr(sys.argv))
channel = sys.argv[1]
xbmc.log(repr(("AAA",channel)))


path = xbmc.translatePath('special://profile/addon_data/script.tvguide.fullscreen/source.db')
xbmc.log(repr(("BBB",path)))
try:
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
except Exception as detail:
    xbmc.log("EXCEPTION: (script.tvguide.fullscreen)  %s" % detail, xbmc.LOGERROR)
if conn:
    c = conn.cursor()
    c.execute('SELECT stream_url FROM custom_stream_url WHERE channel=?', [channel])
    row = c.fetchone()
    xbmc.log(repr(("DDD",row)))
    if row:
        url = row[0]
        xbmc.log(repr(("CCC",url)))
        xbmc.executebuiltin('PlayMedia(%s)' % url)