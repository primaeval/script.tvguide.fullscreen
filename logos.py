import os
import re
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import urllib
import requests
from rpc import RPC

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')

file_name = 'special://profile/addon_data/script.tvguide.fullscreen/folders.list'
f = xbmcvfs.File(file_name)
items = f.read().splitlines()
f.close()
unique = set(items)

logos = {}
for path in unique:
    try:
        response = RPC.files.get_directory(media="files", directory=path, properties=["thumbnail"])
    except:
        continue
    files = response["files"]
    #dirs = dict([[f["label"], f["file"]] for f in files if f["filetype"] == "directory"])
    #links = dict([[f["label"], f["file"]] for f in files if f["filetype"] == "file"])
    thumbnails = dict([[f["label"], f["thumbnail"]] for f in files if f["filetype"] == "file"])
    match = re.match(r"plugin://(.*?)/",path)
    if match:
        plugin = match.group(1)
    else:
        match = re.match(r"plugin://(.*?)$",path)
        if match:
            plugin = match.group(1)
        else:
            continue

    if plugin not in logos:
        logos[plugin] = {}

    thumbs = logos[plugin]
    for file in thumbnails:
        thumb = thumbnails[file]
        thumbs[file] = thumb
logo_folder = 'special://profile/addon_data/script.tvguide.fullscreen/addon_logos/'
for addonId in sorted(logos):
    folder = 'special://profile/addon_data/script.tvguide.fullscreen/addon_logos/%s' % addonId
    xbmcvfs.mkdirs(folder)
    addonLogos = logos[addonId]
    for label in sorted(addonLogos):
        logo = addonLogos[label]
        if logo:
            label = re.sub(r'[:/\\]', '',label)
            label = label.strip()
            label = re.sub(r"\[/?[BI]\]",'',label)
            label = re.sub(r"\[/?COLOR.*?\]",'',label)
            logo = re.sub(r'^image://','',logo)
            logo = urllib.unquote_plus(logo)
            logo = logo.strip('/')
            file_name = "%s/%s.png" % (folder,label)
            if not xbmcvfs.exists(file_name):
                try:
                    r = requests.get(logo)
                    if r.status_code == 200:
                        f = xbmcvfs.File(file_name, 'wb')
                        chunk_size = 16 * 1024
                        for chunk in r.iter_content(chunk_size):
                            f.write(chunk)
                        f.close()
                except Exception as detail:
                    xbmcvfs.copy(logo,file_name)


dialog = xbmcgui.Dialog()
dialog.notification("TV Guide Fullscreen","Done: Download Logos")
