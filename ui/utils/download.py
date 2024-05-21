import shutil
import os

from ui.utils.log import Logging
from ui.utils.config import Settings
from ui.utils import constant
from ui.utils import file_util
from ui.utils import ftp_util
        

def apk_or_ipa():
    settings = Settings()
    # is current is debug mode, ignore it
    debug = str(settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_DEBUG))
    if 'true' == debug.lower():
        Logging.info('current mode is debug, ignore download action.')
        return 

    ftp_name = str(settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_FTP_NAME))
    if not ftp_name:
        Logging.info('ftp_name not exist, please check it first.')
        exit()
    
    env = str(settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_ENV))
    # UI在线监控判断是否在缓存目录下应用存在，若存在，直接设置缓存下的文件
    if 'uimonitorsandbox' in env.lower():
        # check target apk exist or not
        cache_apps_dir = constant.DIR_FOR_CACHE_APPS
        if not os.path.exists(cache_apps_dir):
            Logging.debug('creating cache apps dir: {}'.format(cache_apps_dir))
            os.makedirs(cache_apps_dir)
        is_app_exist = file_util.is_target_app_exist(cache_apps_dir, ftp_name)
        if is_app_exist:
            Logging.debug('target application exist in cache apps dir.')
            # set install path
            settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_APK_PATH, cache_apps_dir + os.path.sep + ftp_name)
            return
    Logging.info('downloading: {}.'.format(ftp_name))
    # connect ftp server
    ftp_client = ftp_util.connect_ftp()
    # download apk from server
    try:
        run_path = str(settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_RUN_PATH))
        # task_token = str(settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_TASK_TOKEN))
        mode = str(settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_MODE))
        local_dir = run_path + os.path.sep + "tmps"
        if os.path.exists(local_dir):
            print('local dir:{} exist, delete it now.'.format(local_dir))
            shutil.rmtree(local_dir)
        os.makedirs(local_dir)
        if 'debug' == mode.lower():
            ftp_path = 'icyiy/debug/file_server/{}'.format(ftp_name)
        else:
            ftp_path = 'icyiy/release/file_server/{}'.format(ftp_name)
        # download apk
        errors = ftp_client.download(ftp_path, local_dir, du_type=ftp_util.DUType.download_file.value)
        if errors and len(errors) > 0:
            for error in errors:
                Logging.error(error)
            Logging.error('download target apk has an exception, aborting task...')
            exit()
        else:
            # set install path
            settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_APK_PATH, local_dir + os.path.sep + ftp_name)
        Logging.debug("download files from ftp server success.")
    finally:
        if ftp_client:
            ftp_client.disconnect()
        if not 'uimonitorsandbox' in env.lower():
            return
        # move target application to cache apps directory
        is_app_exist = file_util.is_target_app_exist(cache_apps_dir, ftp_name)
        if is_app_exist:
            return
        Logging.debug('target application not exist in cache apps dir, copy it...')
        try:
            shutil.copy(local_dir + os.path.sep + ftp_name, cache_apps_dir)
        except:
            Logging.debug('copy target application to cache apps dir has an exception.')