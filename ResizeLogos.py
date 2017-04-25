import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
from PIL import Image, ImageOps

ADDON = xbmcaddon.Addon(id = 'script.tvguide.fullscreen')

def autocrop_image(infile,outfile):
    infile = xbmc.translatePath(infile)
    image = Image.open(infile)
    border = 0
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
    cropped_image = cropped_image.resize((int(logo_height*ratio), logo_height),Image.ANTIALIAS)
    outfile = xbmc.translatePath(outfile)
    cropped_image.save(outfile)


d = xbmcgui.Dialog()

old_path = d.browse(0, 'Source Logo Folder', 'files', '', False, False, 'special://home/')
if not old_path:
    quit()

new_path = d.browse(0, 'Destination Logo Folder', 'files', '', False, False,'special://home/')
if not new_path or old_path == new_path:
    quit()

dirs, files = xbmcvfs.listdir(old_path)

p = xbmcgui.DialogProgressBG()
p.create('TVGF', 'Processing Logos')
images = [f for f in files if f.endswith('.png')]
total = len(images)
i = 0
for f in images:
    infile = old_path+f
    outfile = new_path+f
    autocrop_image(infile,outfile)
    percent = 100.0 * i / total
    i = i+1
    p.update(int(percent),"TVGF",f)
p.close()