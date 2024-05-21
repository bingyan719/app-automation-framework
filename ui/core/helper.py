from ui.utils import time_util
from ui.utils.constant import OPDELAY

class G(object):
    """Represent the globals variables"""
    DEVICE = None
    DEVICE_LIST = []

    @classmethod
    def add_device(cls, device):
        """
        Add device instance in G and set as current device.
        Args:
            device: device to init
        Returns:
            None
        """
        cls.DEVICE = device
        cls.DEVICE_LIST.append(device)


def import_device_cls(platform):
    """lazy import device class"""
    platform = platform.lower()
    if platform == "android":
        from ui.core.android.android import Android as clazz
    elif platform == "ios":
        from ui.core.ios.ios import IOS as clazz
    else:
        raise RuntimeError("Unknown platform: {}".format(platform))
    return clazz


def import_environment_cls(platform):
    """lazy import environment class"""
    platform = platform.lower()
    if platform == "android":
        from ui.core.android.env import Environment as clazz
    elif platform == "ios":
        from ui.core.ios.env import Environment as clazz
    else:
        raise RuntimeError("Unknown platform: {}".format(platform))
    return clazz

def import_guide_cls(platform):
    """lazy import guide class"""
    platform = platform.lower()
    if platform == "android":
        from ui.core.android.guide import GuideUtil as clazz
    elif platform == "ios":
        from ui.core.ios.guide import GuideUtil as clazz
    else:
        raise RuntimeError("Unknown platform: {}".format(platform))
    return clazz

def delay_after_operation():
    time_util.sleep(OPDELAY)