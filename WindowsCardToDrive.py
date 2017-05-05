#system
import argparse
import os
#project
import CardToDrive
from Config import Cameras
from Config import Windows as Config

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual", "-a", action="store_true", default=False)
    parser.add_argument("--delete", "-d", action="store_true", default=False)

    args = parser.parse_args()

    print("Transfering Card (Windows Edition!)")

    CardToDrive.Transfer(Config["SearchPaths"], Config["LocalPath"], delete=args.delete, actual=args.actual)
