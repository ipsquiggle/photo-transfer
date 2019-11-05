import exifread
import os
import math
import string
import timeit
import shutil
from datetime import datetime, timedelta
from copy import copy
import errno
import filecmp
import argparse
import collections

CameraInfo = collections.namedtuple('CameraInfo', 'name path raw mindate')

def MakeDirs(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

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
    def __init__(self, location, camera, date=None, raw=False):
        self.location = location
        self.camera = camera
        self.date = date
        self.raw = raw
        if self.date == None:
            self.date = self.DateFromNameOrMeta(location)
        self.destination = self.TryComputeDestination()
        # print("==> "+self.destination)

    def TryComputeDestination(self):
        if self.date != None:
            base, name = os.path.split(self.location)
            name, ext = os.path.splitext(name)
            path = PathFromDate(self.date)
            path = os.path.join(path, PathFromCamera(self.camera))
            assert(path)
            datename = self.date.strftime("%Y-%m-%d %H.%M.%S")
            if name == datename:
                name = name+ext
            else:
                name = str.format("{} {}{}", datename, name, ext)
            return os.path.join(path, name)
        raise Exception("Couldn't compute a date/destination for "+self.location)

    def DateFromNameOrMeta(self, path):
        base, name = os.path.split(path)
        name, ext = os.path.splitext(name)
        try:
            trydate = datetime.strptime(name, "%Y-%m-%d %H.%M.%S")
            # print("Found date in name: "+trydate)
            return trydate
        except:
            pass

        f = open(path, 'rb')
        if f != None:
            tags = exifread.process_file(f, stop_tag="DateTimeOriginal", details=False)
            if "EXIF DateTimeOriginal" in tags:
                # print("Found date in exif: " + str(tags["EXIF DateTimeOriginal"]))
                try:
                    trydate = datetime.strptime(str(tags["EXIF DateTimeOriginal"]), "%Y:%m:%d %H:%M:%S")
                    return trydate
                except:
                    raise

        ctime = os.path.getctime(path)
        return datetime.fromtimestamp(ctime)

starttimer = None
def PrintProgress(l, last=False):
    global starttimer
    if starttimer == None:
        starttimer = timeit.default_timer()

    if last or timeit.default_timer() - starttimer > 1.0:
        if type(l) == list:
            print(len(l))
        else:
            print(l)
        starttimer = None if last else timeit.default_timer()
        return



def GetCameraPhotosForCamera(camerainfo):
    if(camerainfo.mindate):
        print("Getting photos for camera "+camerainfo.name+" with min date "+str(camerainfo.mindate))
    else:
        print("Getting photos for camera "+camerainfo.name)
    _photos = []

    for f in os.listdir(camerainfo.path):
        PrintProgress(_photos)
        name, ext = os.path.splitext(f)
        if ext in [".jpg", ".JPG", ".mov", ".MOV", ".mts", ".MTS", ".png", ".PNG"]:
            fullpath = os.path.join(camerainfo.path, f)
            # print("Processing "+fullpath)
            p = Photo(fullpath, camerainfo.name)
            if not camerainfo.mindate or p.date > camerainfo.mindate:
                _photos.append( p )

    PrintProgress(_photos, True)
    print("Done.")


    if camerainfo.raw:
        _raw = []
        print("Getting photo raws for camera "+camerainfo.name)
        for p in _photos:
            PrintProgress(_raw)
            pname, _ = os.path.splitext(p.location)
            for ex in [".NEF", ".RAW"]:
                raw = pname + ex
                if os.path.exists(raw):
                    # print("Found and processing raw " + raw)
                    _raw.append( Photo(raw, p.camera, p.date, True) )

        PrintProgress(_raw, True)
        print("Done.")

        _photos += _raw

    return _photos


def GetCameraPhotos(cameras):
    _photos = []

    for camera in cameras:
        print(camera.name + ": " + camera.path)
        if os.path.isdir(camera.path):
            _photos += GetCameraPhotosForCamera(camera)
        else:
            print("\tCouldn't find that path!")

    return _photos


def Transfer(cameras, targetpath, targetrawpath, actual=False):
    photos = GetCameraPhotos(cameras)

    logpath = os.path.dirname(os.path.abspath(__file__))
    logpath = os.path.join(logpath, "logs")
    MakeDirs(logpath)

    textname = os.path.join(logpath, "transferlog-"+(datetime.now().strftime("%Y-%m-%d %H.%M.%S"))+".txt")

    with open(textname, "w") as f:
        print("Copying photos")
        f.write("Copying photos:\n\n")
        skip = 0
        t = 0
        for p in photos:
            t += 1
            destination = (os.path.join(targetpath, p.destination)
                            if not p.raw
                            else os.path.join(targetrawpath, p.destination))
            f.write("{} => {}".format(p.location, destination))
            if os.path.exists(destination) and filecmp.cmp(p.location, destination):
                skip += 1
                f.write(" EXISTS\n")
                continue
            if actual:
                MakeDirs(os.path.dirname(destination))
                shutil.copy2(p.location, destination)
            f.write(" OK\n")
            PrintProgress(str.format("{:d}/{:d} ({:d} skipped)  {}", t, len(photos), skip, p.destination))
        PrintProgress(str.format("{:d}/{:d} ({:d} skipped)", t, len(photos), skip), True)

        f.write("\nDone.\n")

    if actual:
        print("Copied photos.")
    else:
        print("Did not actually copy photos.")

import plumbum
from plumbum import local
from plumbum.path.utils import copy as plumbcopy

def TransferRemote(cameras, targetserver, targetuser, targetpath, targetrawpath, actual=False):
    photos = GetCameraPhotos(cameras)

    logpath = os.path.dirname(os.path.abspath(__file__))
    logpath = os.path.join(logpath, "logs")
    MakeDirs(logpath)

    textname = os.path.join(logpath, "transferlog-"+(datetime.now().strftime("%Y-%m-%d %H.%M.%S"))+".txt")


    if len(photos) == 0:
        print("No photos found.")
        exit(0)

    with open(textname, "w") as f:
        print("Connecting to {}".format(targetserver))
        f.write("Copying photos to {}:\n\n".format(targetserver))

        with plumbum.SshMachine(targetserver, user=targetuser, scp_opts=['-p']) as remote:

            skip = 0
            t = 0
            for p in photos:
                t += 1
                destination = (os.path.join(targetpath, p.destination)
                                if not p.raw
                                else os.path.join(targetrawpath, p.destination))
                f.write("{} => {}".format(p.location, destination))
                src = local.path(p.location)
                dest = remote.path(destination)
                if dest.exists():
                    src_stat = src.stat()
                    dest_stat = dest.stat()
                    if src_stat.st_size == dest_stat.st_size and src_stat.st_mtime == dest_stat.st_mtime and src_stat.st_atime == dest_stat.st_atime:
                        skip += 1
                        f.write(" EXISTS\n")
                        continue
                if actual:
                    dest_path = dest.dirname
                    if not dest_path.exists():
                        dest_path.mkdir()
                    plumbcopy(src, dest)
                f.write(" OK\n")
                PrintProgress(str.format("{:d}/{:d} ({:d} skipped)  {}", t, len(photos), skip, p.destinationn))
            PrintProgress(str.format("{:d}/{:d} ({:d} skipped)", t, len(photos), skip), True)

            f.write("\nDone.\n")

    if actual:
        print("Copied photos.")
    else:
        print("Did not actually copy photos.")



