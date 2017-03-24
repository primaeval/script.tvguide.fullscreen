# -*- coding: utf-8 -*-
#
#      Copyright (C) 2016 Thomas Geppert [bluezed] - bluezed.apps@gmail.com
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
import json
import os
from itertools import izip_longest

import xbmc
from strings import ADDON
from xml.etree import ElementTree as eT
import xml.etree.cElementTree as ceT
import re
import urllib
import xbmcgui
import xbmcvfs
import requests

LOGO_TYPE_DEFAULT = 0
LOGO_TYPE_CUSTOM = 1
DEFAULT_LOGO_URL = 'https://s3.amazonaws.com/schedulesdirect/assets/stationLogos/'


class SourceException(Exception):
    pass


class SourceUpdateCanceledException(SourceException):
    pass


class SourceNotConfiguredException(SourceException):
    pass


class Channel(object):
    def __init__(self, id, title, lineup, logo=None, streamUrl=None, visible=True, weight=-1):
        self.id = id
        self.title = title
        self.lineup = lineup
        self.logo = logo
        self.streamUrl = streamUrl
        self.visible = visible
        self.weight = weight

    def isPlayable(self):
        return hasattr(self, 'streamUrl') and self.streamUrl

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return 'Channel(id=%s, title=%s, lineup=%s, logo=%s, streamUrl=%s)' \
               % (self.id, self.title, self.lineup, self.logo, self.streamUrl)


class Program(object):
    def __init__(self, channel, title, sub_title, startDate, endDate, description, categories, imageLarge=None, imageSmall=None,
                 notificationScheduled=None, autoplayScheduled=None, autoplaywithScheduled=None, season=None, episode=None, is_movie = False, language = "en"):
        """

        @param channel:
        @type channel: source.Channel
        @param title:
        @param startDate:
        @param endDate:
        @param description:
        @param imageLarge:
        @param imageSmall:
        """
        self.channel = channel
        self.title = title
        self.sub_title = sub_title
        self.startDate = startDate
        self.endDate = endDate
        self.description = description
        self.categories = categories
        if imageLarge and imageLarge.startswith('http'):
            self.imageLarge = re.sub(' ','+',imageLarge)
        else:
            self.imageLarge = imageLarge
        if imageSmall and imageSmall.startswith('http'):
            self.imageSmall = re.sub(' ','+',imageSmall)
        else:
            self.imageSmall = imageSmall
        self.notificationScheduled = notificationScheduled
        self.autoplayScheduled = autoplayScheduled
        self.autoplaywithScheduled = autoplaywithScheduled
        self.season = season
        self.episode = episode
        self.is_movie = is_movie
        self.language = language

    def __repr__(self):
        return 'Program(channel=%s, title=%s, sub_title=%s, startDate=%s, endDate=%s, description=%s, categories=%s, imageLarge=%s, ' \
               'imageSmall=%s, episode=%s, season=%s, is_movie=%s)' % (self.channel, self.title, self.sub_title, self.startDate,
                                                                       self.endDate, self.description, self.categories, self.imageLarge,
                                                                       self.imageSmall, self.season, self.episode,
                                                                       self.is_movie)


def save_setting(key, value, is_list=False):

    xbmc.log('[%s] Tyring to save setting: key "%s" / value "%s"' %
             (ADDON.getAddonInfo('id'), key, str(value)), xbmc.LOGDEBUG)

    file_path = xbmc.translatePath(
        os.path.join(ADDON.getAddonInfo('profile'), 'settings.xml'))
    if not os.path.exists(file_path):
        generate_settings_file(file_path)
    tree = eT.parse(file_path)
    root = tree.getroot()
    updated = False
    for item in root.findall('setting'):
        if item.attrib['id'] == key:
            if is_list:
                cur_values = item.attrib['value']
                if not cur_values:
                    cur_values = []
                else:
                    cur_values = json.loads(cur_values)
                if isinstance(value, list):
                    for val in value:
                        if val not in cur_values:
                            cur_values.append(val)
                else:
                    if value not in cur_values:
                        cur_values.append(value)
                item.attrib['value'] = json.dumps(cur_values)
                ADDON.setSetting(key, cur_values)
            else:
                item.attrib['value'] = value
                ADDON.setSetting(key, value)
            updated = True
    if updated:
        tree.write(file_path)
    return True


def generate_settings_file(target_path):
    source_path = xbmc.translatePath(
        os.path.join(ADDON.getAddonInfo('path'), 'resources', 'settings.xml'))
    root_target = ceT.Element("settings")
    tree_source = eT.parse(source_path)
    root_source = tree_source.getroot()
    for item in root_source.findall('category'):
        for setting in item.findall('setting'):
            if 'id' in setting.attrib:
                value = ''
                if 'default' in setting.attrib:
                    value = setting.attrib['default']
                ceT.SubElement(root_target, 'setting', id=setting.attrib['id'], value=value)
    tree_target = ceT.ElementTree(root_target)
    f = open(target_path, 'w')
    tree_target.write(f)
    f.close()


def get_setting(key, is_list=False):
    value = ADDON.getSetting(key)
    if value and is_list:
        value = json.loads(value)
    elif is_list:
        value = []
    return value


def grouper(n, iterable, fillvalue=None):
    """ grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx """
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

#TODO this is wrong
def get_logo(channel):
    logo = channel.logo
    logo_type = int(ADDON.getSetting('logos.source'))
    if logo and logo_type == LOGO_TYPE_DEFAULT:
        return logo

    logo_location = ADDON.getSetting('logos.folder')
    if not logo and logo_type == LOGO_TYPE_DEFAULT:
        logo = DEFAULT_LOGO_URL + 's' + channel.id + '_h3_aa.png'
    elif logo_type == LOGO_TYPE_CUSTOM and not logo.startswith(logo_location):
        logo = logo_location + channel.title + '.png'
    return logo


def reset_playing():
    path = xbmc.translatePath(ADDON.getAddonInfo('profile'))
    if not os.path.exists(path):
        os.mkdir(path)
    proc_file = os.path.join(path, 'proc')
    f = open(proc_file, 'w')
    f.write('')
    f.close()

def autocrop_image(image, border = 0):
    from PIL import Image, ImageOps
    size = image.size
    bb_image = image
    bbox = bb_image.getbbox()
    if (size[0] == bbox[2]) and (size[1] == bbox[3]):
        bb_image=bb_image.convert("RGB")
        bb_image = ImageOps.invert(bb_image)
        bbox = bb_image.getbbox()
    image = image.crop(bbox)
    (width, height) = image.size
    width += border * 2
    height += border * 2
    ratio = float(width)/height
    cropped_image = Image.new("RGBA", (width, height), (0,0,0,0))
    cropped_image.paste(image, (border, border))
    #TODO find epg height
    logo_height = 450 / int(ADDON.getSetting('channels.per.page'))
    logo_height = logo_height - 2
    if ADDON.getSetting('program.channel.logo') == "false":
        cropped_image = cropped_image.resize((int(logo_height*ratio), logo_height),Image.ANTIALIAS)
    return cropped_image

def getLogo(title,ask=False,force=True):
    infile = xbmc.translatePath("special://profile/addon_data/script.tvguide.fullscreen/logos/temp.png")
    outfile = xbmc.translatePath("special://profile/addon_data/script.tvguide.fullscreen/logos/%s.png" % title)
    if not force and xbmcvfs.exists(outfile):
        return outfile
    xbmcvfs.mkdirs("special://profile/addon_data/script.tvguide.fullscreen/logos")
    db_url = "http://www.thelogodb.com/api/json/v1/4423/tvchannel.php?s=%s" % re.sub(' ','+',title)
    try: json = requests.get(db_url).json()
    except: pass
    if json and "channels" in json:
        channels = json["channels"]
        if channels:
            if ask:
                names = ["%s [%s]" % (c["strChannel"],c["strCountry"]) for c in channels]
                d = xbmcgui.Dialog()
                selected = d.select("Logo Source: %s" % title,names)
            else:
                selected = 0
            if selected > -1:
                logo = channels[selected]["strLogoWide"]

                if not logo:
                    return None
                logo = re.sub('^https','http',logo)
                data = requests.get(logo).content
                f = xbmcvfs.File("special://profile/addon_data/script.tvguide.fullscreen/logos/temp.png","wb")
                f.write(data)
                f.close()
                from PIL import Image, ImageOps
                image = Image.open(infile)
                border = 0
                image = autocrop_image(image, border)
                image.save(outfile)
                logo = outfile
                return logo
