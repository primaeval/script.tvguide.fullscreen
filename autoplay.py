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
import xbmcgui
import source as src

from strings import *


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
        for channelTitle, programTitle, startTime in self.database.getAutoplays():
            self._scheduleAutoplay(channelTitle, programTitle, startTime)

    def _scheduleAutoplay(self, channelTitle, programTitle, startTime):
        t = startTime - datetime.datetime.now()
        timeToAutoplay = ((t.days * 86400) + t.seconds) / 60
        if timeToAutoplay < 0:
            return

        name = self.createAlarmClockName(programTitle, startTime)
        #TODO
        description = strings(NOTIFICATION_5_MINS, channelTitle)
        xbmc.executebuiltin('AlarmClock(%s-5mins,Autoplay(%s,%s,10000,%s),%d,True)' %
            (name.encode('utf-8', 'replace'), programTitle.encode('utf-8', 'replace'), description.encode('utf-8', 'replace'), self.icon, timeToAutoplay - 5))
        #TODO
        description = strings(NOTIFICATION_NOW, channelTitle)
        xbmc.executebuiltin('AlarmClock(%s-now,Autoplay(%s,%s,10000,%s),%d,True)' %
                            (name.encode('utf-8', 'replace'), programTitle.encode('utf-8', 'replace'), description.encode('utf-8', 'replace'), self.icon, timeToAutoplay))

    def _unscheduleAutoplay(self, programTitle, startTime):
        name = self.createAlarmClockName(programTitle, startTime)
        xbmc.executebuiltin('CancelAlarm(%s-5mins,True)' % name.encode('utf-8', 'replace'))
        xbmc.executebuiltin('CancelAlarm(%s-now,True)' % name.encode('utf-8', 'replace'))

    def addAutoplay(self, program):
        self.database.addAutoplay(program)
        self._scheduleAutoplay(program.channel.title, program.title, program.startDate)

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
        else:
            database.close()

    database.initialize(onInitialized)
