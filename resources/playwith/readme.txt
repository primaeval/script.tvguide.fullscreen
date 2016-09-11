addons\script.tvguide.fullscreen\resources\playwith contains example AutoPlayWith files for Windows.

Set the paths for your ffmpeg and kodi userdata locations.

You can learn about core players in playercorefactory.xml here:
http://kodi.wiki/view/External_players

If you enable AutoPlayWiths the playwith.py and stopwith.py files will be called on starting and stopping a scheduled program if they exist in the folder:
userdata\addon_data\script.tvguide.fullscreen

The playwithchannel.py and stopwithchannel.py will be called if you press 9 and 8 while in the main epg.

Set the core player in "Settings \ Program Scheduler \ AutoPlayWith \ PlayerCoreFactory.xml player"
If you call your player from the py files leave the player name blank.

If anyone creates some working variations for Linux/Android etc please let me know and I'll add them in.

If you save any streams to disk check that it is legal to do so in your country and have the permission of the stream providers.