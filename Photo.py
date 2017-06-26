#standard
import os
from copy import copy
import math
import string
from datetime import datetime, timedelta
#libs
import exifread

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

def PathFromSource(source):
    if source is None:
        return "Unknown"
    return string.capwords(source)

class Photo():
    def __init__(self, path, source, targetpath, date=False, raw=False):
        self.path = path
        self.source = source
        self.targetpath = targetpath
        self.date = date
        self.raw = raw
        if self.source == None:
            self.source = self.CameraFromMeta(path)
        if date is True:
            self.date = self.DateFromNameOrMeta(path)

    def GetDestination(self):
        if self.date != None:
            if self.date is True:
                destpath = self.targetpath / PathFromDate(self.date) / PathFromSource(self.source)

                datename = self.date.strftime("%Y-%m-%d %H.%M.%S")

                if self.path.stem == datename:
                    return destpath / self.path.name
                else:
                    return destpath / str.format("{} {}{}", datename, name, self.path.name)
            else:
                return self.targetpath / PathFromSource(self.source) / self.path.name

        raise Exception("Couldn't compute a date/destination for "+self.location)

    def FetchTags(self, path):
        if self.tags != None:
            return self.tags

        f = open(path, 'rb')
        if f != None:
            self.tags = exifread.process_file(f, details=False)
            return self.tags

        return None

    def CameraFromMeta(self, path):
        tags = self.FetchTags(path)

        if "Image Model" in tags:
            # print("Found date in exif: " + str(tags["EXIF DateTimeOriginal"]))
            return tags["Image Model"]

        return "Unknown"

    def DateFromNameOrMeta(self, path):

        name = self.path.stem

        try:
            trydate = datetime.strptime(self.path.stem, "%Y-%m-%d %H.%M.%S")
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

        mtime = path.stat().st_mtime
        return datetime.fromtimestamp(mtime)

