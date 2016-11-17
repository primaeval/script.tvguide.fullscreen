# -*- coding: utf-8 -*-
#
# FTV Guide
# Copyright (C) 2015 Thomas Geppert [bluezed]
# bluezed.apps@gmail.com
#
#      Modified for TV Guide Fullscren (2016)
#      by primaeval - primaeval.dev@gmail.com
#
# This Program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
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
import xbmc
import xbmcvfs
import xbmcgui
import os
import urllib2
import datetime
import zlib
import requests
import hashlib



class FileFetcher(object):
    INTERVAL_ALWAYS = 0
    INTERVAL_12 = 1
    INTERVAL_24 = 2
    INTERVAL_48 = 3

    FETCH_ERROR = -1
    FETCH_NOT_NEEDED = 0
    FETCH_OK = 1

    TYPE_DEFAULT = 1
    TYPE_REMOTE = 2

    basePath = xbmc.translatePath(os.path.join('special://profile', 'addon_data', 'script.tvguide.fullscreen'))
    filePath = ''
    fileUrl = ''
    addon = None
    fileType = TYPE_DEFAULT

    def __init__(self, fileName, addon):
        self.addon = addon

        if fileName.startswith("http://") or fileName.startswith("sftp://") or fileName.startswith("ftp://") or \
                fileName.startswith("https://") or fileName.startswith("ftps://") :
            self.fileType = self.TYPE_REMOTE
            self.fileUrl = fileName
            self.filePath = os.path.join(self.basePath, fileName.split('/')[-1])
        else:
            self.fileType = self.TYPE_DEFAULT
            self.fileUrl = fileName
            self.filePath = os.path.join(self.basePath,os.path.basename(fileName))

        # make sure the folder is actually there already!
        if not os.path.exists(self.basePath):
            os.makedirs(self.basePath)

    def fetchFile(self):
        retVal = self.FETCH_NOT_NEEDED
        fetch = False
        if not os.path.exists(self.filePath):  # always fetch if file doesn't exist!
            fetch = True
        elif self.addon.getSetting('background.service') == 'true':
            fetch = True
        else:
            interval = int(self.addon.getSetting('xmltv.interval'))
            if interval != self.INTERVAL_ALWAYS:
                modTime = datetime.datetime.fromtimestamp(os.path.getmtime(self.filePath))
                td = datetime.datetime.now() - modTime
                # need to do it this way cause Android doesn't support .total_seconds() :(
                diff = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6) / 10 ** 6
                if ((interval == self.INTERVAL_12 and diff >= 43200) or
                        (interval == self.INTERVAL_24 and diff >= 86400) or
                        (interval == self.INTERVAL_48 and diff >= 172800)):
                    fetch = True
            else:
                fetch = True

        if fetch:
            tmpFile = os.path.join(self.basePath, 'tmp')
            if self.fileType == self.TYPE_DEFAULT:
                xbmc.log('[script.tvguide.fullscreen] file is in remote location: %s' % self.fileUrl, xbmc.LOGDEBUG)
                if not xbmcvfs.copy(self.fileUrl, tmpFile):
                    xbmc.log('[script.tvguide.fullscreen] Remote file couldn\'t be copied: %s' % self.fileUrl, xbmc.LOGERROR)
            else:
                new_md5 = ''
                if self.addon.getSetting('md5') == 'true':
                    file = self.filePath+".md5"
                    old_md5 = xbmcvfs.File(file,"rb").read()
                    url = self.fileUrl+".md5"
                    try:
                        r = requests.get(url)
                    except:
                        return self.FETCH_ERROR
                    if r.status_code == requests.codes.ok:
                        new_md5 = r.text.encode('ascii', 'ignore')[:32]

                    if old_md5 and (old_md5 == new_md5) and (self.addon.getSetting('xmltv.refresh') == 'false'):
                        return self.FETCH_NOT_NEEDED
                f = open(tmpFile, 'wb')
                xbmc.log('[script.tvguide.fullscreen] file is on the internet: %s' % self.fileUrl, xbmc.LOGDEBUG)
                try:
                    r = requests.get(self.fileUrl)
                except:
                    return self.FETCH_ERROR
                if r.status_code != requests.codes.ok:
                    return self.FETCH_NOT_ERROR
                chunk_size = 16 * 1024
                if new_md5 and (self.addon.getSetting('md5') == 'true'):
                    md5 = hashlib.md5()
                    for chunk in r.iter_content(chunk_size):
                        f.write(chunk)
                        md5.update(chunk)
                    f.close()
                    md5_file = md5.hexdigest()
                    if md5_file != new_md5:
                        return self.FETCH_ERROR
                        d = xbmcgui.Dialog()
                        d.notification('TV Guide Fullscreen', 'md5 Error: %s' % self.fileUrl.split('/')[-1], xbmcgui.NOTIFICATION_ERROR, 10000)
                    else:
                        xbmcvfs.File(self.filePath+".md5","wb").write(new_md5)
                else:
                    for chunk in r.iter_content(chunk_size):
                        f.write(chunk)
                    f.close()
            if os.path.exists(self.filePath):
                os.remove(self.filePath)
            os.rename(tmpFile, self.filePath)
            retVal = self.FETCH_OK
            xbmc.log('[script.tvguide.fullscreen] file %s was downloaded' % self.filePath, xbmc.LOGDEBUG)
        return retVal