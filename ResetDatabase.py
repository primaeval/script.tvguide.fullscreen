# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Sean Poyser and Richard Dean (write2dixie@gmail.com)
#
#      Modified for FTV Guide (09/2014 onwards)
#      by Thomas Geppert [bluezed] - bluezed.apps@gmail.com
#
#      Modified for TV Guide Fullscreen (2016)
#      by primaeval - primaeval.dev@gmail.com
#
# This Program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This Program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with XBMC; see the file COPYING. If not, write to
# the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# http://www.gnu.org/copyleft/gpl.html
#

import os
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs

def deleteDB():
    try:
        xbmc.log("[script.tvguide.fullscreen] Deleting database...", xbmc.LOGDEBUG)
        dbPath = xbmc.translatePath(xbmcaddon.Addon(id = 'script.tvguide.fullscreen').getAddonInfo('profile'))
        dbPath = os.path.join(dbPath, 'source.db')

        delete_file(dbPath)

        passed = not os.path.exists(dbPath)

        if passed:
            xbmc.log("[script.tvguide.fullscreen] Deleting database...PASSED", xbmc.LOGDEBUG)
        else:
            xbmc.log("[script.tvguide.fullscreen] Deleting database...FAILED", xbmc.LOGDEBUG)

        return passed

    except Exception, e:
        xbmc.log('[script.tvguide.fullscreen] Deleting database...EXCEPTION', xbmc.LOGDEBUG)
        return False

def delete_file(filename):
    tries = 10
    while os.path.exists(filename) and tries > 0:
        try:
            os.remove(filename)
            break
        except:
            tries -= 1

if __name__ == '__main__':
    if len(sys.argv) > 1:
        mode = int(sys.argv[1])

        if mode in [1,2]:
            if deleteDB():
                d = xbmcgui.Dialog()
                d.ok('TV Guide', 'The database has been successfully deleted.', 'It will be re-created next time you start the guide')
            else:
                d = xbmcgui.Dialog()
                d.ok('TV Guide', 'Failed to delete database.', 'Database may be locked,', 'please restart and try again')
        if mode == 2:
            xbmcvfs.delete('special://profile/addon_data/script.tvguide.fullscreen/addons.ini')
            xbmcvfs.delete('special://profile/addon_data/script.tvguide.fullscreen/categories.ini')
            xbmcvfs.delete('special://profile/addon_data/script.tvguide.fullscreen/custom_stream_urls.ini')
            xbmcvfs.delete('special://profile/addon_data/script.tvguide.fullscreen/mapping.ini')
            xbmcvfs.delete('special://profile/addon_data/script.tvguide.fullscreen/icons.ini')
            xbmcvfs.delete('special://profile/addon_data/script.tvguide.fullscreen/folders.list')
            xbmcvfs.delete('special://profile/addon_data/script.tvguide.fullscreen/tvdb.pickle')
            xbmcvfs.delete('special://profile/addon_data/script.tvguide.fullscreen/tvdb_banners.pickle')
            path = 'special://profile/addon_data/script.tvguide.fullscreen/'
            dirs, files = xbmcvfs.listdir(path)
            for f in files:
                if (f.endswith('xml') or f.endswith('xmltv')) and f != "settings.xml":
                    xbmcvfs.delete(path+f)
        if mode == 3:
            xbmcvfs.delete('special://profile/addon_data/script.tvguide.fullscreen/tvdb.pickle')
            xbmcvfs.delete('special://profile/addon_data/script.tvguide.fullscreen/tvdb_banners.pickle')
        if mode in [2,4]:
            dirs, files = xbmcvfs.listdir('special://profile/addon_data/script.tvguide.fullscreen/logos')
            for f in files:
                xbmcvfs.delete('special://profile/addon_data/script.tvguide.fullscreen/logos/%s' % f)