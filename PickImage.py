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

setting = sys.argv[1]

def log(x):
    xbmc.log(repr(x))

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')

d = xbmcgui.Dialog()

where = d.select("Image Search",["Local","Pixabay"])
if where == -1:
     quit()

if where == 0:
    image = d.browse(2, 'Image', 'files', '', True, False)
    if image:
        ADDON.setSetting(setting,image)

elif where == 1:
    what = d.input("PixaBay Image Search","background")
    if not what:
        quit()

    url = "https://pixabay.com/api/?key=3974133-0e761ef66bcfb72c6a8ac8f4e&q=%s&image_type=photo&pretty=true&orientation=horizontal&per_page=200" % what
    r = requests.get(url)
    j = json.loads(r.content)
    log(j)
    if not 'hits' in j:
        quit()

    dirs, files = xbmcvfs.listdir('special://profile/addon_data/script.tvguide.fullscreen/pick/')
    for f in files:
        path = 'special://profile/addon_data/script.tvguide.fullscreen/pick/'+f
        success = xbmcvfs.delete(path)
        log((success,path))

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
    log(image)
    if image:
        ADDON.setSetting(setting,image)