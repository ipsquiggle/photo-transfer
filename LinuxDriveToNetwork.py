import argparse
import os
from datetime import datetime, timedelta

import DriveToNetwork
from DriveToNetwork import CameraInfo

default_cameras = {
    "Nikon",
    "Panasonic",
}
default_cameraphotospath = r"/media/usbdrive/cameras"

# default_dropboxpath = {
#     "G Phone":r"~/Dropbox/Camera Uploads",
#     "M Phone":r"~/Dropbox_Michelle/Camera Uploads"
# }
# dropbox_mindate = datetime.now() - timedelta(days=90)

default_paths = []
for c in default_cameras:
    default_paths.append( CameraInfo(c, os.path.join(default_cameraphotospath, c), True, None) )
# for c,path in default_dropboxpath.items():
#     default_paths.append( CameraInfo(c, path, False, dropbox_mindate) )

default_server = "hda"
default_user = "graham"
default_targetpath = r"/var/hda/files/xdrive/Michelle Pictures and Video"
default_targetrawpath = r"/var/hda/files/xdrive/Camera/RAW"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual", "-a", action="store_true", default=False)

    args = parser.parse_args()

    print("Transfering Photos (Windows Edition!)")

    DriveToNetwork.TransferRemote(default_paths, default_server, default_user, default_targetpath, default_targetrawpath, actual=args.actual)

