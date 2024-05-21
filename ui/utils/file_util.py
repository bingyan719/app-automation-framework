import os
import time
import random
import shutil
import stat
import collections
import pathlib

from ui.utils import constant
from ui.utils.log import Logging


def is_target_app_exist(cache_dir, app_name):
    for filename in os.listdir(cache_dir):
        if filename == app_name:
            return True
    return False

def make_directory(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

def make_result_dir(settings, udid):
    env = str(settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_ENV))
    report_source_dir = str(settings.get_ini(constant.SECTION_REPORT_INFO, constant.SECTION_REPORT_INFO_SOURCE_DIR))
    result_dir = str(settings.get_ini(constant.SECTION_REPORT_INFO, constant.SECTION_REPORT_INFO_RESULT_DIR))
    result_file_every = result_dir + os.path.sep + str(udid)

    dirs = [
        result_dir,
        result_file_every,
        result_file_every + os.path.sep + 'cloudtestcapture',
        result_file_every + os.path.sep + 'logs',]

    # 首先删除已经存在的目录
    if os.path.exists(result_dir):
        Logging.debug('result dir exist, delete it first.')
        shutil.rmtree(result_dir)
    # 重新创建所有的目录
    for dir_path in dirs:
        make_directory(dir_path)
    # 拷贝资源文件到report目录下
    target_result_dir = result_file_every + os.path.sep + 'report'
    shutil.copytree(report_source_dir, target_result_dir)
    return result_file_every


def get_all_cases_file(settings):
    case_path = settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_CASE_PATH)
    return get_all_file(case_path, '.xlsx')


def get_all_file(root_directory, extension_name):
    """
    :return: 遍历文件目录
    """
    file_dic = collections.OrderedDict()
    for parent, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.endswith(extension_name) and not filename.startswith('~$'):
                # path = os.path.join(parent, filename).replace('\\', '/')
                path = os.path.join(parent, filename)
                file_dic[filename] = path
    return file_dic

def write_log_data(path, log_str):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(log_str)
        f.close()

def read_log_data(path):
    with open(path, encoding='utf-8') as f:
        contents = f.read()
        contents.rstrip()
    return contents

def del_file(filePath):
    try:
        if os.path.exists(filePath):
            for fileList in os.walk(filePath):
                for name in fileList[2]:
                    os.chmod(os.path.join(fileList[0], name), stat.S_IWRITE)
                    os.remove(os.path.join(fileList[0], name))
            shutil.rmtree(filePath)
            print("delete ok")
        else:
            print("no filepath")
    except Exception:
        print("delete files error")

def create_file(directory, file_name):
    file_path = os.path.join(directory, file_name)
    if not os.path.exists(file_path):
        pathlib.Path(file_path).touch()

