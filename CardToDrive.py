#standard
from datetime import datetime, timedelta
#libs
import itertools
import plumbum
from plumbum import local
#project
from PrintProgress import PrintProgress
from PhotoGlobs import PhotoGlobs

class Photo:
    def __init__(self, name, path):
        self.name = name
        self.path = path

def CameraForCard(cameras, path):
    for camera in cameras:
        camerapath = path / camera / ".camera"
        if camerapath.exists():
            return camera

    return "Unknown"

def GetCardPhotos(src):
    print("Looking for photos at {}".format(src))
    _photos = []
    globs = PhotoGlobs()
    photopaths = src // globs
    for path in photopaths:
        _photos.append(Photo(path.name, path))
        PrintProgress(_photos)
    PrintProgress(_photos, True)

    return _photos

def Transfer(srcpath, destpath, cameras, actual=False):
    print("Transferring from {} to {}".format(srcpath, destpath))

    src = local.path(srcpath)
    photos = GetCardPhotos(src)

    camera = CameraForCard(cameras, src)
    dest = local.path(destpath) / camera

    if len(photos) == 0:
        print("No photos found.")
        exit(0)

    logpath = local.path(__file__).dirname / "logs"

    textname = logpath / ("card-to-drive-"+(datetime.now().strftime("%Y-%m-%d %H.%M.%S"))+".txt")

    with open(textname, "w") as f:

        print("Grabbing {} photos from {}".format(len(photos), camera))
        f.write("Grabbing {} photos from {}\n\n".format(len(photos), camera))

        skip = 0
        t = 0
        if actual:
            dest.mkdir()

        for p in photos:
            t += 1
            srcfile = p.path
            destfile = dest / p.name
            f.write("{} => {}".format(srcfile, destfile))
            if actual:
                srcfile.copy(destfile)
            f.write(" OK\n")
            PrintProgress(str.format("{:d}/{:d} ({:d} skipped)", t, len(photos), skip))
        PrintProgress(str.format("{:d}/{:d} ({:d} skipped)", t, len(photos), skip), True)

        f.write("\nDone.\n")

    if actual:
        print("Copied photos.")
    else:
        print("Did not actually copy photos.")


# default_srcpath = "/media/4503-1203"
# default_destpath = "/media/usbdrive"
default_srcpath = r"c:\Users\graham\Pictures\Gords Camera"
default_destpath = r"c:\Users\graham\Pictures\Gords Camera 2"
default_cameras = ["Nikon", "Panasonic"]

Transfer(default_srcpath, default_destpath, default_cameras, False)
