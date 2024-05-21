import os
import json
import random
import requests
import datetime
import traceback
import shutil
import stat
import time

from ui.utils.log import Logging
from ui.utils import file_util
from ui.utils.config import Settings
from ui.utils import constant
from ui.utils import time_util
from ui.entity.job import Job
from ui.cli import installer
from ui.cli import appium
from ui.utils import db_util
from ui.utils.clean_tasks import Cp
from ui.entity.suites import Suites
from ui.utils.ftp_upload import Xfer
from ui.cli import run_suite
from ui.utils import ftp_util
from ui.utils import device_util
from ui.utils import pkg_util
from ui.utils import net_util

from ui.core.api import *


class RunApp(object):

    def __init__(self, device_id, settings):
        Logging.info('starting test device: {}'.format(device_id))
        self.time = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime(time.time()))
        self.device_id = device_id
        self.settings = settings
        self.driver = None
        self.result_path = file_util.make_result_dir(self.settings, self.device_id)
        self.cloud_path = None

    def mkdirCloudTest(self, env, need_comparison, pkg_version, project_name):
        if not need_comparison == '1':
            return
        sn = str(self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_SN))
        token = str(self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_TASK_TOKEN))
        mode = str(self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_MODE))
        # device type
        device_type_settings = self.settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_TYPE)
        if device_type_settings.lower() == 'android':
            device_type = 'android'
            manufacturer = device_util.get_android_device_manufacturer(self.device_id)
            device_name = device_util.get_android_device_name(self.device_id)
        else:
            device_type = 'ios'
            manufacturer = device_util.get_ios_device_manufacturer(self.device_id)
            device_name = device_util.get_ios_device_name(self.device_id)
        project_name = project_name.replace("_test", "")
        self.cloud_path = self.result_path + os.path.sep + 'cloudtestcapture' + os.path.sep + project_name.lower() \
             + os.path.sep + pkg_version + os.path.sep + device_type + os.path.sep + manufacturer + os.path.sep + device_name
        file_util.make_directory(self.cloud_path)
        try:
            need_compare = 0
            xfer = Xfer()
            xfer.setFtpParams(constant.FTP_SERVER, constant.FTP_USER, constant.FTP_PASSWORD)
            mode = str(self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_MODE))
            if mode == 'debug':
                path = '/icyiy/debug/screenshots' + self.cloud_path.split('cloudtestcapture')[1]
            else:
                path = '/icyiy/release/screenshots' + self.cloud_path.split('cloudtestcapture')[1]
            is_baseline_exist = xfer.isExist(path + os.path.sep + "baseline")
            if is_baseline_exist:
                Logging.debug('baseline exist')
                self.cloud_path = self.cloud_path + os.path.sep + token + os.path.sep + str(self.device_id).lower().replace(' ', '')
                file_util.make_directory(self.cloud_path)
                need_compare = 1
            else:
                Logging.debug('baseline not exist')
                pre_version = db_util.select_version(mode, device_type, manufacturer, device_name, project_name)
                self.cloud_path = self.cloud_path + os.path.sep + "baseline"
                file_util.make_directory(self.cloud_path)
                if pre_version:
                    Logging.debug('baseline version exist: {}'.format(pre_version))
                    xfer.DownLoadFileTree(self.cloud_path, path.replace(pkg_version, pre_version) + os.path.sep + "baseline")
                    self.cloud_path = self.cloud_path.replace("baseline", token) + os.path.sep + str(self.device_id).lower().replace(' ', '')
                    file_util.make_directory(self.cloud_path)
                    need_compare = 1
                else:
                    Logging.debug('baseline version not exist.')
                    need_compare = 0
                # still use device_brand in mysql, just replace it's value to manufacturer
                db_util.insert_version(mode, pkg_version, device_type, manufacturer, device_name, project_name)
            # finnaly cloud path
            Logging.info('cloud path: {}'.format(self.cloud_path))
            # create a blockouts.ini file
            file_util.create_file(self.cloud_path, 'blockouts.ini')
            # set need compare flag
            self.settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_NEED_COMPARE, str(need_compare))
        finally:
            # always disconnect it 
            if xfer:
                xfer.clearEnv()

    def clear_process(self):
        """
        :return: clean appium and logcat process
        """
        cp = Cp()
        cp.clean_p(self.appium_port, self.device_id)
        cp.darwin_kill_appium(self.appium_port)

    def analysis(self, file_name, file_path, test_case_file, suites):
        """
        inherit driver and start test
        :param file_path: test case files
        :return:
        """
        s = run_suite.start_suite(
            self.driver,
            self.settings,
            file_name,
            file_path,
            self.result_path,
            self.device_id, 
            test_case_file, 
            suites, 
            self.cloud_path)
        return s.run()

    def start(self):
        Logging.info('enter integration test start...')
        test_case_file = file_util.get_all_cases_file(self.settings)
        if not test_case_file:
            Logging.error('not test case files found')
            exit()
        test_case_file_items = test_case_file.items()
        env = str(self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_ENV))
        mode = str(self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_MODE))
        need_comparison = str(self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_NEED_COMPARISON))
        project_name = str(self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_PROJECT))
        package_name = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_PKG_NAME)
        activity_name = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_ACTIVITY_NAME)
        app_path = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_APK_PATH)
        pkg_version = pkg_util.get_application_version(self.settings, app_path)
        self.mkdirCloudTest(env, need_comparison, pkg_version, project_name)
        job = Job()
        job.startTime = time_util.get_now_time()
        job.package_name = package_name
        job.package_name_version = pkg_version
        job.device_name = self.device_id
        job.suites = []
        fail_suites = ""
        
        s_case = str(self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_SPECIFY_CASES))
        sn = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_SN)
        ori_sn = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_ORI_SN)
        if int(sn) > 0 and int(ori_sn) > 0:
            sn = ori_sn

        # run test suite
        for file_name, file_path in test_case_file_items:
            Logging.debug('current file name: {}, file path: {}'.format(file_name, file_path))
            ignore_suite = False
            try:
                # 是否在指定的测试用例集中
                if s_case:
                    s_case_list = s_case.split('|')
                    if str(file_name).split('.')[0] not in s_case_list:
                        ignore_suite = True
                        continue
                # 剔除公共测试用例集
                if file_name.find('_common') > -1:
                    ignore_suite = True
                    continue
                # install it first 
                installer.install(self.settings)

                # start appium now 
                self.appium_port, self.driver = appium.start_appium(self.settings)

                # set allowInvisibleElements settings
                self.driver.update_settings({"allowInvisibleElements": True})

                time.sleep(5)
                #page_source = self.driver.page_source
                #print(page_source)

                # init device
                device_type = str(self.settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_TYPE))
                device_setup(self.device_id, device_type, self.driver)

                suites = Suites()
                suites.suite_name = str(file_name).split('.')[0]
                suites.startTime = time_util.get_now_time()
                suites.test_classes_list = []
                suites.retry_times = 1
                Logging.info('current test suite: {}'.format(file_path))
                
                self.analysis(file_name, file_path, test_case_file, suites)

                if suites.fail == 0:
                    job.suites.append(suites)
                else:
                    job.suites.append(suites)
                    fail_suites = fail_suites + suites.suite_name + '|'
            finally:
                if not ignore_suite:
                    debug = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_DEBUG)
                    if debug.lower() != 'true':
                        # uninstall target application first
                        try:
                            uninstall(package_name)
                        except Exception as e:
                            Logging.error('uninstall pkg: {} has an exception:'.format(package_name))
                    # clean environment
                    self.clean_up()
            
        job.endTime = time_util.get_now_time()
        job.total = sum([x.total for x in job.suites])
        job.success = sum([x.success for x in job.suites])
        job.fail = sum([x.fail for x in job.suites])
        # send task info to config 
        Logging.debug('total: {}'.format(job.total)) 
        Logging.debug('success: {}'.format(job.success)) 
        Logging.debug('fail: {}'.format(job.fail)) 
        self.settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_PASS_COUNTER, str(job.success))
        self.settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_FAIL_COUNTER, str(job.fail))
        # 暂时不统计
        self.settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_NO_EXEC_COUNTER, str(0))
        # 统计失败的测试用例步骤
        if job.fail > 0:
            fail_case_names = []
            Logging.debug('current test has fail, calulate fail case name')
            for test_suite in job.suites:
                test_cases = test_suite.test_classes_list[0].case_list
                for test_case in test_cases:
                    if test_case.result != 0:
                        continue
                    if test_case.fail_step:
                        fail_case_names.append("{}(失败步骤:{})".format(test_case.case_name, test_case.fail_step))
                    else:
                        fail_case_names.append(test_case.case_name)
            for fail_case in fail_case_names:
                Logging.info('fail case name: {}'.format(fail_case))
            self.settings.set_ini(constant.SECTION_TEST_INFO, 'fail_case_names', "|".join(fail_case_names))
        
        log_str = json.dumps(job, default=lambda obj: obj.__dict__, ensure_ascii=False)
        file_util.write_log_data(self.result_path + str(os.sep) + str(os.sep).join(['report', 'report', 'data.js']), 'var testSuits=' + log_str)
        mode = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_MODE)
        token = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_TASK_TOKEN)
        debug = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_DEBUG)
        if debug.lower() == 'true':
            return
        # 上传测试结果到服务器
        self.upload_results_to_server(mode, token)
        # 兼容性测试需要上传截屏文件
        if 'COMPATI' in env.upper():
            sn = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_SN)
            report_path = self.settings.get_ini(constant.SECTION_REPORT_INFO, constant.SECTION_REPORT_INFO_REPORT_PATH)
            self.upload_cloud_capture(mode, need_comparison)
            self.send_comparison_request(mode, need_comparison, token, self.device_id, project_name, pkg_version)

    def clean_up(self):
        Logging.info('cleaning up...')
        try:
            # quit appium server
            if self.driver:
                self.driver.quit()
            # uninstal WDA if current target device is iOS
            device_type = self.settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_TYPE)
            if 'ios' == device_type.lower():
                Logging.info('uninstall webdriver agent...')
                uninstall("com.apple.test.WebDriverAgentRunner-Runner")
            debug = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_DEBUG)
            # 测试模式不清除appium服务
            if debug.lower() == 'true':
                return
            # clean all processes
            self.clear_process()
        except Exception as error:
            Logging.warn('driver quit Error %s' % error)
       
    def send_comparison_request(self, mode, need_comparison, task, serial, project, version):
        Logging.debug('sending comparison request')
        if not need_comparison == '1':
            Logging.debug('current task not set need_comparison flag to true.')
            return
        need_compare = int(self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_NEED_COMPARE))
        if not need_compare == 1:
            Logging.debug('current task do not need compare.')
            return
        project_name = project.replace("_test", "")
        # device type
        device_type_settings = self.settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_TYPE)
        if device_type_settings.lower() == 'android':
            system = 'android'
            brand = device_util.get_android_device_manufacturer(self.device_id)
            model = device_util.get_android_device_name(self.device_id)
        else:
            system = 'ios'
            brand = device_util.get_ios_device_manufacturer(self.device_id)
            model = device_util.get_ios_device_name(self.device_id)
        net_util.send_comparison_request(mode, task, serial, project_name, version, system, brand, model)

    def upload_cloud_capture(self, mode, need_comparison):
        Logging.debug('upload cloud capture.')
        if not need_comparison == '1':
            return 
        # upload files
        if mode == 'debug':
            remote_dir = './icyiy/debug/screenshots'
        else:
            remote_dir = './icyiy/release/screenshots'
        srcDir = self.result_path + str(os.sep) + 'cloudtestcapture'
        try:
            # connect ftp server
            ftp_client = ftp_util.connect_ftp()
            errors = ftp_client.upload(srcDir, remote_dir, du_type=ftp_util.DUType.upload_dir.value)
            if errors and len(errors) > 0:
                for error in errors:
                    Logging.error(error)
                Logging.error('upload result directory has an exception.')
                exit()
        finally:
            # always disconnect it when finished
            if ftp_client:
                ftp_client.disconnect()

    def upload_results_to_server(self, mode, task_token):
        Logging.debug('upload result to server begin.')
        # upload files
        if mode == 'debug':
            remote_dir = './icyiy/debug/ui_reports/{}/{}'.format(task_token, self.device_id)
        else:
            remote_dir = './icyiy/release/ui_reports/{}/{}'.format(task_token, self.device_id)
        try:
            # connect ftp server
            ftp_client = ftp_util.connect_ftp()
            errors = ftp_client.upload(self.result_path, remote_dir, du_type=ftp_util.DUType.upload_dir.value)
            if errors and len(errors) > 0:
                for error in errors:
                    try:
                        Logging.error(error)
                    except:
                        # ignore this
                        pass
                Logging.error('upload result directory has an exception.')
        finally:
            # always disconnect it when finished
            if ftp_client:
                ftp_client.disconnect()


