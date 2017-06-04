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
import xbmcaddon
import os
import urllib2
import datetime,time
import zlib
import gzip
import requests
import hashlib

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')

def log(x):
    xbmc.log(repr(x))


class FileFetcher(object):
    INTERVAL_ALWAYS = 0
    INTERVAL_12 = 1
    INTERVAL_24 = 2
    INTERVAL_48 = 3
    INTERVAL_7 = 4
    INTERVAL_14 = 5

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

    def __init__(self, url, path, addon):
        self.addon = addon

        if url.startswith("http://") or url.startswith("sftp://") or url.startswith("ftp://") or \
                url.startswith("https://") or url.startswith("ftps://") :
            self.fileType = self.TYPE_REMOTE
            self.fileUrl = url
            self.fileName = path.split('/')[-1]
            self.filePath = path
        else:
            self.fileType = self.TYPE_DEFAULT
            self.fileUrl = url
            self.fileName = path.split('/')[-1]
            self.filePath = path

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
                        (interval == self.INTERVAL_48 and diff >= 172800) or
                        (interval == self.INTERVAL_7 and diff >= 604800) or
                        (interval == self.INTERVAL_14 and diff >= 1209600)):
                    fetch = True
            else:
                fetch = True

        if fetch:
            user = ''
            password = ''
            new_md5 = ''
            auth = None
            if self.addon.getSetting('authentication') == 'true':
                user = self.addon.getSetting('user')
                password = self.addon.getSetting('password')
                auth = (user, password)
            tmpFile = os.path.join(self.basePath, self.fileName+'.tmp')
            if self.fileType == self.TYPE_DEFAULT:
                xbmc.log('[script.tvguide.fullscreen] file is in remote location: %s' % self.fileUrl, xbmc.LOGDEBUG)
                if xbmcvfs.exists(self.filePath):
                    st = xbmcvfs.Stat(self.fileUrl)
                    src_modified = st.st_mtime()
                    st = xbmcvfs.Stat(self.filePath)
                    dst_modified = st.st_mtime()
                    if src_modified <= dst_modified:
                        return self.FETCH_NOT_NEEDED
                if not xbmcvfs.copy(self.fileUrl, tmpFile):
                    xbmc.log('[script.tvguide.fullscreen] Remote file couldn\'t be copied: %s' % self.fileUrl, xbmc.LOGERROR)
            else:

                if self.addon.getSetting('md5') == 'true':
                    file = self.filePath+".md5"
                    url = self.fileUrl+".md5"
                    old_md5 = xbmcvfs.File(file,"rb").read()
                    try:
                        r = requests.get(url,auth=auth)
                        if r.status_code == requests.codes.ok:
                            new_md5 = r.text.encode('ascii', 'ignore')[:32]
                    except Exception as detail:
                        xbmc.log('[script.tvguide.fullscreen] Missing md5: %s.md5 (%s)' % (self.fileUrl,detail), xbmc.LOGERROR)
                    #log((old_md5,new_md5))
                    if old_md5 and (old_md5 == new_md5) and (self.addon.getSetting('xmltv.refresh') == 'false'):
                        return self.FETCH_NOT_NEEDED
                f = open(tmpFile, 'wb')
                xbmc.log('[script.tvguide.fullscreen] file is on the internet: %s' % self.fileUrl, xbmc.LOGDEBUG)
                total = 0
                fileUrl = self.fileUrl
                if ADDON.getSetting('gz') == 'true':
                    fileUrl = fileUrl + '.gz'
                try:
                    r = requests.get(fileUrl,auth=auth, stream=True, verify=False)
                    if r.status_code != requests.codes.ok:
                        if ADDON.getSetting('gz') == 'true':
                            r = requests.get(self.fileUrl,auth=auth, stream=True, verify=False)
                            if r.status_code != requests.codes.ok:
                                xbmc.log('[script.tvguide.fullscreen] no file: %s' % self.fileUrl, xbmc.LOGERROR)
                                xbmcgui.Dialog().notification("TV Guide Fullscreen", "bad status code %s" % self.fileUrl,xbmcgui.NOTIFICATION_ERROR)
                        else:
                            xbmc.log('[script.tvguide.fullscreen] no file: %s' % fileUrl, xbmc.LOGERROR)
                            xbmcgui.Dialog().notification("TV Guide Fullscreen", "bad status code %s " % fileUrl,xbmcgui.NOTIFICATION_ERROR)
                            return self.FETCH_NOT_NEEDED
                    if "Content-Length" in r.headers:
                        total = int(r.headers['Content-Length'])
                except Exception as detail:
                    xbmc.log('[script.tvguide.fullscreen] bad request: %s (%s)' % (fileUrl,detail), xbmc.LOGERROR)
                    xbmcgui.Dialog().notification("TV Guide Fullscreen", "failed to download %s " % fileUrl,xbmcgui.NOTIFICATION_ERROR)
                    return self.FETCH_NOT_NEEDED

                title = fileUrl.split('/')[-1]
                d = xbmcgui.DialogProgressBG()
                d.create('TV Guide Fullscreen', 'downloading %s' % title)
                chunk_size = 16 * 1024
                size = 0
                oldtime = time.time()
                for chunk in r.iter_content(chunk_size):
                    f.write(chunk)
                    size = size + chunk_size
                    if total:
                        percent = 100.0 * size / total
                        now = time.time()
                        diff = now - oldtime
                        if diff > 1:
                            d.update(int(percent))
                            oldtime = now
                f.close()
                d.update(100, message="Done")
                d.close()
            if os.path.exists(self.filePath):
                try:
                    os.remove(self.filePath)
                except:
                    return self.FETCH_NOT_NEEDED
            try:
                magic = xbmcvfs.File(tmpFile,"rb").read(3)
                if magic == "\x1f\x8b\x08":
                    g = gzip.open(tmpFile)
                    data = g.read()
                    xbmcvfs.File(self.filePath,"wb").write(data)
                else:
                    xbmcvfs.copy(tmpFile, self.filePath)
                xbmcvfs.delete(tmpFile)
            except:
                return self.FETCH_NOT_NEEDED
            if new_md5 and (self.addon.getSetting('md5') == 'true'):
                md5 = hashlib.md5()
                md5.update(xbmcvfs.File(self.filePath,"rb").read())
                md5_file = md5.hexdigest()
                if md5_file != new_md5:
                    xbmc.log('[script.tvguide.fullscreen] md5 mismatch: %s calculated:%s server:%s' % (self.fileUrl,md5_file,new_md5), xbmc.LOGERROR)
                    xbmcgui.Dialog().notification("TV Guide Fullscreen", "failed md5 check %s",xbmcgui.NOTIFICATION_ERROR)
                else:
                    xbmcvfs.File(self.filePath+".md5","wb").write(new_md5)
            retVal = self.FETCH_OK
            xbmc.log('[script.tvguide.fullscreen] file %s was downloaded' % self.filePath, xbmc.LOGDEBUG)
        return retVal