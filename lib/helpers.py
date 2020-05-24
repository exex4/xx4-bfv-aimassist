import os
import sys
import struct
from ctypes import *


def is_admin():
    try:
        admin = os.getuid() == 0
    except AttributeError:
        admin = windll.shell32.IsUserAnAdmin() != 0
    return admin


def is_python3():
    if sys.version_info[0] < 3:
        return False
    return True


def get_python_arch():
    return (8 * struct.calcsize("P"))