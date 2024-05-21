import os
import sys
import base64

from six import PY3

from ui.utils.time_util import sleep
from ui.utils.log import Logging
from ui.utils import time_util


def swipe(driver, startX, startY, endX, endY, duration=800):
    driver.swipe(startX, startY, endX, endY, duration)

def swipe_ratio(driver, screenWidth, screenHeight, startXR, startYR, endXR, endYR):
    return swipe(driver, str(startXR * screenWidth), str(startYR * screenHeight),
                        str(endXR * screenWidth), str(endYR * screenHeight))

def swipe_left_full(driver, screenWidth, screenHeight):
    """
    左滑屏幕整屏
    """
    # adapter huawei mate20 pro 
    # add by viking.den 2019.3.8
    swipe_ratio(driver, screenWidth, screenHeight, 0.9, 0.5, 0.1, 0.5)
    sleep(1)

def get_ios_predicate_content(keyword):
    return "(name == '{}' OR label == '{}' OR value == '{}') AND visible == 1".format(keyword, keyword, keyword)

def get_ios_predicate_content_contains(keyword):
    return "(name CONTAINS '{}' OR label CONTAINS '{}' OR value CONTAINS '{}') AND visible == 1".format(keyword, keyword, keyword)

def get_ios_predicate_content_starts_with(keyword):
    return "(name BEGINSWITH '{}' OR label BEGINSWITH '{}' OR value BEGINSWITH '{}') AND visible == 1".format(keyword, keyword, keyword)

def get_ios_predicate_content_ends_with(keyword):
    return "(name ENDSWITH '{}' OR label ENDSWITH '{}' OR value ENDSWITH '{}') AND visible == 1".format(keyword, keyword, keyword)

def take_screenshot(driver, filename):
    if not filename:
        return None
    if os.path.exists(filename):
        Logging.debug('save target destination screenshot exists, delete it first.')
        os.remove(filename)
    try:
        screenshotBase64 = driver.get_screenshot_as_base64()
        with open(filename, 'wb') as f:
            f.write(base64.b64decode(screenshotBase64))
        return filename
    except Exception:
        # may be black/locked screen or other reason, print exc for debugging
        import traceback
        traceback.print_exc()
        return None