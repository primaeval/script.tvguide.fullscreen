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

import datetime
import requests

import xbmcgui
from utils import *
from strings import *

MAIN_URL = 'https://json.schedulesdirect.org/20141201'


class SdAPI(object):

    def __init__(self, user=get_setting('sd.username'), passw=get_setting('sd.password')):
        agent = "KODI-%s" % (ADDON.getAddonInfo('id'))
        self._headers = {'User-agent': agent}
        xbmc.log("[%s] SD-Header set to: %s" % (ADDON.getAddonInfo('id'), self._headers),
                 xbmc.LOGDEBUG)

        self._main_url = MAIN_URL
        self._user = user
        self.logged_in = False
        self.changes_remaining = 0
        self.max_lineups = 0
        self.lineups = []
        if self._main_url and self._user and passw:
            self._pass = passw  # Needs to be SHA1-Hex!
            self._get_token()
            if self.logged_in:
                self._get_status()
        else:
            raise SourceException('SD-Data not configured!')

    def _get_token(self):
        if 'token' in self._headers:
            del self._headers['token']
        resp = self._post('token', {"password": self._pass, "username": self._user})
        if 'code' in resp and int(resp['code']) != 0:
            xbmc.log("[%s] Error trying to log in: %s" % (ADDON.getAddonInfo('id'), resp['message']),
                     xbmc.LOGDEBUG)
            xbmcgui.Dialog().ok(ADDON.getAddonInfo('name'), 'Error trying to log into SchedulesDirect:', resp['message'])
            self.logged_in = False
        elif 'token' in resp:
            xbmc.log("[%s] SD-Token received: %s" % (ADDON.getAddonInfo('id'), resp['token']),
                     xbmc.LOGDEBUG)
            self._headers['token'] = resp['token']
            self.logged_in = True

    def _get_status(self):
        status = self._get('status')
        if 'account' in status and 'maxLineups' in status['account']:
            self.max_lineups = int(status['account']['maxLineups'])
        if 'lineups' in status:
            self.lineups = []
            for lineup in status['lineups']:
                self.lineups.append(lineup['lineup'])

    @staticmethod
    def _check_resp(resp):
        if resp.status_code == requests.codes.ok:
            info = (resp.text[:1000] + '..') if len(resp.text) > 1000 else resp.text
            xbmc.log("[%s] Reply from SD: %s - %s" %
                     (ADDON.getAddonInfo('id'), resp.status_code, info), xbmc.LOGDEBUG)
            return True
        else:
            message = ''
            try:
                info = resp.json()
                if 'message' in info:
                    message = info['message']
            except ValueError:
                message = resp.text

            xbmcgui.Dialog().ok(ADDON.getAddonInfo('name'), 'SchedulesDirect server reply:', message)
            xbmc.log("[%s] SD-Server response: %s - %s" %
                     (ADDON.getAddonInfo('id'), resp.status_code, resp.text), xbmc.LOGDEBUG)
            return False

    def _get(self, path):
        url = MAIN_URL + "/" + path
        xbmc.log('[%s] GET request: %s' % (ADDON.getAddonInfo('id'), url), xbmc.LOGDEBUG)
        resp = requests.get(url, headers=self._headers)
        if self._check_resp(resp):
            return resp.json()
        else:
            return []

    def _put(self, path):
        url = MAIN_URL + "/" + path
        xbmc.log('[%s] PUT request: %s' % (ADDON.getAddonInfo('id'), url), xbmc.LOGDEBUG)
        resp = requests.put(url, headers=self._headers)
        if self._check_resp(resp):
            return resp.json()
        else:
            return []

    def _post(self, path, post_data=None):
        url = MAIN_URL + "/" + path
        data = ""
        if post_data:
            data = json.dumps(post_data)
        info = (data[:1000] + '..') if len(data) > 1000 else data
        xbmc.log('[%s] POST request: %s - data: %s' % (ADDON.getAddonInfo('id'), url, info),
                 xbmc.LOGDEBUG)
        resp = requests.post(url, headers=self._headers, data=data)
        if self._check_resp(resp):
            return resp.json()
        else:
            return []

    def _delete(self, path):
        url = MAIN_URL + "/" + path
        xbmc.log('[%s] DELETE request: %s' % (ADDON.getAddonInfo('id'), url),
                 xbmc.LOGDEBUG)
        resp = requests.delete(url, headers=self._headers)
        if self._check_resp(resp):
            return resp.json()
        else:
            return []

    def get_user_lineups(self):
        data = self._get('lineups')
        lineups = []
        self.lineups = []
        if "lineups" in data:
            for lineup in data['lineups']:
                lineups.append(lineup)
                self.lineups.append(lineup['lineup'])
        return lineups

    def get_countries(self):
        data = self._get('available/COUNTRIES')
        countries = []
        for _, country_list in data.iteritems():
            for country in country_list:
                countries.append(country)
        return countries

    def get_lineups(self, country, postcode):
        data = self._get('headends?country=%s&postalcode=%s' % (country, postcode))
        lineups = []
        for item in data:
            if "lineups" in item:
                for lineup in item['lineups']:
                    lineups.append(lineup)
        return lineups

    def get_stations(self, lineup):
        data = self._get('lineups/%s' % lineup)
        stations = []
        if 'stations' in data:
            for station in data['stations']:
                logo = ''
                if 'logo' in station and 'URL' in station['logo']:
                    logo = station['logo']['URL']
                logo_type = int(ADDON.getSetting('logos.source'))
                if logo_type == 1:
                    logo = "%s%s.png" % (ADDON.getSetting('logos.folder'),station['name'])
                elif logo_type == 2:
                    url = ADDON.getSetting('logos.url').rstrip('/')
                    logo = "%s/%s.png" % (url,station['name'].replace(' ','%20'))
                channel = Channel(station['stationID'], station['name'], lineup, logo)
                stations.append(channel)
        return stations

    def save_lineup(self, lineup):
        resp = self._put('lineups/%s' % lineup)
        if "changesRemaining" in resp:
            self.changes_remaining = int(resp["changesRemaining"])
        if "response" in resp and resp["response"] == "OK":
            self.lineups.append(lineup)
            return True
        else:
            return False

    def delete_lineup(self, lineup):
        xbmc.log('[%s] Removing lineup "%s" form current lineups: %s' %
                 (ADDON.getAddonInfo('id'), str(lineup), str(self.lineups)), xbmc.LOGDEBUG)
        resp = self._delete('lineups/%s' % lineup)
        if "changesRemaining" in resp:
            self.changes_remaining = int(resp["changesRemaining"])
        if "response" in resp and resp["response"] == "OK":
            self.lineups.remove(lineup)
            return True
        else:
            return False

    def get_schedules(self, stations, date, progress_callback):
        req_data = []
        dates = [date.strftime('%Y-%m-%d')]
        date2 = date
        for d in range(1, int(get_setting('sd.range'))):
            date2 = date2 + datetime.timedelta(days=1)
            dates.append(date2.strftime('%Y-%m-%d'))
        for s in stations:
            req_data.append({'stationID': s, 'date': dates})

        resp = self._post('schedules', req_data)

        if progress_callback:
            if not progress_callback(10):
                raise SourceException()

        prg_list = []
        schedule = []
        for record in resp:
            if "stationID" in record:
                station_id = record['stationID']
            else:
                continue

            if "programs" in record:
                for program in record['programs']:
                    p_id = program['programID']
                    start = program['airDateTime']
                    dur = program['duration']
                    prg_list.append(p_id)
                    schedule.append({'station_id': station_id, 'p_id': p_id, 'start': start,
                                     'dur': dur, 'title': '', 'desc': '', 'logo': ''})

        prg_count = len(prg_list)
        if prg_count < 3000:
            xbmc.log("[%s] Number of programs requested: %d" %
                     (ADDON.getAddonInfo('id'), prg_count), xbmc.LOGDEBUG)
            p_resp = self._post('programs', prg_list)
            if progress_callback:
                if not progress_callback(75):
                    raise SourceException()
        else:
            xbmc.log("[%s] Number of programs requested: %d... Requesting batches of 3000" %
                     (ADDON.getAddonInfo('id'), prg_count), xbmc.LOGDEBUG)
            # Deal with more data requestes
            p_resp = []
            batches = list(grouper(3000, prg_list))
            step = (75-10) / len(batches)
            for ctr, batch in enumerate(batches):
                batch = filter(None, batch)
                xbmc.log("[%s] Requesting batch %d with %d items" %
                         (ADDON.getAddonInfo('id'), ctr+1, len(batch)), xbmc.LOGDEBUG)
                p_resp += self._post('programs', batch)
                if progress_callback:
                    if not progress_callback(10 + (ctr * step)):
                        raise SourceException()

        elements_parsed = 0
        for prg_data in p_resp:
            if 'programID' in prg_data:
                prg_id = prg_data['programID']
            else:
                continue

            # find the idx in the schedule
            idx = []
            for i, s in enumerate(schedule):
                if s['p_id'] == prg_id:
                    idx.append(i)

            title = ''
            if 'titles' in prg_data and len(prg_data['titles']) > 0:
                if 'title120' in prg_data['titles'][0]:
                    title = prg_data['titles'][0]['title120']

            desc = ''
            if 'episodeTitle150' in prg_data:
                desc = prg_data['episodeTitle150'] + ' - '

            if 'descriptions' in prg_data:
                tmp_d = None
                if 'description1000' in prg_data['descriptions']:
                    tmp_d = prg_data['descriptions']['description1000']
                elif 'description100' in prg_data['descriptions']:
                    tmp_d = prg_data['descriptions']['description100']

                if tmp_d and len(tmp_d) > 0 and 'description' in tmp_d[0]:
                    desc += tmp_d[0]['description']

            for i in idx:
                schedule[i]['title'] = title
                schedule[i]['desc'] = desc

        elements_parsed += 1
        if progress_callback and elements_parsed % 100 == 0:
            if not progress_callback(100.0 / prg_count * elements_parsed):
                raise SourceException()
        return schedule
