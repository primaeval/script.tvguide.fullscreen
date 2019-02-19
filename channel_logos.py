import datetime
import os
import xbmc
import xbmcgui, xbmcaddon,xbmcvfs
import re
import source as src

from strings import *

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')


if __name__ == '__main__':
    database = src.Database()

    def onAutoplaysCleared():
        pass

    def onInitialized(success):
        if success:
            channelList = database.getChannelList(onlyVisible=False)
            xbmcvfs.mkdirs("special://profile/addon_data/script.tvguide.fullscreen/channel_logos/")
            for channel in channelList:
                from_file = channel.logo
                regex = '[%s]' % re.escape('[]/\:')
                xbmc.log(regex)
                ext = from_file.rsplit('.',1)[-1]
                to_file = "special://profile/addon_data/script.tvguide.fullscreen/channel_logos/%s.%s" % (re.sub(regex,' ',channel.title),ext)
                xbmcvfs.copy(from_file,to_file)
            database.close(onAutoplaysCleared)
        else:
            database.close()

    database.initialize(onInitialized)
    xbmcgui.Dialog().notification("TV Guide Fullscreen","channels downloaded to addon_data")
