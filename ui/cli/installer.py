import traceback

from ui.utils.log import Logging
from ui.utils.config import Settings
from ui.utils import constant
from ui.utils import command
from ui.core.android import perm_util


def install(settings):
    """
    install apk
    """
    Logging.info('install app begins...')
    # if current is debug mode, ignore it
    debug = str(settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_DEBUG))
    if 'true' == debug.lower():
        Logging.info('current mode is debug, ignore install action.')
        return 
    device_id = settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_ID)
    device_type = settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_TYPE)
    Logging.debug('device id: {}'.format(device_id))
    Logging.debug('device platform: {}'.format(device_type))
    is_install_success = False
    if 'android' == device_type.lower():
        is_install_success = install_android_app(settings, device_id)
    elif 'ios' == device_type.lower():
        is_install_success = install_ios_app(settings, device_id)
    else:
        Logging.error('unknown device type, please check it first.')
        exit()
    if not is_install_success:
        Logging.error('install not success after {} times retry.'.format(constant.INSTALL_RETRY_TIMES))
        exit()
    Logging.info('install app ends...')


def install_android_app(settings, udid):
    Logging.info('install android app begins...')
    apk_path = settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_APK_PATH)
    Logging.info('install android app path: {}'.format(apk_path))
    cur_counter = 0 
    is_success = False
    while cur_counter < constant.INSTALL_RETRY_TIMES and not is_success:
        try:
            outputs = command.cmd(['adb', '-s', udid, 'install', '-r', apk_path])
            for line in outputs.splitlines():
                line = line.strip()
                Logging.info('install message: {}'.format(line))
                if 'Success' in line:
                    Logging.info('install target apk has success.')
                    is_success = True
                    break
        except:
            traceback.print_exc()
            Logging.error('install target apk has an exception, try it again.')
            cur_counter += 1
    if is_success:
        Logging.info('install apk has success, grant all require permission')
        perm_util.grant_permissions(settings)
    return is_success


def install_ios_app(settings, udid):
    Logging.info('install ios app begins...')
    ipa_path = settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_APK_PATH)
    Logging.info('install ios ipa path: {}'.format(ipa_path))
    cur_counter = 0 
    is_success = False
    while cur_counter < constant.INSTALL_RETRY_TIMES and not is_success:
        try:
            outputs = command.cmd(['ios-deploy', '-i', udid, '-b', ipa_path])
            for line in outputs.splitlines():
                line = line.strip()
                Logging.info('install message: {}'.format(line))
                if 'Installed package' in line:
                    Logging.info('install target ipa has success.')
                    is_success = True
                    break
        except:
            traceback.print_exc()
            Logging.error('install target ipa has an exception, try it again.')
            cur_counter += 1
    return is_success