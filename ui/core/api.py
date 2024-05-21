"""
This module contains the ui.automation Core APIs.
"""

import time

from ui.utils.log import Logging
from ui.utils import constant
from ui.core.helper import G, import_device_cls, delay_after_operation

"""
Device Setup APIs
"""

def connect_device(uuid = None, platform = 'Android', driver = None, **kwargs):
    """
    Initialize device and set as current device.
    :param uuid: uuid for target device, e.g. serialno for Android, uuid for iOS
    :param platform: Android, IOS or Windows
    :param kwargs: Optional platform specific keyword args
    :return: device instance
    """
    if not uuid:
        Logging.error('device identifer should not be empty, please check it first')
        exit(3)
    clazz = import_device_cls(platform)
    device = clazz(uuid, driver, **kwargs)
    for index, instance in enumerate(G.DEVICE_LIST):
        if device.uuid == instance.uuid:
            Logging.info('Updating device: {}'.format(device.uuid))
            G.DEVICE = device
            G.DEVICE_LIST[index] = device
            break
    else:
        G.add_device(device)
    return device
    

def device():
    """
    Return the current active device.
    :return: current device instance
    """
    return G.DEVICE


def device_setup(device_id, device_type, driver):
    """
    Auto setup running environment and try connect android device if not device connected.
    """
    Logging.debug('enter device setup')
    Logging.debug('device id: {}'.format(device_id))
    Logging.debug('device platform: {}'.format(device_type))
    connect_device(device_id, device_type, driver)

"""
Device Operations
"""


def install(filepath, **kwargs):
    """
    Install application on device
    :param filepath: the path to file to be installed on target device
    :param kwargs: platform specific `kwargs`, please refer to corresponding docs
    :return: None
    :platforms: Android, iOS
    """
    return G.DEVICE.install_app(filepath, **kwargs)


def uninstall(package):
    """
    Uninstall application on device
    :param package: name of the package
    :return: None
    :platforms: Android, iOS
    """
    return G.DEVICE.uninstall_app(package)


def start_app(package, activity=None):
    """
    Start the target application on device
    :param package: name of the package to be started, e.g. "com.ABCD.smt"
    :param activity: the activity to start, default is None which means the main activity, will ignore it when target device is iOS
    :return: None
    :platforms: Android, iOS
    """
    G.DEVICE.start_app(package, activity)


def stop_app(package):
    """
    Stop the target application on device
    :param package: name of the package to stop
    :return: None
    :platforms: Android, iOS
    """
    G.DEVICE.stop_app(package)


def clear_app(package):
    """
    Clear data of the target application on device
    :param package: name of the package
    :return: None
    :platforms: Android, iOS
    """
    G.DEVICE.clear_app(package)


def current_activity():
    """
    fetch current focus activity name
    :return: current activity name
    :platforms: Android
    """
    return G.DEVICE.current_activity()


def home():
    """
    Return to the home screen of the target device.
    :return: None
    :platforms: Android
    """
    G.DEVICE.home()


def swipe_left_full():
    """
    swipe left with full screen
    """
    G.DEVICE.swipe_left_full()
    delay_after_operation()


def tap(x, y):
    """
    tap with cord
    """
    G.DEVICE.tap(x, y)
    delay_after_operation()


def click(locator, wait=2, runWatcher=True):
    """
    click with locator
    """
    is_clicked = G.DEVICE.click(locator, wait, runWatcher)
    delay_after_operation()
    return is_clicked

def longclick(locator, wait=2, runWatcher=True):
    """
    long click with locator
    """
    is_clicked = G.DEVICE.longclick(locator, wait, runWatcher)
    delay_after_operation()
    return is_clicked


def wait_until(locator, timeout=15):
    """
    Wait to match the target condition on the device screen
    :param locator: the target condition to meet
    :param timeout: max timeout for wait
    :return: None
    :platforms: Android, iOS
    """
    return G.DEVICE.wait_until(locator, timeout)


def swipe_until(direction, locator, times=10, padding=0.2):
    """
    Swipe up until the target condition meet
    :param direction: swipe direction, should be: UP, DOWN, LEFT, RIGHT.
    :param locator: the target condition to meet
    :param times: max times to do swipe action, default is 10.
    :return: None
    :platforms: Android, iOS
    """
    return G.DEVICE.swipe_until(direction, locator, times, padding)


def swipe_up_until(locator, times=10, padding=0.2):
    """
    Swipe up until the target condition meet
    :param locator: the target condition to meet
    :param times: max times to do swipe action, default is 10.
    :return: None
    :platforms: Android, iOS
    """
    return G.DEVICE.swipe_until(constant.UP, locator, times, padding)


def swipe_down_until(locator, times=10, padding=0.2):
    """
    Swipe down until the target condition meet
    :param locator: the target condition to meet
    :param times: max times to do swipe action, default is 10.
    :return: None
    :platforms: Android, iOS
    """
    return G.DEVICE.swipe_until(constant.DOWN, locator, times, padding)


def swipe_left_until(locator, times=10, padding=0.2):
    """
    Swipe left until the target condition meet
    :param locator: the target condition to meet
    :param times: max times to do swipe action, default is 10.
    :return: None
    :platforms: Android, iOS
    """
    return G.DEVICE.swipe_until(constant.LEFT, locator, times, padding)


def swipe_right_until(locator, times=10, padding=0.2):
    """
    Swipe right until the target condition meet
    :param locator: the target condition to meet
    :param times: max times to do swipe action, default is 10.
    :return: None
    :platforms: Android, iOS
    """
    return G.DEVICE.swipe_until(constant.RIGHT, locator, times, padding)


def text(locator, content, **kwargs):
    """
    Input text on the target device. Text input widget must be active first.
    :param text: text to input, unicode is supported
    :param enter: input `Enter` keyevent after text input, default is True
    :return: None
    :platforms: Android, Windows, iOS
    """
    is_set = G.DEVICE.text(locator, content, **kwargs)
    delay_after_operation()
    return is_set


def sleep(secs=1.0):
    """
    Set the sleep interval. It will be recorded in the report
    :param secs: seconds to sleep
    :return: None
    :platforms: Android, iOS
    """
    time.sleep(secs)


def run_watcher():
    """
    execute watcher one time
    """
    return G.DEVICE.run_watcher()


def exists(locator, wait=15):
    """
    Check whether the given target condition exists on device screen
    :param locator: target to be checked
    :return: False if target is not found, otherwise return True
    :platforms: Android, iOS
    """
    return G.DEVICE.exists(locator, wait)

def find_element(locator, wait=10):
    """
    Find element with current locator
    :param locator: target to be locator
    :param wait: timeout for find current element
    :return: target element information if exists, or Null will be returned.
    :platforms: Android, iOS
    """
    return G.DEVICE.find_element(locator, wait)


def snapshot(filename=None):
    """
    Take the screenshot of the target device and save it to the file.
    :param filename: name of the file where to save the screenshot. 
    :return: absolute path of the screenshot
    :platforms: Android, iOS
    """
    return G.DEVICE.screenshot(filename)

"""
Assertions
"""

def assert_exists(locator, msg=""):
    """
    Assert the target condition exists on device screen
    :param locator: target to be checked
    :param msg: short description of assertion, it will be recorded in the report
    :raise AssertionError: if assertion fails
    :return: None.
    :platforms: Android, iOS
    """
    is_exists = exists(locator)
    if not is_exists:
        raise AssertionError("%s does not exist in screen, message: %s" % (locator, msg))


def assert_not_exists(locator, msg=""):
    """
    Assert the target condition does not exist on device screen
    :param locator: target to be checked
    :param msg: short description of assertion, it will be recorded in the report
    :raise AssertionError: if assertion fails
    :return: None.
    :platforms: Android, iOS
    """
    is_exists = exists(locator)
    if not is_exists:
        raise AssertionError("%s exists unexpectedly, message: %s" % (locator, msg))

"""
Help Methods
"""

def disable_tbs():
    """
    Disable tbs when test begins, only works for android and smt apps.
    """
    return G.DEVICE.disable_tbs()

