#system
import sys
import argparse
import time
from subprocess import Popen
from subprocess import PIPE
#project

class ScriptException(Exception):
    '''RunScript error!'''

# In a future version, this is a big sleepy loop, but for now we're just going to execute it once.
def RunScript(scriptname, delete, actual):
    card_args = ['python', '-u', scriptname]
    if delete:
        card_args.append('-d')
    if actual:
        card_args.append('-a')

    print("Running {} (actual: {})".format(scriptname, actual))
    print(card_args)
    print('')

    card_process = Popen(card_args, stdout=PIPE, stderr=PIPE, bufsize=1)

    for line in iter(card_process.stdout.readline, b''):
        sys.stdout.write(line)

    print('')
    print(">> Returned {}".format(card_process.returncode))
    if card_process.returncode > 0:
        print("Child process failed!")
        print('')
        sys.stderr.write(card_process.stderr.read())
        sys.stderr.flush()
        print('')
        raise ScriptException()

    print("Completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual", "-a", action="store_true", default=False)
    parser.add_argument("--deletecard", action="store_true", default=False)

    args = parser.parse_args()

    print("Transfering Photos From Card")
    RunScript('WindowsCardToDrive.py', args.deletecard, args.actual)

    # print("Transfering Photos To Network")
    # RunScript('WindowsDriveToNetwork.py', args.actual)


