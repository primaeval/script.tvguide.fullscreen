# -*- coding: utf-8 -*-
#
# TV Guide Fullscreen
# Copyright (C) 2016 primaeval.dev@gmail.com
#
#      Original for FTV Guide
#      bluezed.apps@gmail.com
#
#      Modified for TV Guide Fullscreen (2016)
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
            self.fileName = fileName.split('/')[-1]
            self.filePath = os.path.join(self.basePath, fileName.split('/')[-1])
        else:
            self.fileType = self.TYPE_DEFAULT
            self.fileUrl = fileName
            self.fileName = os.path.basename(fileName)
            self.filePath = os.path.join(self.basePath,os.path.basename(fileName))

        # make sure the folder is actually there already!
        if not os.path.exists(self.basePath):
            os.makedirs(self.basePath)

    def fetchFile(self,force=False):
        retVal = self.FETCH_NOT_NEEDED
        fetch = False
        if not os.path.exists(self.filePath):  # always fetch if file doesn't exist!
            fetch = True
        elif force == True:
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
            tmpFile = os.path.join(self.basePath, self.fileName+'.tmp')
            xbmc.log(tmpFile)
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
                        if r.status_code == requests.codes.ok:
                            new_md5 = r.text.encode('ascii', 'ignore')[:32]
                    except Exception as detail:
                        xbmc.log('[script.tvguide.fullscreen] Missing md5: %s.md5 (%s)' % (self.fileUrl,detail), xbmc.LOGERROR)
                    if old_md5 and (old_md5 == new_md5) and (self.addon.getSetting('xmltv.refresh') == 'false'):
                        return self.FETCH_NOT_NEEDED
                f = open(tmpFile, 'wb')
                xbmc.log('[script.tvguide.fullscreen] file is on the internet: %s' % self.fileUrl, xbmc.LOGDEBUG)
                try:
                    r = requests.get(self.fileUrl)
                    if r.status_code != requests.codes.ok:
                        xbmc.log('[script.tvguide.fullscreen] no file: %s' % self.fileUrl, xbmc.LOGERROR)
                        return self.FETCH_NOT_NEEDED
                except Exception as detail:
                    xbmc.log('[script.tvguide.fullscreen] bad request: %s (%s)' % (self.fileUrl,detail), xbmc.LOGERROR)
                    return self.FETCH_NOT_NEEDED
                chunk_size = 16 * 1024
                if new_md5 and (self.addon.getSetting('md5') == 'true'):
                    md5 = hashlib.md5()
                    for chunk in r.iter_content(chunk_size):
                        f.write(chunk)
                        md5.update(chunk)
                    f.close()
                    md5_file = md5.hexdigest()
                    if md5_file != new_md5:
                        xbmc.log('[script.tvguide.fullscreen] md5 mismatch: %s calculated:%s server:%s' % (self.fileUrl,md5_file,new_md5), xbmc.LOGERROR)
                    else:
                        xbmcvfs.File(self.filePath+".md5","wb").write(new_md5)
                else:
                    for chunk in r.iter_content(chunk_size):
                        f.write(chunk)
                    f.close()
            if os.path.exists(self.filePath):
                try:
                    os.remove(self.filePath)
                except:
                    return self.FETCH_NOT_NEEDED
            try:
                os.rename(tmpFile, self.filePath)
            except:
                return self.FETCH_NOT_NEEDED
            retVal = self.FETCH_OK
            xbmc.log('[script.tvguide.fullscreen] file %s was downloaded' % self.filePath, xbmc.LOGDEBUG)
        return retVal