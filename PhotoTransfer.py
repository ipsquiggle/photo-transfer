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


parser = argparse.ArgumentParser()
parser.add_argument("--actual", "-a", action="store_true", default=False)

args = parser.parse_args()

dropboxpath = {
    "G Phone":r"C:\Dropbox\Camera Uploads",
    "M Phone":r"C:\Users\Michelle\Dropbox\Camera Uploads"
}

dropbox_mindate = datetime(2016,7,1)

validcameras = {
    "Nikon",
    "Panasonic",
}
cameraphotospath = r"C:\Users\Graham\Pictures"

targetpath = r"X:\Michelle Pictures and Video"
targetrawpath = r"X:\Camera\RAW"

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
    def __init__(self, location, camera, targetroot, date=None):
        self.location = location
        self.camera = camera
        self.targetroot = targetroot
        self.date = date
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
            return os.path.join(self.targetroot, path, name)
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
        starttimer = None
        return



def GetCameraPhotosForCamera(camera, path, targetroot, dropbox=False):
    print("Getting photos for camera "+camera)
    _photos = []

    for f in os.listdir(path):
        PrintProgress(_photos)
        name, ext = os.path.splitext(f)
        if ext in [".jpg", ".JPG", ".mov", ".MOV", ".mts", ".MTS"]:
            fullpath = os.path.join(path, f)
            # print("Processing "+fullpath)
            p = Photo(fullpath, camera, targetroot)
            if not dropbox or p.date > dropbox_mindate:
                _photos.append( p )

    PrintProgress(_photos, True)
    print("Done.")

    return _photos


def GetCameraPhotos():
    _photos = []
    _raw = []

    for camera in validcameras:
        fullpath = os.path.join(cameraphotospath, camera)
        print(camera + ": " + fullpath)
        if os.path.isdir(fullpath):
            _photos += GetCameraPhotosForCamera(camera, fullpath, targetpath)

    for camera,path in dropboxpath.items():
        print(camera + ": " + path)
        if os.path.isdir(path):
            _photos += GetCameraPhotosForCamera(camera, path, targetpath, True)


    print("Getting photo raws.")

    for p in _photos:
        PrintProgress(_raw)
        pname, _ = os.path.splitext(p.location)
        for ex in [".NEF", ".RAW"]:
            raw = pname + ex
            if os.path.exists(raw):
                # print("Found and processing raw " + raw)
                _raw.append( Photo(raw, p.camera, targetrawpath, p.date) )

    PrintProgress(_raw, True)
    print("Done.")

    _photos += _raw

    return _photos


photos = GetCameraPhotos()

textname = os.path.join(cameraphotospath, "transferlog-"+(datetime.now().strftime("%Y-%m-%d %H.%M.%S"))+".txt")

with open(textname, "w") as f:
    print("Copying photos")
    f.write("Copying photos:\n\n")
    skip = 0
    t = 0
    for p in photos:
        t += 1
        f.write("{} => {}".format(p.location, p.destination))
        if os.path.exists(p.destination) and filecmp.cmp(p.location, p.destination):
            skip += 1
            f.write(" EXISTS\n")
            continue
        if args.actual:
            MakeDirs(os.path.dirname(p.destination))
            shutil.copy2(p.location, p.destination)
        f.write(" OK\n")
        PrintProgress(str.format("{:d}/{:d} ({:d} skipped)", t, len(photos), skip))
    PrintProgress(str.format("{:d}/{:d} ({:d} skipped)", t, len(photos), skip), True)

    f.write("\nDone.\n")

if args.actual:
    print("Copied photos.")
else:
    print("Did not actually copy photos.")

