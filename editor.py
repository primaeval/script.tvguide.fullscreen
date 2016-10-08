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
import hashlib
import sys

import source as src
import xbmcgui
from sdAPI import SdAPI
from utils import *

SKIN = get_setting('skin')
PATH = ADDON.getAddonInfo('path')

ACTION_PARENT_DIR = 9
KEY_NAV_BACK = 92

database = None


def login_popup(message=None):
    dialog = xbmcgui.Dialog()
    additional = 'Please enter your credentials or register if you don\'t have an account at ' \
                 'http://schedulesdirect.org'
    if message:
        additional = message
    ret = dialog.yesno('[COLOR red]EPG-Direct[/COLOR]',
                       'EPG-Direct requires that you have an account at SchedulesDirect.',
                       additional, '', 'Cancel', 'Login')
    if ret:
        ret = enter_credentials()
    else:
        close()
    return ret


def enter_credentials(is_change=False):
    global user, passw
    default_user = ''
    default_pass = ''
    if is_change:
        default_user = user
    keyb = xbmc.Keyboard(default_user, 'Enter Username')
    keyb.doModal()
    if keyb.isConfirmed():
        user = keyb.getText()
        keyb = xbmc.Keyboard(default_pass, 'Enter Password:', True)
        keyb.doModal()
        if keyb.isConfirmed():
            xbmcgui.Dialog().notification(ADDON.getAddonInfo('name'), 'Checking login...',
                                          os.path.join(PATH, 'icon.png'), 1500)
            passw = hashlib.sha1(keyb.getText().encode('utf-8')).hexdigest()
            sd = SdAPI(user=user, passw=passw)
            if sd.logged_in:
                save_setting('sd.username', user)
                save_setting('sd.password', passw)
                xbmcgui.Dialog().notification(ADDON.getAddonInfo('name'), 'Login saved',
                                              os.path.join(PATH, 'icon.png'), 2000)
                return True
    return False


def delete_lineup():
    global sd, database
    lineup_list = sd.get_user_lineups()
    if len(lineup_list) == 0:
        return
    lineups = []
    for lineup in lineup_list:
        lineups.append(lineup['name'])
    lineups = sorted(lineups, key=lambda s: s.lower())
    sel = xbmcgui.Dialog().select('Current lineups - Click to delete...', list=lineups)
    if sel >= 0:
        name = lineups[sel]
        sel_lineup = [x for x in lineup_list if x["name"] == name]
        if len(sel_lineup) > 0:
            sel_lineup = sel_lineup[0]
            yes_no = xbmcgui.Dialog().yesno(ADDON.getAddonInfo('name'),
                                            '[COLOR red]Deleting a lineup will also remove all '
                                            'channels associated with it![/COLOR]',
                                            'Do you want to continue?')
            if yes_no:
                xbmcgui.Dialog().notification(ADDON.getAddonInfo('name'), 'Deleting lineup...',
                                              os.path.join(PATH, 'icon.png'), 3000)
                if sd.delete_lineup(sel_lineup['lineup']):
                    database.deleteLineup(close, sel_lineup['lineup'])
                    xbmcgui.Dialog().notification(ADDON.getAddonInfo('name'), 'Lineup "%s" deleted' % name,
                                                  os.path.join(PATH, 'icon.png'), 5000)


def select_lineup():
    global sd
    status = 'You have %d / %d lineups' % (len(sd.lineups), sd.max_lineups)
    if sd.max_lineups - len(sd.lineups) < 1:
        xbmcgui.Dialog().ok(
            ADDON.getAddonInfo('name'), status,
            'To add a new one you need to first remove one of your lineups')
        return

    country_list = sd.get_countries()
    countries = []
    for country in country_list:
        countries.append(country['fullName'])
    countries = sorted(countries, key=lambda s: s.lower())
    sel = xbmcgui.Dialog().select('Select country - %s' % status, list=countries)
    if sel >= 0:
        name = countries[sel]
        sel_country = [x for x in country_list if x["fullName"] == name]
        if len(sel_country) > 0:
            sel_country = sel_country[0]
            keyb = xbmc.Keyboard(sel_country['postalCodeExample'], 'Enter Post Code')
            keyb.doModal()
            if keyb.isConfirmed():
                lineup_list = sd.get_lineups(country=sel_country["shortName"], postcode=keyb.getText())
                lineups = []
                saved_lineups = sd.lineups
                for lineup in lineup_list:
                    if lineup['lineup'] not in saved_lineups:
                        lineups.append(lineup['name'])
                lineups = sorted(lineups, key=lambda s: s.lower())
                sel = xbmcgui.Dialog().select('Select lineup - not showing already selected...',
                                              list=lineups)
                if sel >= 0:
                    name = lineups[sel]
                    sel_lineup = [x for x in lineup_list if x["name"] == name]
                    if len(sel_lineup) > 0:
                        sel_lineup = sel_lineup[0]
                        xbmcgui.Dialog().notification(ADDON.getAddonInfo('name'), 'Saving lineup...',
                                                      os.path.join(PATH, 'icon.png'), 3000)
                        if sd.save_lineup(sel_lineup['lineup']):
                            xbmcgui.Dialog().notification(ADDON.getAddonInfo('name'),
                                                          'Lineup "%s" saved' % name,
                                                          os.path.join(PATH, 'icon.png'), 5000)
                        else:
                            raise SourceException('Lineup could not be saved! '
                                                  'Check the log for details.')


def edit_channels():
    global sd
    lineup_list = sd.get_user_lineups()
    if len(lineup_list) == 0:
        return
    lineups = []
    for lineup in lineup_list:
        lineups.append(lineup['name'])
    lineups = sorted(lineups, key=lambda s: s.lower())
    sel = xbmcgui.Dialog().select('Select lineup', list=lineups)
    if sel >= 0:
        name = lineups[sel]
        sel_lineup = [x for x in lineup_list if x["name"] == name]
        if len(sel_lineup) > 0:
            sel_lineup = sel_lineup[0]
            d = StationsSelect(sel_lineup['lineup'])
            d.doModal()
            del d


class StationsSelect(xbmcgui.WindowXMLDialog):
    global database
    C_CHANNELS_LIST_SOURCE = 7000
    C_CHANNELS_LIST = 6000
    C_CHANNELS_SELECTION_VISIBLE = 6001
    C_CHANNELS_SELECTION = 6002
    C_CHANNELS_SAVE = 6003
    C_CHANNELS_CANCEL = 6004

    def __new__(cls, lineup):
        return super(StationsSelect, cls).__new__(cls, 'script-tvguide-stations.xml',
                                                  ADDON.getAddonInfo('path'), SKIN)

    def __init__(self, lineup):
        """
        @type stations: list of available stations
        """
        super(StationsSelect, self).__init__()
        self.lineup = lineup
        self.station_list = sorted(sd.get_stations(lineup=lineup), key=lambda s: s.title.lower())
        self.channel_list = []
        self.swapInProgress = False
        self.selected_station = 0
        self.database = database

    def onInit(self):
        self.channel_list = self.database.getLineupChannels(self.lineup)
        self.updateChannelList()
        self.updateSavedChannelList()
        if len(self.station_list) > 0:
            self.setFocusId(self.C_CHANNELS_LIST_SOURCE)
        else:
            self.setFocus(self.C_CHANNELS_CANCEL)

    def onAction(self, action):
        if action.getId() in [ACTION_PARENT_DIR, KEY_NAV_BACK]:
            self.close()
            return

    def onClick(self, controlId):
        if controlId == self.C_CHANNELS_LIST:
            listControl = self.getControl(self.C_CHANNELS_LIST)
            item = listControl.getSelectedItem()
            del self.channel_list[int(item.getProperty('idx'))]
            if len(self.channel_list) == 0:
                self.channel_list.append(self.station_list[0])
            self.updateSavedChannelList()

        elif controlId == self.C_CHANNELS_LIST_SOURCE:
            listControl = self.getControl(self.C_CHANNELS_LIST_SOURCE)
            item = listControl.getSelectedItem()
            channel = self.station_list[int(item.getProperty('idx'))]
            found = False
            for ch in self.channel_list:
                if ch.id == channel.id:
                    found = True
                    break
            if not found:
                self.channel_list.append(channel)
            self.updateSavedChannelList()

        elif controlId == self.C_CHANNELS_SAVE:
            self.database.saveLineup(self.close, self.channel_list, self.lineup)
            xbmcgui.Dialog().notification(ADDON.getAddonInfo('name'), 'Changes saved...',
                                          os.path.join(PATH, 'icon.png'), 2500)

        elif controlId == self.C_CHANNELS_CANCEL:
            self.close()

    def onFocus(self, controlId):
        pass

    def updateChannelList(self):
        listControl = self.getControl(self.C_CHANNELS_LIST_SOURCE)
        listControl.reset()
        for idx, channel in enumerate(self.station_list):
            item = xbmcgui.ListItem('%3d. %s' % (idx + 1, channel.title))
            item.setProperty('idx', str(idx))
            listControl.addItem(item)

    def updateSavedChannelList(self):
        listControl = self.getControl(self.C_CHANNELS_LIST)
        listControl.reset()
        for idx, channel in enumerate(self.channel_list):
            item = xbmcgui.ListItem('%3d. %s' % (idx + 1, channel.title))
            item.setProperty('idx', str(idx))
            listControl.addItem(item)


def onDbInit(success):
    if not success:
        xbmcgui.Dialog().ok(ADDON.getAddonInfo('name'), 'Error initialising the Database!')


def close():
    global database
    change_count = int(get_setting('sd.changed')) + 1
    save_setting('sd.changed', str(change_count))
    if database:
        database.close(quit)

if __name__ == '__main__':

    user = get_setting('sd.username')
    passw = get_setting('sd.password')

    try:
        database = src.Database()
    except src.SourceNotConfiguredException:
        xbmcgui.Dialog().ok(ADDON.getAddonInfo('name'), 'Error initialising the Database!')
        close()
    database.initialize(onDbInit)

    try:
        if len(sys.argv) > 1:
            mode = int(sys.argv[1])
            if mode == 1:
                enter_credentials(is_change=True)
            else:
                login_ok = user and passw
                if not login_ok:
                    login_ok = login_popup() and user and passw

                if login_ok:
                    xbmcgui.Dialog().notification(ADDON.getAddonInfo('name'), 'Loading data...',
                                                  os.path.join(PATH, 'icon.png'), 2000)
                    sd = SdAPI(user=user, passw=passw)
                    if sd.logged_in:
                        if mode == 2:
                            select_lineup()
                        elif mode == 3:
                            if get_setting('source.source') != "SchedulesDirect":
                                xbmcgui.Dialog().ok('Settings','Set Data Source to SchedulesDirect and press OK first.')
                                exit()
                            edit_channels()
                        elif mode == 4:
                            delete_lineup()

    except SourceException as se:
        xbmcgui.Dialog().ok('ERROR', se.message,
                            'Make sure your username and password are correct!')
    close()
