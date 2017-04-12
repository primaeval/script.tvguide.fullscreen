import sys
import xbmc,xbmcaddon
import sqlite3
from vpnapi import VPNAPI

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
    ADDON.setSetting('playing.channel',channel)
    ADDON.setSetting('playing.start',start)
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
    xbmc.executebuiltin('PlayMedia(%s)' % url)