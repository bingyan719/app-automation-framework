import os
import re

from ui.utils.compat import decode_path

THISPATH = decode_path(os.path.dirname(os.path.realpath(__file__)))
STATICPATH = os.path.join(THISPATH, "static")
DEFAULT_ADB_PATH = {
    "Windows": os.path.join(STATICPATH, "adb", "windows", "adb.exe"),
    "Darwin": os.path.join(STATICPATH, "adb", "mac", "adb"),
    "Linux": os.path.join(STATICPATH, "adb", "linux", "adb"),
    "Linux-x86_64": os.path.join(STATICPATH, "adb", "linux", "adb"),
    "Linux-armv7l": os.path.join(STATICPATH, "adb", "linux_arm", "adb"),
}
DEFAULT_ADB_SERVER = ('127.0.0.1', 5037)
SDK_VERISON_NEW = 24

IP_PATTERN = re.compile(r'(\d+\.){3}\d+')