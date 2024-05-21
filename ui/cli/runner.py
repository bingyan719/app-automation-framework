import os
import threading
import shutil

from ui.core.api import device_setup
from ui.core.helper import import_environment_cls
from ui.utils.config import Settings
from ui.utils.log import Logging
from ui.utils import constant
from ui.utils import download
from ui.utils import case_util
from ui.utils import net_util
from ui.cli.integration_test import RunApp
from ui.cli import installer
from ui.cli import appium


def check_environment():
    Logging.info('checking environment.')
    settings = Settings()
    device_id = settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_ID)
    device_type = settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_TYPE)
    Logging.debug('device id: {}'.format(device_id))
    Logging.debug('device platform: {}'.format(device_type))
    clz = import_environment_cls(device_type)
    env = clz(device_id)
    env.check()


def clean_environment():
    Logging.info('clearing environment.')
    # 清除tmps目下的所有文件
    settings = Settings()
    run_path = str(settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_RUN_PATH))
    local_dir = run_path + os.path.sep + "tmps"
    if os.path.exists(local_dir):
        print('local dir:{} exist, delete it now.'.format(local_dir))
        shutil.rmtree(local_dir)


def download_apk_or_ipa():
    Logging.info('downloading apk or ipa.')
    download.apk_or_ipa()


class Runner(object):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.settings = Settings()
        self.serial = self.settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_ID)
        self.device_type = self.settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_TYPE)

    def is_android(self):
        return self.device_type.lower() == 'android'

    def start(self):
        try:
            Logging.debug('device run: {}'.format(self.serial))
            # set status bar
            env = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_ENV)
            Logging.debug('env: {}'.format(env))
            need_comparison = str(self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_NEED_COMPARISON))
            Logging.debug('need_comparison: {}'.format(need_comparison))
            # ensure env is cloudsandbox, otherwise don't mind it
            if 'COMPATISANDBOX' in env.upper() and need_comparison == '1' and self.is_android():
                set_status_cmd = 'adb -s {} shell settings put global policy_control immersive.full=*'.format(self.serial)
                Logging.debug('set status bar.....')
                os.system(set_status_cmd)
            # convert test suite ids to test suite names when env is not dev
            case_util.convert_testcase_suites(self.settings)
            # send starting status to server
            net_util.send_start_status(self.settings, self.serial)
            a = RunApp(self.serial, self.settings)
            a.start()
        finally:
            # unset status bar
            if 'COMPATISANDBOX' == env.upper() and need_comparison == '1' and self.is_android():
                unset_status_cmd = 'adb -s {} shell settings put global policy_control null'.format(self.serial)
                Logging.debug('unset status bar.....')
                os.system(unset_status_cmd)
            # send finish status to server
            net_util.send_finish_status(self.settings, self.serial)


def run_device():
    test_run = Runner()
    test_run.start()


def run():
    Logging.info('runner run...')
    # check environment first
    check_environment()
    # download apk or ipa
    download_apk_or_ipa()
    # run it
    run_device()
    # uninstall it
    clean_environment()