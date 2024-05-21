import os
import random
import time
import platform
import subprocess

from appium import webdriver

from ui.utils.log import Logging
from ui.utils.config import Settings
from ui.utils import constant
from ui.utils import command
from ui.utils import device_util
from ui.utils import net_util
from ui.utils.config import Apps
from ui.utils.clean_tasks import Cp


def __cmd(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

def clear_process(device_id, appium_port):
    cp = Cp()
    cp.clean_p(appium_port, device_id)
    cp.darwin_kill_appium(appium_port)

def __start_driver(settings, aport, bpport, drport):
    udid = settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_ID)
    d_type = settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_TYPE)
    result_dir = settings.get_ini(constant.SECTION_REPORT_INFO, constant.SECTION_REPORT_INFO_RESULT_DIR)
    time_str = time.strftime("%Y-%m-%d_%H_%M_%S{}".format(random.randint(10, 99)), time.localtime(time.time()))
    if platform.system() == 'Windows':
        log_file = 'appium_log' + '_' + time_str + '.txt'
    else:
        log_file = 'appium_log' + '_' + time_str + '.txt'
        log_path = result_dir + os.path.sep + udid + os.path.sep + 'logs' + os.path.sep + log_file
        if 'android' == d_type.lower():
            appium_cmd = 'appium -p {} -bp {} --chromedriver-port {} -g {}'.format(aport, bpport, drport, log_path)
        elif 'ios' == d_type.lower():
            appium_cmd = 'appium -p {} -g {}'.format(aport, log_path)
        else:
            Logging.error('Unknown device type, please check it first.')
            exit()
        count = 0
        appium_proc = __cmd(appium_cmd)
        while True:
            appium_line = str(appium_proc.stdout.readline().strip(), "utf-8")
            Logging.debug(appium_line)
            count = count + 1
            if 'listener started' in appium_line or 'Error: listener' in appium_line:
                break
            if not appium_line and count > 10:
                raise Exception('appium start error')
                break
                

def __get_appium_port(settings):
    aport = net_util.get_random_port_with_retry(random.randint(4700, 4900))
    bpport = net_util.get_random_port_with_retry(random.randint(4700, 4900))
    drport = net_util.get_random_port_with_retry(random.randint(9500, 9700))
    Logging.debug('random aport: {}, bpport: {}, drport: {}'.format(aport, bpport, drport))
    __start_driver(settings, aport, bpport, drport)
    return aport


def __get_android_desired_caps(udid, package_name, main_activity, debug):
    desired_caps = {}
    desired_caps['platformName'] = 'Android'
    desired_caps['platformVersion'] = device_util.get_android_platform_version(udid)
    desired_caps['deviceName'] = udid
    desired_caps['udid'] = udid
    desired_caps['noSign'] = True
    if debug.lower() == "true":
        desired_caps['noReset'] = True
    desired_caps['automationName'] = 'uiautomator2'
    desired_caps['newCommandTimeout'] = '1800'
    desired_caps['unicodeKeyboard'] = True
    desired_caps['resetKeyboard'] = True
    desired_caps['systemPort'] = net_util.get_random_port_with_retry(random.randint(8200, 8299))
    desired_caps['appPackage'] = package_name
    desired_caps['appActivity'] = main_activity
    return desired_caps


def __get_ios_desired_caps(udid, package_name):
    desired_caps = {}
    desired_caps['platformName'] = 'iOS'
    desired_caps['platformVersion'] = device_util.get_ios_platform_version(udid)
    desired_caps['automationName'] = 'xcuitest'
    desired_caps['deviceName'] = device_util.get_ios_device_name(udid)
    desired_caps['wdaLocalPort'] = net_util.get_random_port_with_retry(random.randint(8100, 8199))
    # desired_caps['usePrebuildWDA'] = True
    desired_caps['udid'] = udid
    desired_caps['bundleId'] = package_name
    return desired_caps


def start_appium(settings):
    number_of_starts = 0
    package_name = settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_PKG_NAME)
    udid = settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_ID)
    d_type = settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_TYPE)
    is_start_success = False
    driver = None
    apps = Apps()
    appium_port = constant.APPIUM_PORT
    while number_of_starts <= constant.APPIUM_MAX_RETRY_TIMES and not is_start_success:
        try:
            debug = str(settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_DEBUG))
            if 'true' == debug.lower():
                Logging.debug('debug mode, just connect it...')
                desired_caps = {}
                if 'android' == d_type.lower():
                    main_activity = settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_ACTIVITY_NAME)
                    Logging.debug('assembly android desired caps.')
                    desired_caps = __get_android_desired_caps(udid, package_name, main_activity, debug)
                    desired_caps['noReset'] = True
                else:
                    Logging.debug('assembly ios desired caps.')
                    desired_caps = __get_ios_desired_caps(udid, package_name)
                Logging.info('connecting appium server...')
                driver = webdriver.Remote('http://127.0.0.1:{}/wd/hub'.format(appium_port), desired_caps)
            else:
                Logging.debug('not debug mode, start appium first then connect it...')
                desired_caps = {}
                if 'android' == d_type.lower():
                    Logging.debug('assembly android desired caps.')
                    main_activity = settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_ACTIVITY_NAME)
                    desired_caps = __get_android_desired_caps(udid, package_name, main_activity, debug)
                else:
                    Logging.debug('assembly ios desired caps.')
                    desired_caps = __get_ios_desired_caps(udid, package_name)
                appium_port = __get_appium_port(settings)
                driver = webdriver.Remote('http://127.0.0.1:{}/wd/hub'.format(appium_port), desired_caps)
            Logging.debug('appium start {} success'.format(udid))
            is_start_success = True
        except Exception as e:
            number_of_starts += 1
            Logging.error('Failed to start appium :{}'.format(e))
            Logging.error('Try restarting the appium :{}, Trying the {} frequency'.format(udid, number_of_starts))
            try:
                if 'true' != debug.lower():
                    clear_process(udid, appium_port)
            except :
                Logging.error('cleaning appium process has an problem, ignore it.')
                pass
            time.sleep(5)
    if number_of_starts > 5 and not is_start_success:
        Logging.error('Can not start appium, exiting now...')
        exit()
    return appium_port, driver