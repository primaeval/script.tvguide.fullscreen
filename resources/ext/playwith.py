import sys
import xbmc,xbmcaddon,xbmcvfs
import sqlite3
from subprocess import Popen, CREATE_NEW_CONSOLE
import datetime,time
xbmc.log("XXX started")
channel = sys.argv[1]
start = sys.argv[2]
xbmc.log(repr(sys.argv))
#core = "record"
core = "dummy"



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
    conn.row_factory = sqlite3.Row
except Exception as detail:
    xbmc.log("EXCEPTION: (script.tvguide.fullscreen)  %s" % detail, xbmc.LOGERROR)
    
  

c = conn.cursor()

startDate = datetime.datetime.fromtimestamp(float(start))
xbmc.log(repr(startDate))
#c.execute('SELECT * FROM programs')
c.execute('SELECT DISTINCT * FROM programs WHERE channel=? AND start_date = ?', [channel,startDate])
#row = c.fetchone()
for row in c:
    title = row["title"]
xbmc.log(repr(("row",row)))



c.execute('SELECT stream_url FROM custom_stream_url WHERE channel=?', [channel])
row = c.fetchone()
if row:
    url = row[0]

class MyPlayer(xbmc.Player):
    def onPlayBackStarted():
        xbmc.log("XXX onPlayBackStarted")
        
    def onPlayBackStopped():
        xbmc.log("XXX onPlayBackStopped")

f = xbmcvfs.File("special://profile/addon_data/script.tvguide.fullscreen/test.txt","wb")
#f.write(repr(sys.argv))
xbmc.executebuiltin('PlayWith(%s)' % core)
#xbmc.executebuiltin('PlayMedia(%s)' % url)
myPlayer = MyPlayer()
myPlayer.play(url)
#cmd = [r"c:\utils\ffmpeg.exe", "-i", sys.argv[1], r"C:\Kodi16.1\portable_data\userdata\addon_data\script.tvguide.fullscreen\out.ts"]
#p = Popen(cmd,shell=True)
#time.sleep(2)
count = 10
url = ""
while count:
    count = count - 1
    xbmc.log(repr(count))
    time.sleep(1)
    #xbmc.log(repr(myPlayer.isPlaying()))
    if myPlayer.isPlaying():
        url = myPlayer.getPlayingFile()
        xbmc.log(repr(myPlayer.getPlayingFile()))    
        break

myPlayer.stop()
#xbmc.log("XXX finished")
#time.sleep(10)
if url:
    name = "%s - %s - %s" % (start,channel,title)
    xbmc.log(repr(name))
    name = name.encode("cp1252")
    cmd = [r"c:\utils\ffmpeg.exe", "-y", "-i", url, r"C:\Kodi16.1\portable_data\userdata\addon_data\script.tvguide.fullscreen\%s.ts" % name]
    xbmc.log(repr(cmd))
    f.write(repr(cmd))
    p = Popen(cmd,shell=False)