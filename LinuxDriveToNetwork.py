#system
import argparse
#project
import DriveToNetwork
from Config import Linux as Config

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual", "-a", action="store_true", default=False)

    args = parser.parse_args()

    print("Transfering Photos (Linux Edition!)")

    DriveToNetwork.TransferRemote(Config["Cameras"], Config["Server"], Config["User"], Config["RemotePath"], Config["RemoteRawPath"], actual=args.actual)

