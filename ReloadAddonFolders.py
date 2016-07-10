import os
import re
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
from rpc import RPC

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')

file_name = 'special://profile/addon_data/script.tvguide.fullscreen/folders.list'
f = xbmcvfs.File(file_name)
items = f.read().splitlines()
f.close()
unique = set(items)

file_name = 'special://profile/addon_data/script.tvguide.fullscreen/addons.ini'
if int(ADDON.getSetting('addons.ini.type')) == 1:
    customFile = str(ADDON.getSetting('addons.ini.file'))
    if os.path.exists(customFile) and os.access(customFile,os.W_OK):
        file_name = customFile

plugins = {}
for path in unique:
    response = RPC.files.get_directory(media="files", directory=path, properties=["thumbnail"])
    files = response["files"]
    dirs = dict([[f["label"], f["file"]] for f in files if f["filetype"] == "directory"])
    links = dict([[f["label"], f["file"]] for f in files if f["filetype"] == "file"])
    
    plugin = re.match(r"plugin://(.*?)/",path).group(1)
    if plugin not in plugins:
        plugins[plugin] = {}
        
    streams = plugins[plugin]
    for label in links:
        file = links[label]
        streams[label] = file
        

f = xbmcvfs.File(file_name,'wb')
write_str = "# WARNING Make a copy of this file.\n# It will be overwritten on the next folder add.\n\n"
f.write(write_str.encode("utf8"))

for addonId in sorted(plugins):
    write_str = "[%s]\n" % (addonId)
    f.write(write_str)
    addonStreams = plugins[addonId]
    for name in sorted(addonStreams):
        stream = addonStreams[name]
        if name.startswith(' '):
            continue
        name = re.sub(r'[:=]',' ',name)
        if not stream:
            stream = 'nothing'
        write_str = "%s=%s\n" % (name,stream)
        f.write(write_str.encode("utf8"))
f.close()
