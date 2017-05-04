#system
import itertools
from datetime import datetime
#lib
import plumbum
from plumbum import local

#################################################
### UTILS


imageext = [".jpg",".png"]
movieext = [".mov",".mts",".mp4"]
rawext = [".nef",".raw"]

def _globs(ext):
    globs = [["**/*"+x, "*"+x] for x in ext]
    globs = tuple(itertools.chain.from_iterable(globs))
    return globs

def PhotoGlobs():
    return _globs(imageext + movieext + rawext)

def PhotoNormalGlobs():
    return _globs(imageext + movieext)

def PhotoRawGlobs():
    return _globs(rawext)

import timeit

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

### UTILS
#################################################

def Process(photos, logprefix, skiptest, actualaction, actual):
    if len(photos) == 0:
        print("No photos found.")
        return []

    logpath = local.path(__file__).dirname / "logs"

    textname = logpath / (logprefix + (datetime.now().strftime("%Y-%m-%d %H.%M.%S"))+".txt")

    acted = []

    with open(textname, "w") as f:

        print("Beginning...")
        f.write("Beginning...\n\n")
        skip = 0
        t = 0

        for p in photos:
            t += 1
            srcfile = p.path
            destfile = p.destination

            f.write("{} => {}".format(srcfile, destfile))
            if skiptest(srcfile, destfile):
                skip += 1
                f.write(" SKIPPED\n")
                continue
            if actual:
                actualaction(srcfile, destfile)
            acted.append(srcfile)
            f.write(" OK\n")
            PrintProgress(str.format("{:d}/{:d} ({:d} skipped)", t, len(photos), skip))
        PrintProgress(str.format("{:d}/{:d} ({:d} skipped)", t, len(photos), skip), True)

        f.write("\nDone.\n")
        print("Logged to {}".format(textname))

    return acted

