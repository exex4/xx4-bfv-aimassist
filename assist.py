from lib import aimer
from lib import helpers
import ctypes

version = "0.1"

# this will attempt to gather your primar screen size. if you have issues or use
# a windowed version of BFV, you'll need to set this yourself

screensize = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
# or
#screensize = (1280, 960)


if __name__ == "__main__":
    print("xx4 aim assist Version %s" % version)

    if not helpers.is_admin():
        print("- Error: This must be run with admin privileges")
        input("Press Enter to continue...")
        exit(1)

    if not helpers.is_python3():
        print("- Error: This script requires Python 3")
        raw_input("Press Enter to continue...")
        exit(1)

    arch = helpers.get_python_arch()
    if arch != 64:
        print("- Error: This version of Python is not 64-bit")
        input("Press Enter to continue...")
        exit(1)

    print ("Using screensize: %s x %s" % screensize)
    aimer = aimer.Aimer(screensize)
    aimer.start()

