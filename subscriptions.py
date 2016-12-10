import os
import re
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
from rpc import RPC

def log(x):
    xbmc.log(repr(x))

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')

file_name = 'special://profile/addon_data/script.tvguide.fullscreen/subscriptions.ini'
f = xbmcvfs.File(file_name,"rb")
data = f.read()
f.close()
name_sub = re.findall('(.*?)=(.*)',data)
name_sub = sorted(name_sub, key=lambda x: x[0].lower())
name_sub = [list(i) for i in name_sub]

while True:
    actions = ["Add", "Remove"] + ["%s [COLOR dimgrey]%s[/COLOR]" % (x[0],x[1]) for x in name_sub]
    d = xbmcgui.Dialog()
    action = d.select("Manage",actions)
    if action == -1:
        break
    elif action == 0:
        name = d.input("Name")
        if not name:
            break
        url = d.input("Url")
        if not url:
            break
        name_sub.append((name,url))
    elif action == 1:
        names = ["%s [COLOR dimgrey]%s[/COLOR]" % (x[0],x[1]) for x in name_sub]
        which = d.multiselect("Remove",names)
        name_sub = [v for i, v in enumerate(name_sub) if i not in which]
    else:
        new_name = d.input("Name (%s)" % actions[action],name_sub[action-2][0])
        if new_name:
            name_sub[action-2][0] = new_name
        new_url = d.input("Url (%s)" % actions[action],name_sub[action-2][1])
        if new_url:
            name_sub[action-2][1] = new_url

f = xbmcvfs.File(file_name,"wb")
for (name,url) in name_sub:
    s = "%s=%s\n" % (name,url)
    f.write(s)
f.close()