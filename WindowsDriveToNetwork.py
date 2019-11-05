import argparse
import os
from datetime import datetime, timedelta

import DriveToNetwork
from DriveToNetwork import CameraInfo

default_cameras = {
    "Nikon",
    "Panasonic",
    "Gord",
}
default_cameraphotospath = r"C:\Users\Graham\Pictures"

default_dropboxpath = {
    "G Phone":r"C:\Dropbox\Camera Uploads",
    "M Phone":r"C:\Users\Michelle\Dropbox\Camera Uploads"
}
dropbox_mindate = datetime.now() - timedelta(days=290)

default_paths = []
for c in default_cameras:
    default_paths.append( CameraInfo(c, os.path.join(default_cameraphotospath, c), True, None) )
for c,path in default_dropboxpath.items():
    default_paths.append( CameraInfo(c, path, False, dropbox_mindate) )

default_targetpath = r"X:\BackedUp\Michelle Pictures and Video"
default_targetrawpath = r"X:\BackedUp\Camera\RAW"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual", "-a", action="store_true", default=False)

    args = parser.parse_args()

    print("Transfering Photos (Windows Edition!)")

    DriveToNetwork.Transfer(default_paths, default_targetpath, default_targetrawpath, actual=args.actual)

