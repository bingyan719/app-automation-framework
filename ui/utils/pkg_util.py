import os
import re
import subprocess
import zipfile
import plistlib
import traceback
from subprocess import PIPE

from ui.utils import constant
from ui.utils.log import Logging

def __get_android_application_version(settings, app_path):
    pkg_version = 'N/A'
    try:
        if not os.path.exists(app_path):
            Logging.error('target app path: {} not exist.'.format(app_path))
            return pkg_version
        Logging.info('dump apk information.')
        root_path = settings.get_ini(constant.SECTION_REPORT_INFO, constant.SECTION_REPORT_INFO_ROOT_PATH)
        tools_path = root_path + os.path.sep + 'resources' + os.path.sep + 'tools' + os.path.sep 
        Logging.info('os name: {}'.format(os.name))
        if os.name == 'nt':
            aapt_path = tools_path + 'aapt.exe'
        else:
            aapt_path = tools_path + 'aapt'
        Logging.info('aapt path: ' + aapt_path)
        outputs = subprocess.Popen("{} d badging {}".format(aapt_path, app_path), shell=True,
                                   stdout=PIPE).stdout.readlines()
        package_name = None
        version_name = None
        version_code = None
        for line in outputs:
            line = line.decode().strip()
            if 'package: name=' in line:
                match = re.compile("package: name='(\S+)' versionCode='(\d+)' versionName='(\S+)'").match(line)
                if match:
                    package_name = match.group(1)
                    version_code = match.group(2)
                    version_name = match.group(3)
        if not package_name:
            raise RuntimeError('Parsing apk has failed.')
        Logging.info('package name:' + package_name)
        Logging.info('version code:' + version_code)
        Logging.info('version name:' + version_name)
        pkg_version = version_name
    except Exception as e:
        traceback.print_exc()
        Logging.error('Parsing apk information has failed.')
    return pkg_version


def __analyze_ipa_with_plistlib(ipa_path):
    ipa_file = zipfile.ZipFile(ipa_path)
    plist_path = __find_plist_path(ipa_file)
    if not plist_path:
        return None
    plist_data = ipa_file.read(plist_path)
    plist_root = plistlib.loads(plist_data)
    return plist_root
 

def __find_plist_path(zip_file):
    name_list = zip_file.namelist()
    pattern = re.compile(r'Payload/[^/]*.app/Info.plist')
    for path in name_list:
        m = pattern.match(path)
        if m is not None:
            return m.group()

def __get_ios_application_version(settings, app_path):
    pkg_version = 'N/A'
    try:
        if not os.path.exists(app_path):
            Logging.error('target app path: {} not exist.'.format(app_path))
            return pkg_version
        Logging.info('dump ipa information.')
        plist_dict = __analyze_ipa_with_plistlib(app_path)
        if not plist_dict:
            raise RuntimeError('can not read plist file.')
        for key, value in plist_dict.items():
            print('key: {}, value: {}'.format(key, value))
        package_name = plist_dict['CFBundleIdentifier']
        version_code = plist_dict['CFBundleVersion']
        version_name = plist_dict['CFBundleShortVersionString']
        app_label = plist_dict['CFBundleName']
        Logging.info('package name:' + package_name)
        Logging.info('version code:' + version_code)
        Logging.info('version name:' + version_name)
        pkg_version = version_name
    except Exception as e:
        traceback.print_exc()
        Logging.error('Parsing apk information has failed.')
    return pkg_version


def get_application_version(settings, app_path):
    Logging.debug('enter parsing application version')
    device_type = settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_TYPE)
    if 'android' == device_type.lower():
        return __get_android_application_version(settings, app_path)
    return __get_ios_application_version(settings, app_path)



