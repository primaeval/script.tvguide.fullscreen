# -*- coding: utf-8 -*-
#
#      Copyright (C) 2012 Tommy Winther
#      http://tommy.winther.nu
#
#      Modified for FTV Guide (09/2014 onwards)
#      by Thomas Geppert [bluezed] - bluezed.apps@gmail.com
#
#      Modified for TV Guide Fullscreen (2016)
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
import xbmcgui, xbmcaddon
import source as src

from strings import *

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')


class Autoplay(object):
    def __init__(self, database, addonPath):
        """
        @param database: source.Database
        """
        self.database = database
        self.addonPath = addonPath
        self.icon = os.path.join(self.addonPath, 'icon.png')

    def createAlarmClockName(self, programTitle, startTime):
        return 'tvguide-%s-%s' % (programTitle, startTime)
        
    def scheduleAutoplays(self):
        for program in self.database.getFullAutoplays():
            self._scheduleAutoplay(program.channel.id, program.title, program.startDate, program.endDate)


    def _scheduleAutoplay(self, channelId, programTitle, startTime, endTime):
        t = startTime - datetime.datetime.now()
        timeToAutoplay = ((t.days * 86400) + t.seconds) / 60
        if timeToAutoplay < 0:
            return
        #timeToAutoplay = 1
        name = self.createAlarmClockName(programTitle, startTime)
        xbmc.executebuiltin('AlarmClock(%s-start,RunScript(special://home/addons/script.tvguide.fullscreen/play.py,%s,%s),%d,True)' %
        (name.encode('utf-8', 'replace'), channelId.encode('utf-8'), startTime, timeToAutoplay - int(ADDON.getSetting('autoplays.before'))))

        t = endTime - datetime.datetime.now()
        timeToAutoplay = ((t.days * 86400) + t.seconds) / 60
        #timeToAutoplay = 0
        if ADDON.getSetting('autoplays.stop') == 'true':
            xbmc.executebuiltin('AlarmClock(%s-stop,RunScript(special://home/addons/script.tvguide.fullscreen/stop.py,%s,%s),%d,True)' %
            (name.encode('utf-8', 'replace'), channelId.encode('utf-8'), startTime, timeToAutoplay + int(ADDON.getSetting('autoplays.after'))))


    def _unscheduleAutoplay(self, programTitle, startTime):
        name = self.createAlarmClockName(programTitle, startTime)
        xbmc.executebuiltin('CancelAlarm(%s-start,True)' % name.encode('utf-8', 'replace'))
        xbmc.executebuiltin('CancelAlarm(%s-stop,True)' % name.encode('utf-8', 'replace'))

    def addAutoplay(self, program,type):
        self.database.addAutoplay(program,type)
        self._scheduleAutoplay(program.channel.id, program.title, program.startDate, program.endDate)

    def removeAutoplay(self, program):
        self.database.removeAutoplay(program)
        self._unscheduleAutoplay(program.title, program.startDate)


if __name__ == '__main__':
    database = src.Database()

    def onAutoplaysCleared():
        xbmcgui.Dialog().ok(strings(CLEAR_NOTIFICATIONS), strings(DONE)) #TODO

    def onInitialized(success):
        if success:
            database.clearAllAutoplays()
            database.close(onAutoplaysCleared)
            ADDON.setSetting('playing.channel','')
            ADDON.setSetting('playing.start','')
        else:
            database.close()

    database.initialize(onInitialized)
