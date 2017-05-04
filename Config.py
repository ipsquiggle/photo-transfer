#system
import os
import collections
from datetime import datetime, timedelta
#libs
import plumbum
from plumbum import local

CameraInfo = collections.namedtuple('CameraInfo', 'name path raw mindate id')

DropboxMindate = datetime.now() - timedelta(days=90)

# Linux_CardPath = local.path(r"/media/4503-1203")
Linux_CardPath = local.path(r"c:\Users\graham\Pictures\Gords Camera")

Linux = {
    "Server" : "hda",
    "User" : "graham",
    # "LocalPath" : local.path(r"/media/usbdrive/cameras"),
    "LocalPath" : local.path(r"c:\Users\graham\Pictures\Gords Camera 2"),
    "RemotePath" : local.path(r"/var/hda/files/xdrive/Michelle Pictures and Video"),
    "RemoteRawPath" : local.path(r"/var/hda/files/xdrive/Camera/RAW"),
    "Cameras" : [
        CameraInfo("Nikon", Linux_CardPath, True, None, "NIKON D3300"),
        CameraInfo("Panasonic", Linux_CardPath, False, None, "DMC-ZS20"),
        # CameraInfo("G Phone", local.path(r"~/Dropbox/Camera Uploads"), False, DropboxMindate, "LG-D852"),
        # CameraInfo("M Phone", local.path(r"~/Dropbox_Michelle/Camera Uploads"), False, DropboxMindate, "SGH-I747M")
    ]
}

Windows_CardPath = local.path(r"C:\Users\graham\Pictures\Gords Camera")
# Windows_CardPath = local.path(r"L:")

Windows = {
    "LocalPath" : local.path(r"c:\Users\graham\Pictures\Gords Camera 2"),
    "RemotePath" : local.path(r"X:\Michelle Pictures and Video"),
    "RemoteRawPath" : local.path(r"X:\Camera\RAW"),
    "Cameras" : [
        CameraInfo("Nikon", Windows_CardPath, True, None, "NIKON D3300"),
        CameraInfo("Panasonic", Windows_CardPath, False, None, "DMC-ZS20"),
        # CameraInfo("G Phone", local.path(r"C:\Dropbox\Camera Uploads"), False, DropboxMindate, "LG-D852"),
        # CameraInfo("M Phone", local.path(r"C:\Users\Michelle\Dropbox\Camera Uploads"), False, DropboxMindate, "SGH-I747M")
    ]
}


# WHERE I AM:
#     I just converted everything in DriveToNetwork file to use plumbum, though I haven't
#     tested it yet. Need to make sure CardToDrive is converted, and then update
#     the calling scripts to use it as well! Actually they should probably just
#     use strings, I only need fancy path stuff within these workers anyways.

