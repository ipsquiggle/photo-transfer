#standard
from datetime import datetime, timedelta
#libs
import itertools
import plumbum
from plumbum import local
from plumbum.path.utils import copy as plumbcopy
#project
from TransferCommon import PrintProgress
from TransferCommon import PhotoGlobs
from TransferCommon import Process

class Photo:
    def __init__(self, name, path, destination):
        self.name = name
        self.path = path
        self.destination = destination

def GetCardPhotosForCamera(camera, destpath):
    print("Looking for photos for {} at {}".format(camera.name, camera.path))
    _photos = []
    globs = PhotoGlobs()
    photopaths = camera.path // globs
    for path in photopaths:
        _photos.append(Photo(path.name, path, destpath / camera.name / path.name))
        PrintProgress(_photos)
    PrintProgress(_photos, True)

    return _photos

def GetCardPhotos(cameras, destpath):
    _photos = []

    for camera in cameras:
        print("{}: {}".format(camera.name, camera.path))
        if camera.path.is_dir():
            _photos += GetCardPhotosForCamera(camera, destpath)
        else:
            print("\tCouldn't find that path!")

    return _photos

def Transfer(cameras, destpath, delete=False, actual=False):
    print("Transferring photos from cards to {}".format(destpath))

    print("\nGathering Photos")

    photos = GetCardPhotos(cameras, destpath)

    if len(photos) == 0:
        print("No photos found.")
        exit(0)

    def copyskiptest(srcfile, destfile):
        # Note: this is a cheap imitation of filecmp
        if not destfile.exists():
            return False
        src_stat = srcfile.stat()
        dest_stat = destfile.stat()
        return (src_stat.st_mode == dest_stat.st_mode
                and src_stat.st_size == dest_stat.st_size
                and src_stat.st_mtime == dest_stat.st_mtime)

    def actualcopy(srcfile, destfile):
        dest_path = destfile.dirname
        if not dest_path.exists():
            dest_path.mkdir()
        plumbcopy(srcfile, destfile)

    print("\nCopying Photos")
    copied = Process(photos, "card-to-drive-", copyskiptest, actualcopy, actual)

    if actual:
        print("Copied {} photos.".format(len(copied)))
    else:
        print("Did not actually copy {} photos.".format(len(copied)))

    if delete:
        def deleteskiptest(srcfile, destfile):
            return False

        def actualdelete(srcfile, destfile):
            srcfile.delete()

        print("\nDeleting Photos")
        deleted = Process(photos, "erase-card-", deleteskiptest, actualdelete, actual)

        if actual:
            print("Deleted {} photos.".format(len(deleted)))
        else:
            print("Did not actually delete {} photos.".format(len(deleted)))
    else:
        print("No deletions.")

