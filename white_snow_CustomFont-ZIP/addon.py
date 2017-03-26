import xbmc,xbmcgui,xbmcaddon

d = xbmcgui.Dialog()
ok = d.ok("TV Guide Fullscreen","Set this Skin as default?")
if ok:
    tvgf = xbmcaddon.Addon("script.tvguide.fullscreen")
    if tvgf:
        tvgf.setSetting('skin.source', '2')
        tvgf.setSetting('skin.folder', 'special://home/addons/script.tvguide.fullscreen.skin.white_snow_CustomFont/')
        tvgf.setSetting('skin.user', 'Skin')
        tvgf.setSetting('action.bar', 'value="true')
        tvgf.setSetting('down.action', 'value="true')
        tvgf.setSetting('channels.per.page', '8')
        tvgf.setSetting('epg.box.spacing', '4')
        tvgf.setSetting('epg.focus.color', '[COLOR ff606060]black[/COLOR]')
        tvgf.setSetting('epg.font', 'TVGuide29')
        tvgf.setSetting('epg.nofocus.color', '[COLOR ff696969]dimgrey[/COLOR]')
        tvgf.setSetting('last.channel.popup', 'value="1')
        tvgf.setSetting('redraw.epg', 'value="false')
        tvgf.setSetting('up.cat.mode', 'No')
        