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

