#standard
import os
import math
import string
import shutil
from datetime import datetime, timedelta
from copy import copy
import errno
import filecmp
import argparse
import collections
#libs
import exifread
import plumbum
from plumbum import local
from plumbum.path.utils import copy as plumbcopy
#project
from TransferCommon import PrintProgress

def LastOfMonth(date):
    assert(date)
    d = copy(date)
    nextmonth = d.replace(day=28) + timedelta(days=4)
    return nextmonth - timedelta(days=nextmonth.day)

def PathFromDate(date):
    assert(date)
    yearfolder = date.strftime(r"%Y")
    monthfolder = date.strftime(r"%m %B")

    month = date.month
    daygroupstart = int(math.floor((date.day-1) / 7.0)*7 + 1)
    daygroupend = min(daygroupstart + 6, LastOfMonth(date).day)
    weekfolder = "{:02d} {:02d}-{:02d}".format(month, daygroupstart, daygroupend)

    path = os.path.join(yearfolder, monthfolder, weekfolder)
    return path

def PathFromCamera(camera):
    return string.capwords(camera)

class Photo():
    def __init__(self, path, camera, targetpath, date=None, raw=False):
        self.path = path
        self.camera = camera
        self.date = date
        self.raw = raw
        if self.camera == None:
            self.camera = self.CameraFromMeta(path)
        if self.date == None:
            self.date = self.DateFromNameOrMeta(path)
        self.destination = self.TryComputeDestination(targetpath)
        # print("==> "+self.destination)

    def TryComputeDestination(self, targetpath):
        if self.date != None:
            destpath = local.path(targetpath) / PathFromDate(self.date) / PathFromCamera(self.camera)

            ext = self.path.suffix
            name = self.path.stem

            datename = self.date.strftime("%Y-%m-%d %H.%M.%S")

            if name == datename:
                return destpath / self.path.name
            else:
                return destpath / str.format("{} {}{}", datename, name, ext)

        raise Exception("Couldn't compute a date/destination for "+self.location)

    def FetchTags(self, path):
        if self.tags != None:
            return self.tags

        f = open(path, 'rb')
        if f != None:
            self.tags = exifread.process_file(f, stop_tag="DateTimeOriginal", details=False)
            return self.tags

        return None


    def CameraFromMeta(self, path):
        base, name = os.path.split(path)
        name, ext = os.path.splitext(name)
        try:
            trydate = datetime.strptime(name, "%Y-%m-%d %H.%M.%S")
            # print("Found date in name: "+trydate)
            return trydate
        except:
            pass

        tags = self.FetchTags(path)
        if "EXIF DateTimeOriginal" in tags:
            # print("Found date in exif: " + str(tags["EXIF DateTimeOriginal"]))
            try:
                trydate = datetime.strptime(str(tags["EXIF DateTimeOriginal"]), "%Y:%m:%d %H:%M:%S")
                return trydate
            except:
                raise

        ctime = os.path.getctime(path)
        return datetime.fromtimestamp(ctime)

    def DateFromNameOrMeta(self, path):
        base, name = os.path.split(path)
        name, ext = os.path.splitext(name)
        try:
            trydate = datetime.strptime(name, "%Y-%m-%d %H.%M.%S")
            # print("Found date in name: "+trydate)
            return trydate
        except:
            pass

        tags = self.FetchTags(path)
        if tags != None:
            if "EXIF DateTimeOriginal" in tags:
                # print("Found date in exif: " + str(tags["EXIF DateTimeOriginal"]))
                try:
                    trydate = datetime.strptime(str(tags["EXIF DateTimeOriginal"]), "%Y:%m:%d %H:%M:%S")
                    return trydate
                except:
                    raise

        ctime = os.path.getctime(path)
        return datetime.fromtimestamp(ctime)


def GetCameraPhotosForCamera(camerainfo, targetpath, targetrawpath):
    if(camerainfo.mindate):
        print("Getting photos for camera "+camerainfo.name+" with min date "+str(camerainfo.mindate))
    else:
        print("Getting photos for camera "+camerainfo.name)
    _photos = []

    globs = PhotoNormalGlobs()
    photopaths = camerainfo.path // globs
    for path in photopaths:
        PrintProgress(_photos)
        p = Photo(path, camerainfo.name, targetpath)
        if not camerainfo.mindate or p.date > camerainfo.mindate:
            _photos.append( p )

    PrintProgress(_photos, True)
    print("Done.")


    if camerainfo.raw:
        _raw = []
        print("Getting photo raws for camera "+camerainfo.name)
        for p in _photos:
            PrintProgress(_raw)
            for ext in rawext:
                rawpath = p.path.with_suffix(ext)
                if rawpath.exists():
                    _raw.append( Photo(rawpath, p.camera, targetrawpath, date=p.date, raw=True) )

        PrintProgress(_raw, True)
        print("Done.")

        _photos += _raw

    return _photos

def GetCameraPhotos(cameras, dest, rawdest):
    _photos = []

    for camera in cameras:
        print("{}: {}".format(camera.name, camera.path))
        if camera.path.is_dir():
            _photos += GetCameraPhotosForCamera(camera, dest, rawdest)
        else:
            print("\tCouldn't find that path!")

    return _photos


def Transfer(cameras, targetpath, targetrawpath, actual=False):
    print("Transferring photos from all cameras to {}".format(targetpath))

    dest = local.path(targetpath)
    rawdest = local.path(targetrawpath)

    photos = GetCameraPhotos(cameras, dest, rawdest)

    def skiptest(srcfile, destfile):
        return os.path.exists(destination) and filecmp.cmp(srcfile, destfile)

    def actualaction(srcfile, destfile):
        srcfile.copy(destfile)

    copied = Process(photos, "drive-to-network-", skiptest, actualaction, actual)

    if actual:
        print("Copied {} photos.".format(len(copied)))
    else:
        print("Did not actually copy {} photos.".format(len(copied)))


def TransferRemote(cameras, targetserver, targetuser, targetpath, targetrawpath, actual=False):
    print("Transferring photos from all cameras to {} on {}".format(targetpath, targetserver))

    dest = local.path(targetpath)
    rawdest = local.path(targetrawpath)

    photos = GetCameraPhotos(cameras, dest, rawdest)

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
        copied = Process(photos, "drive-to-network-remote-", skiptest, actualaction, actual)

    if actual:
        print("Copied {} photos.".format(len(copied)))
    else:
        print("Did not actually copy {} photos.".format(len(copied)))


