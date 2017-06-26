#standard
import filecmp
#libs
import plumbum
from plumbum import local
from plumbum.path.utils import copy as plumbcopy
#project
from TransferCommon import PrintProgress
from Photo import Photo


def GetPhotosFromSource(sourcepath, targetpath):
    print("Getting photos from {} ".format(camerainfo.name))
    _photos = []

    globs = PhotoNormalGlobs()
    photopaths = sourcepath // globs
    for path in photopaths:
        PrintProgress(_photos)
        _photos.append( Photo(path, None, targetpath) )

    PrintProgress(_photos, True)
    print("Done.")

    return _photos

def GetRaw(photo, targetrawpath):
    for ext in rawext:
        rawpath = photo.path.with_suffix(ext)
        if rawpath.exists():
            return Photo(rawpath, photo.source, targetrawpath, date=photo.date, raw=True)

def GetSourcePhotos(cameras, sourcepath, dest, rawdest):
    _photos = GetPhotosFromSource(sourcepath, dest)

    print("Reprocessing...")
    for p in _photos:
        PrintProgress(_photos)
        _raw = []
        for camera in cameras:
            if p.source == camera.id:
                p.source = camera.name

                if camera.raw:
                    raw = GetRaw(photo)
                    if raw:
                        _raw.append(raw)
        _photos += _raw

    return _photos


def Transfer(cameras, sourcepath, targetpath, targetrawpath, actual=False):
    print("Transferring photos from {} to {}".format(sourcepath, targetpath))

    dest = local.path(targetpath)
    rawdest = local.path(targetrawpath)

    photos = GetSourcePhotos(cameras, dest, rawdest)

    def skiptest(srcfile, destfile):
        return os.path.exists(destination) and filecmp.cmp(srcfile, destfile)

    def actualaction(srcfile, destfile):
        srcfile.copy(destfile)

    copied = Process(photos, "-drive-to-network", skiptest, actualaction, actual)

    if actual:
        print("Copied {} photos.".format(len(copied)))
    else:
        print("Did not actually copy {} photos.".format(len(copied)))


def TransferRemote(cameras, targetserver, targetuser, targetpath, targetrawpath, actual=False):
    print("Transferring photos from all cameras to {} on {}".format(targetpath, targetserver))

    dest = local.path(targetpath)
    rawdest = local.path(targetrawpath)

    photos = GetSourcePhotos(cameras, dest, rawdest)

    def skiptest(srcfile, destfile):
        # Note: this is a cheap imitation of filecmp
        if not destfile.exists():
            return False
        src_stat = srcfile.stat()
        dest_stat = destfile.stat()
        return (src_stat.st_mode == dest_stat.st_mode
                and src_stat.st_size == dest_stat.st_size
                and src_stat.st_mtime == dest_stat.st_mtime)

    def actualaction(srcfile, destfile):
        dest_path = destfile.dirname
        if not dest_path.exists():
            dest_path.mkdir()
        plumbcopy(srcfile, destfile)

    copied = []
    with plumbum.SshMachine(targetserver, user=targetuser, scp_opts=['-p']) as remote:
        copied = Process(photos, "-drive-to-network-remote", skiptest, actualaction, actual)

    if actual:
        print("Copied {} photos.".format(len(copied)))
    else:
        print("Did not actually copy {} photos.".format(len(copied)))


