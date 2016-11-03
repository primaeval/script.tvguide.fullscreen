import xbmcaddon
import notification
import autoplay
import autoplaywith
import xbmc,xbmcvfs
import source
import time
import requests
import base64

def getCustomStreamUrls(success):
    if success:
        stream_urls = database.getCustomStreamUrls()
        file_name = 'special://profile/addon_data/script.tvguide.fullscreen/custom_stream_urls.ini'
        f = xbmcvfs.File(file_name,'wb')
        for (name,stream) in stream_urls:
            write_str = "%s=%s\n" % (name,stream)
            f.write(write_str.encode("utf8"))
        f.close()
    else:
        database.close()

def setCustomStreamUrls(success):
    if success:
        file_name = 'special://profile/addon_data/script.tvguide.fullscreen/custom_stream_urls.ini'
        f = xbmcvfs.File(file_name)
        lines = f.read().splitlines()
        stream_urls = [line.split("=") for line in lines]
        f.close()
        database.setCustomStreamUrls(stream_urls)
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