
import itertools

def PhotoGlobs():
    globs = [["**/*"+x, "*"+x] for x in [".jpg",".png",".nef",".mov",".mts",".mp4"]]
    globs = tuple(itertools.chain.from_iterable(globs))
    return globs
