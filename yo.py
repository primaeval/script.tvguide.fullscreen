# -*- coding: utf-8 -*-
#
#      Copyright (C) 2016 primaeval [primaeval.dev@gmail.com]
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
import xbmc,xbmcgui,xbmcaddon,xbmcplugin,xbmcvfs
import sys
import re
import requests
import HTMLParser
import json

def log(x):
    xbmc.log(repr(x),xbmc.LOGERROR)

def get_url(url):
    #headers = {'user-agent': 'Mozilla/5.0 (BB10; Touch) AppleWebKit/537.10+ (KHTML, like Gecko) Version/10.0.9.2372 Mobile Safari/537.10+'}
    headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'}
    try:
        r = requests.get(url,headers=headers)
        html = HTMLParser.HTMLParser().unescape(r.content.decode('utf-8'))
        return html
    except:
        return ''


if __name__ == '__main__':
    d = xbmcgui.Dialog()
    select = d.select('yo.tv',['Add Provider','Remove Provider'])
    if select == 0:
        html = get_url("http://www.yo.tv")
        list_items = re.findall(r'<li><a href="http://(.*?)\.yo\.tv"  >(.*?)</a></li>',html,flags=(re.DOTALL | re.MULTILINE))
        names = [i[1].encode("utf8") for i in list_items]
        result = d.select("yo.tv Countries",names)
        if result != -1:
            #log(result)
            country = list_items[result][0]
            name = names[result]

            if country == "uk":
                url = "http://uk.yo.tv/api/setting?id=1594745998&lookupid=3"
            else:
                result = d.input("%s: zip/post code" % country)
                if not result:
                    pass
                url = "http://%s.yo.tv/api/setting?id=%s" % (country,result)
            #log(url)

            j = get_url(url)
            if not j:
                quit()
            #log(j)
            data = json.loads(j)
            headend = ""
            provider = ""
            if "Message" not in data:
                providers = [x["Name"] for x in data]
                index = d.select("%s provider:" % country,providers)
                if index == -1:
                    quit()
                headend = data[index]["Value"]
                provider = data[index]["Name"]
            #log((name,provider,country,headend))

            filename = 'special://profile/addon_data/script.tvguide.fullscreen/yo.json'
            providers = {}
            try:
                f = xbmcvfs.File(filename,'rb')
                providers = json.load(f)
                f.close()
            except:
                pass

            providers[str((name,provider,country,headend))] = (name,provider,country,headend)
            f = xbmcvfs.File(filename,'wb')
            json.dump(providers,f,indent=2)
            f.close()

    elif select == 1:
        filename = 'special://profile/addon_data/script.tvguide.fullscreen/yo.json'
        providers = {}
        try:
            f = xbmcvfs.File(filename,'rb')
            providers = json.load(f)
            f.close()
        except:
            pass

        providers_list = [(x,providers[x]) for x in sorted(providers)]
        labels = ["%s - %s" % (x[1][0],x[1][1]) for x in providers_list]

        results = d.multiselect("yo.tv - Remove Provider",labels)
        if results:
            for result in results:
                key = providers_list[result][0]
                del providers[key]

            f = xbmcvfs.File(filename,'wb')
            json.dump(providers,f,indent=2)
            f.close()


