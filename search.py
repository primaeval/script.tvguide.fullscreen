import sys
import xbmc,xbmcaddon,xbmcvfs,xbmcgui
import sqlite3
import re
import urllib
from HTMLParser import HTMLParser
from rpc import RPC
import requests

def log(x):
    xbmc.log(repr(x))

def getTVDBId(title):
    orig_title = title
    try: title = title.encode("utf8")
    except: title = unicode(title)
    url = "http://thetvdb.com/?string=%s&searchseriesid=&tab=listseries&function=Search" % urllib.quote_plus(title)
    try:
        html = requests.get(url).content
    except:
        return
    match = re.search('<a href="(/\?tab=series&amp;id=(.*?))">(.*?)</a>',html)
    tvdb_url = ''
    if match:
        id = match.group(2)
        return id

def getIMDBId(title, year):
    orig_title = "%s (%s)" % (title,year)
    try: utf_title = orig_title.encode("utf8")
    except: utf_title = unicode(utf_title)
    headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'}
    url = "http://www.bing.com/search?q=site%%3Aimdb.com+%s" % urllib.quote_plus(utf_title)
    try: html = requests.get(url).content
    except: return

    match = re.search('href="(http://www.imdb.com/title/(tt.*?)/)".*?<strong>(.*?)</strong>',html)
    tvdb_url = ''
    if match:
        id = match.group(2)
        return id


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
year = None
match = re.search('(.*?)\(([0-9]{4})\)$',orig_title)
if match:
    orig_title = match.group(1).strip()
    year = match.group(2)
title = urllib.quote_plus(orig_title)

tvdb = None
imdb = None
if tv:
    tvdb = getTVDBId(title)
elif year:
    imdb = getIMDBId(title,year)

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
        action = re.sub('\[%SE%\]',episode,action)
        action = re.sub('\[%SS%\]',season,action)
        if tvdb:
            action = re.sub('\[%ST%\]',tvdb,action)
            year = "0" #TODO tv show year
            action = re.sub('\[%SY%\]',year,action)
    else:
        if imdb:
            action = re.sub('\[%SI%\]',imdb,action)
            action = re.sub('\[%SY%\]',year,action)
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
    url = search_addons[names[which]]
    if url.startswith("plugin://"):
        xbmc.Player().play(item=url)
    else:
        xbmc.executebuiltin(url)

