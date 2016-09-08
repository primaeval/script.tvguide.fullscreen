# -*- coding: utf-8 -*-
#
#      Copyright (C) 2012 Tommy Winther
#      http://tommy.winther.nu
#
#      Modified for FTV Guide (09/2014 onwards)
#      by Thomas Geppert [bluezed] - bluezed.apps@gmail.com
#
#      Modified for TV Guide Fullscren (2016)
#      by primaeval - primaeval.dev@gmail.com
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
import datetime
import os
import xbmc
import xbmcgui, xbmcaddon, xbmcvfs
import source as src

from strings import *

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')


class Autoplaywith(object):
    def __init__(self, database, addonPath):
        """
        @param database: source.Database
        """
        self.database = database
        self.addonPath = addonPath
        self.icon = os.path.join(self.addonPath, 'icon.png')

    def createAlarmClockName(self, programTitle, startTime):
        return 'tvguide-%s-%s' % (programTitle, startTime)

    def scheduleAutoplaywiths(self):
        for channelId, programTitle, startTime, endTime in self.database.getAutoplaywiths():
            self.writeNfoFile(program)
            self._scheduleAutoplaywith(channelId, programTitle, startTime, endTime)

    def _scheduleAutoplaywith(self, channelId, programTitle, startTime, endTime):
        t = startTime - datetime.datetime.now()
        timeToAutoplaywith = ((t.days * 86400) + t.seconds) / 60
        if timeToAutoplaywith < 0:
            return
        #timeToAutoplaywith = 1
        name = self.createAlarmClockName(programTitle, startTime)
        #TODO
        description = strings(NOTIFICATION_5_MINS, channelId)
        xbmc.executebuiltin('AlarmClock(%s-5mins,Autoplaywith(%s,%s,10000,%s),%d,True)' %
            (name.encode('utf-8', 'replace'), programTitle.encode('utf-8', 'replace'), description.encode('utf-8', 'replace'), self.icon, timeToAutoplaywith - 5))
        xbmc.executebuiltin('AlarmClock(%s-start,RunScript(special://home/addons/script.tvguide.fullscreen/playwith.py,%s,%s),%d,True)' %
        (name.encode('utf-8', 'replace'), channelId.encode('utf-8'), startTime, timeToAutoplaywith - int(ADDON.getSetting('autoplaywiths.before'))))

        t = endTime - datetime.datetime.now()
        timeToAutoplaywith = ((t.days * 86400) + t.seconds) / 60
        #timeToAutoplaywith = 0
        if ADDON.getSetting('autoplaywiths.stop') == 'true':
            xbmc.executebuiltin('AlarmClock(%s-stop,RunScript(special://home/addons/script.tvguide.fullscreen/stopwith.py,%s,%s),%d,True)' %
            (name.encode('utf-8', 'replace'), channelId.encode('utf-8'), startTime, timeToAutoplaywith + int(ADDON.getSetting('autoplaywiths.after'))))


    def _unscheduleAutoplaywith(self, programTitle, startTime):
        name = self.createAlarmClockName(programTitle, startTime)
        xbmc.executebuiltin('CancelAlarm(%s-5mins,True)' % name.encode('utf-8', 'replace'))
        xbmc.executebuiltin('CancelAlarm(%s-start,True)' % name.encode('utf-8', 'replace'))
        xbmc.executebuiltin('CancelAlarm(%s-stop,True)' % name.encode('utf-8', 'replace'))

    def addAutoplaywith(self, program,type):
        self.database.addAutoplaywith(program,type)
        self.writeNfoFile(program)
        self._scheduleAutoplaywith(program.channel.id, program.title, program.startDate, program.endDate)

    def removeAutoplaywith(self, program):
        self.database.removeAutoplaywith(program)
        self._unscheduleAutoplaywith(program.title, program.startDate)

    def writeNfoFile(self,program):
        folder = "special://profile/addon_data/script.tvguide.fullscreen/programs"
        xbmcvfs.mkdirs(folder)
        timestamp = program.startDate.strftime("%Y%m%d%H%M")
        filename = "%s - %s - %s" % (timestamp,program.channel.title,program.title)
        f = xbmcvfs.File('%s/%s.ini' % (folder,filename), "wb")
        f.write(u'\ufeff'.encode("utf8"))
        s = "channel.id=%s\n" % program.channel.id
        f.write(s.encode("utf8"))
        s = "channel.title=%s\n" % program.channel.title
        f.write(s.encode("utf8"))
        s = "channel.logo=%s\n" % program.channel.logo
        f.write(s.encode("utf8"))
        s = "program.title=%s\n" % program.title
        f.write(s.encode("utf8"))
        s = "program.startDate=%s\n" % program.startDate
        f.write(s.encode("utf8"))
        s = "program.endDate=%s\n" % program.endDate
        f.write(s.encode("utf8"))
        s = "program.description=%s\n" % program.description
        f.write(s.encode("utf8"))
        s = "program.imageLarge=%s\n" % program.imageLarge
        f.write(s.encode("utf8"))
        s = "program.imageSmall=%s\n" % program.imageSmall
        f.write(s.encode("utf8"))
        s = "program.episode=%s\n" % program.episode
        f.write(s.encode("utf8"))
        s = "program.season=%s\n" % program.season
        f.write(s.encode("utf8"))
        s = "program.is_movie=%s\n" % program.is_movie
        f.write(s.encode("utf8"))
        s = "autoplays.before=%s\n" % ADDON.getSetting('autoplays.before')
        f.write(s.encode("utf8"))
        s = "autoplays.after=%s\n" % ADDON.getSetting('autoplays.after')
        f.write(s.encode("utf8"))


if __name__ == '__main__':
    database = src.Database()

    def onAutoplaywithsCleared():
        xbmcgui.Dialog().ok(strings(CLEAR_NOTIFICATIONS), strings(DONE)) #TODO

    def onInitialized(success):
        if success:
            database.clearAllAutoplaywiths()
            database.close(onAutoplaywithsCleared)
            ADDON.setSetting('playing.channel','')
            ADDON.setSetting('playing.start','')
        else:
            database.close()

    database.initialize(onInitialized)
