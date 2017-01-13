import xbmcaddon
import notification
import autoplay
import autoplaywith
import xbmc,xbmcvfs,xbmcgui
import source
import time
import requests
import base64

ADDON = xbmcaddon.Addon(id = 'script.tvguide.fullscreen')

def log(x):
    xbmc.log(repr(x))

def getCustomStreamUrls(success):
    if success:
        stream_urls = database.getCustomStreamUrls()
        file_name = 'special://profile/addon_data/script.tvguide.fullscreen/custom_stream_urls.ini'
        f = xbmcvfs.File(file_name,'wb')
        for (name,stream) in stream_urls:
            write_str = "%s=%s\n" % (name,stream)
            f.write(write_str.encode("utf8"))
        f.close()
        xbmcgui.Dialog().notification(ADDON.getAddonInfo('name'), 'Exported channel mappings')
    else:
        database.close()

def setCustomStreamUrls(success):
    if success:
        file_name = 'special://profile/addon_data/script.tvguide.fullscreen/custom_stream_urls.ini'
        f = xbmcvfs.File(file_name)
        lines = f.read().splitlines()
        stream_urls = [line.split("=",1) for line in lines]
        f.close()
        database.setCustomStreamUrls(stream_urls)
        xbmcgui.Dialog().notification(ADDON.getAddonInfo('name'), 'Imported channel mappings')
    else:
        database.close()

def getAltCustomStreamUrls(success):
    if success:
        stream_urls = database.getAltCustomStreamUrls()
        file_name = 'special://profile/addon_data/script.tvguide.fullscreen/alt_custom_stream_urls.tsv'
        f = xbmcvfs.File(file_name,'wb')
        for (name,title,stream) in stream_urls:
            write_str = "%s\t%s\t%s\n" % (name,title,stream)
            f.write(write_str.encode("utf8"))
        f.close()
        xbmcgui.Dialog().notification(ADDON.getAddonInfo('name'), 'Exported alternative channel mappings')
    else:
        database.close()

def setAltCustomStreamUrls(success):
    if success:
        file_name = 'special://profile/addon_data/script.tvguide.fullscreen/alt_custom_stream_urls.tsv'
        f = xbmcvfs.File(file_name)
        lines = f.read().splitlines()
        stream_urls = [line.split("\t",2) for line in lines]
        f.close()
        database.setAltCustomStreamUrls(stream_urls)
        xbmcgui.Dialog().notification(ADDON.getAddonInfo('name'), 'Imported alternative channel mappings')
    else:
        database.close()

def clearCustomStreamUrls(success):
    if success:
        database.clearCustomStreamUrls()
        xbmcgui.Dialog().notification(ADDON.getAddonInfo('name'), 'Cleared channel mappings')
    else:
        database.close()

def clearAltCustomStreamUrls(success):
    if success:
        database.clearAltCustomStreamUrls()
        xbmcgui.Dialog().notification(ADDON.getAddonInfo('name'), 'Cleared alternative channel mappings')
    else:
        database.close()

if __name__ == '__main__':
    database = source.Database()
    if len(sys.argv) > 1:
        mode = int(sys.argv[1])
        if mode in [1]:
            database.initialize(getCustomStreamUrls)
        elif mode in [2]:
            database.initialize(setCustomStreamUrls)
        elif mode in [3]:
            database.initialize(getAltCustomStreamUrls)
        elif mode in [4]:
            database.initialize(setAltCustomStreamUrls)
        elif mode in [5]:
            database.initialize(clearCustomStreamUrls)
        elif mode in [6]:
            database.initialize(clearAltCustomStreamUrls)