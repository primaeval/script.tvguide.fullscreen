import sys
import xbmc,xbmcaddon,xbmcvfs,xbmcgui
import sqlite3
import re
import urllib
from HTMLParser import HTMLParser
from rpc import RPC

installed_addons = []
for media in ["video","audio","executable"]:
    type = "xbmc.addon.%s" % media
    response = RPC.addons.get_addons(type=type,properties=["name", "thumbnail"])
    if "addons" not in response:
        continue
    adds = response["addons"]
    installed_addons = installed_addons + [a['addonid'] for a in adds]

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')
orig_title = sys.argv[1]
tv = False
if len(sys.argv) > 2:
    tv = True
    season = sys.argv[2]
    episode = sys.argv[3]
match = re.search('(.*?)\([0-9]{4}\)$',orig_title)
if match:
    orig_title = match.group(1).strip()
title = urllib.quote_plus(orig_title)

f = xbmcvfs.File('special://profile/addon_data/script.tvguide.fullscreen/favourites.xml')
data = f.read()
f.close()
if not data:
    f = xbmcvfs.File('special://home/addons/script.tvguide.fullscreen/resources/favourites.xml')
    data = f.read()
    f.close()

search_addons = {}
match = re.findall('<favourite name="(.*?)" thumb="(.*?)">(.*?)</favourite>',data)
for m in match:
    name = m[0]
    thumb = m[1]
    action = m[2]
    action = HTMLParser().unescape(action)
    action = re.sub('\?sf_options.*?options_sf','',action)
    if tv:
        se_title = "%s+S%02dE%02d" % (title,int(season),int(episode))
        action = re.sub('\[%SE%\]',se_title,action)
    else:
        action = re.sub('\[%SE%\]',title,action)
    action = re.sub('\[%SF%\]',title,action)
    p = re.search('plugin://(.*?)/',action)
    if p:
        plugin = p.group(1)
        if plugin in installed_addons:
            search_addons[name] = action
    
d = xbmcgui.Dialog()
names = sorted(search_addons.keys())
which = d.select('Search: %s' % orig_title,names)
if which > -1:
    xbmc.executebuiltin(search_addons[names[which]])

