import sys
import xbmc,xbmcaddon,xbmcvfs
import psutil

PROCNAME = "ffmpeg.exe"

for proc in psutil.process_iter():
    # check whether the process name matches
    if proc.name() == PROCNAME:
        proc.kill()

player = xbmc.Player()
player.stop()
