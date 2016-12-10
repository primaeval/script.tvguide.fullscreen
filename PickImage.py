import os
import re
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import requests
import json
import sys
from rpc import RPC

location = sys.argv[1]
setting = sys.argv[2]

def log(x):
    xbmc.log(repr(x))

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')

d = xbmcgui.Dialog()

if location == "both":
    places = ["Local","Pixabay"]
elif location == "remote":
    places = ["Pixabay"]
else:
    places = ["Local"]

where = d.select("Image Search",places)
if where == -1:
     quit()
place = places[where]
if place == "Local":
    image = d.browse(2, 'Image', 'files', '', True, False)
    if image:
        ADDON.setSetting(setting,image)

elif place == "Pixabay":
    what = d.input("PixaBay Image Search","background")
    if not what:
        quit()

    url = "https://pixabay.com/api/?key=3974133-0e761ef66bcfb72c6a8ac8f4e&q=%s&image_type=photo&pretty=true&orientation=horizontal&per_page=200" % what
    r = requests.get(url)
    j = json.loads(r.content)
    if not 'hits' in j:
        quit()

    dirs, files = xbmcvfs.listdir('special://profile/addon_data/script.tvguide.fullscreen/pick/')
    for f in files:
        path = 'special://profile/addon_data/script.tvguide.fullscreen/pick/'+f
        success = xbmcvfs.delete(path)

    hits = j['hits']
    images = {}
    p = xbmcgui.DialogProgressBG()
    p.create("Finding Images","...")
    total = len(hits)
    i = 0
    for h in hits:
        url = h["previewURL"].replace(': //','://')
        basename= url.rsplit('/',1)[-1]
        localfile = 'special://profile/addon_data/script.tvguide.fullscreen/pick/'+basename
        xbmcvfs.copy(url,localfile)
        image = h["webformatURL"].replace(': //','://')
        if image:
            images[localfile] = image
        percent = 100.0 * i / total
        i = i + 1
        p.update(int(percent),"Finding Images",basename)
    p.close()

    what = d.browse(2, 'Image', 'files', '', True, False, 'special://profile/addon_data/script.tvguide.fullscreen/pick/')
    image = images.get(what,'')
    if image:
        ADDON.setSetting(setting,image)