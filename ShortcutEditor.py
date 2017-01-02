import os
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import json

file_name = 'special://profile/addon_data/script.tvguide.fullscreen/channel_id_shortcut.ini'
f = xbmcvfs.File(file_name,'rb')
data = f.read()
f.close()
id_shortcuts = {}
if data:
    lines = data.splitlines()
    for line in lines:
        id_shortcut = line.split("=")
        if len(id_shortcut) == 2:
            id_shortcuts[id_shortcut[0]] = id_shortcut[1]

d = xbmcgui.Dialog()
while True:
    ids = sorted(id_shortcuts.keys())
    labels = ["%s - %s" % (x, id_shortcuts[x]) for x in ids]
    which = d.select("Shortcut Editor (id - numeric shortcut)",labels)
    if which == -1:
        f = xbmcvfs.File(file_name,'wb')
        for id in sorted(id_shortcuts):
            f.write("%s=%s\n" % (id.encode("utf8"),id_shortcuts[id].encode("utf8")))
        f.close()
        break
    id = ids[which]
    shortcut = d.input("New Shortcut (%s)" % labels[which], id_shortcuts[id])
    if shortcut:
        id_shortcuts[id] = shortcut