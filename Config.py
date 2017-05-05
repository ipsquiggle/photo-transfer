#system
import os
import collections
from datetime import datetime, timedelta
#libs
import plumbum
from plumbum import local

SearchPath = collections.namedtuple('SearchPath', 'name path mindate')
CameraInfo = collections.namedtuple('CameraInfo', 'name raw id')

DropboxMindate = datetime.now() - timedelta(days=90)

Cameras = [
    CameraInfo("Nikon", True, "NIKON D3300"),
    CameraInfo("Panasonic", False, "DMC-ZS20"),
    CameraInfo("G Phone",  False, "LG-D852"),
    CameraInfo("M Phone", False, "SGH-I747M")
]

Linux = {
    "Server" : "hda",
    "User" : "graham",
    # "LocalPath" : local.path(r"/media/usbdrive/cameras"),
    "LocalPath" : local.path(r"c:\Users\graham\Pictures\Gords Camera 2"),
    "RemotePath" : local.path(r"/var/hda/files/xdrive/Michelle Pictures and Video"),
    "RemoteRawPath" : local.path(r"/var/hda/files/xdrive/Camera/RAW"),
    "SearchPaths" : [
        # SearchPath("G Dropbox", local.path(r"~/Dropbox/Camera Uploads"), DropboxMindate),
        # SearchPath("M Dropbox", local.path(r"~/Dropbox_Michelle/Camera Uploads"), DropboxMindate),
        SearchPath("SD Card", local.path(r"c:\Users\graham\Pictures\Gords Camera"), None),
        # SearchPath("SD Card", local.path(r"/media/4503-1203"), None),
    ],
}

Windows_CardPath = local.path(r"C:\Users\graham\Pictures\Gords Camera")
# Windows_CardPath = local.path(r"L:")

Windows = {
    "LocalPath" : local.path(r"c:\Users\graham\Pictures\Gords Camera 2"),
    "RemotePath" :  local.path(r"C:\Users\graham\Pictures\Gords Camera 3"),
    "RemoteRawPath" :  local.path(r"C:\Users\graham\Pictures\Gords Camera 3 Raw"),
    # "RemotePath" : local.path(r"X:\Michelle Pictures and Video"),
    # "RemoteRawPath" : local.path(r"X:\Camera\RAW"),
    "SearchPaths" : [
        # SearchPath("G Dropbox", local.path(r"C:\Dropbox\Camera Uploads"), DropboxMindate),
        # SearchPath("M Dropbox", local.path(r"C:\Users\Michelle\Dropbox\Camera Uploads"), DropboxMindate),
        SearchPath("SD Card", local.path(r"C:\Users\graham\Pictures\Gords Camera"), None),
        # SearchPath("SD Card", local.path(r"L:"), None),
    ],
}


# WHERE I AM:
#     I just converted everything in DriveToNetwork file to use plumbum, though I haven't
#     tested it yet. Need to make sure CardToDrive is converted, and then update
#     the calling scripts to use it as well! Actually they should probably just
#     use strings, I only need fancy path stuff within these workers anyways.

