import traceback
import importlib, sys
import os
import time

from ui.utils.config import Settings
from ui.utils.log import Logging, Logs
from ui.utils import constant
from ui.utils import time_util
from ui.utils import base64_util

from ui.entity.action_enums import ActionType
from ui.entity.cases import Cases
from ui.entity.test_class import TestClasss
from ui.entity.case_data import CaseData
from ui.entity.sub_case_data import SubCaseData
from ui.utils.excel_helper import get_test_case
from ui.core.api import *
from ui.core.helper import import_guide_cls

from ui.utils.config import BlockoutsIni

class start_suite():

    def __init__(self, driver, settings, name, path, all_result_path, device, test_case_files, suites, cloud_path):
        self.path_file = path
        self.filename = str(name).split('.')[0]
        self.settings = settings
        self.device = device
        self.all_result_path = all_result_path
        self.test_case_files = test_case_files
        self.suites = suites
        self.cloud_path = cloud_path
        self.variables = None 
        self.retry_times = 1
        self.pkg_name = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_PKG_NAME)
        self.activity_name = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_ACTIVITY_NAME)
        try:
            self.retry_times = int(self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_RETRY_TIMES))
        except :
            Logging.debug('parsing retry_times has an exception.')
            self.retry_times = 3
        try:
            self.variables = self.settings.get_section(constant.SECTION_VARIABLES_INFO)
        except:
            Logging.debug('no variables exist.')
        self.device_type = self.settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_TYPE)
        self.need_comparison = str(self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_NEED_COMPARISON))

    def get_variable(self, name):
        if not self.variables:
            return name
        for _name in self.variables:
            if _name == name:
                return self.variables[_name]
        return name

    def __save_screen_file(self, file_name, cloudtestflag=False):
        Logging.info('saving screenshot: {}'.format(file_name))
        if cloudtestflag:
            screen_file = self.cloud_path + os.path.sep + '{}'.format(file_name)
        else:
            screen_file = self.all_result_path + os.path.sep + str(os.path.sep).join(['report', 'capture', '{}']).format(file_name)
        time.sleep(0.8)
        return snapshot(screen_file)

    def __handle_guide(self):
        device_id = self.settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_ID)
        device_type = self.settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_TYPE)
        clz = import_guide_cls(device_type)
        guide_util = clz(self.settings, device_id)
        guide_util.handle_guide()
        # handle disable tbs actions
        self.__disable_tbs()
    

    def __disable_tbs(self):
        debug = str(self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_DEBUG))
        if 'true' == debug.lower():
            Logging.info('debug mode, ignore disable tbs...')
            return
        if not (self.pkg_name in ('com.ABCD.smt', 'com.ABCD.smt.test',)):
            Logging.info('disable tbs actions only works for smt apps.')
            return
        Logging.info('do disable tbs after handle guide.')
        is_first = True
        cur_time = 1
        is_success = False
        # let's try three times
        while (not is_success) and cur_time <= 3:
            Logging.info('current retry time: {}'.format(cur_time))
            if not is_first:
                start_app(self.pkg_name, self.activity_name)
                time_util.sleep(6)
            else:
                is_first = False
            is_success = disable_tbs()
            if is_success:
                break
            else:
                stop_app(self.pkg_name)
                cur_time += 1
                time_util.sleep(3)
        if not is_success:
            Logging.info('disable tbs has failed, ignore it.')
            return   
        Logging.info('disable tbs has success, stop target app first')
        stop_app(self.pkg_name)
        time_util.sleep(5)
        Logging.info('restart target app...')
        start_app(self.pkg_name, self.activity_name)
        Logging.info('end disable tbs.')

    def start_target_app(self):
        Logging.debug('starting current application\'s main activity.')
        start_app(self.pkg_name, self.activity_name)
        time_util.sleep(0.8)

    def handle_target_app_start(self):
        self.__handle_guide()

    def quit_target_app(self):
        # quit app
        Logging.debug('quit current application.')
        # stop target application, then uninstal it
        stop_app(self.pkg_name)
        time_util.sleep(0.8)

    def get_control_property(self, dic_step):
        # 首先获取当前设备类型是否有设置对应的控制属性
        if 'ios' == self.device_type.lower():
            _ios_control_type = dic_step.ios_control_type
            _ios_control = dic_step.ios_control
            if _ios_control_type and _ios_control:
                return (_ios_control_type, _ios_control)
        _test_control_type = dic_step.test_control_type
        _test_control = dic_step.test_control
        return (_test_control_type, _test_control)

    def _append_case_log(self, cases, msg, level='info'):
        log = Logs(level, msg)
        cases.logs.append(log)

    def _append_case_snapshot(self, cases, filename):
        img_file = './capture/{}'.format(filename)
        log = Logs('capture', img_file)
        cases.logs.append(log)

    def capture_current_screen(self, step_name, block_areas):
        try:
            # first capture current screen
            ss_name = '{}.png'.format(step_name)
            self.__save_screen_file(ss_name, True)
            ini_path = os.path.join(self.cloud_path, 'blockouts.ini')
            blockoutsIni = BlockoutsIni(ini_path)
            counter = 1
            blockoutsIni.add_ini(step_name)
            # add exist blockout to ini file
            for blocking_area in block_areas:
                ss_test_control_type, ss_test_control = self.get_control_property(blocking_area)
                # handle :id/ property
                if ss_test_control and ss_test_control.startswith(':id/'):
                    # reset test control with package
                    ss_test_control = self.pkg_name + ss_test_control
                Logging.info('ss_test_control_type: {}'.format(ss_test_control_type))
                Logging.info('ss_test_control: {}'.format(ss_test_control))
                if not (ss_test_control_type and ss_test_control):
                    Logging.info('blocking info is empty, just ignore it.')
                    continue
                locator = (ss_test_control_type, ss_test_control)
                # max wait time to 5 seconds
                element = find_element(locator, wait=5)
                if not element:
                    Logging.info('target blocking out not exist, just ignore it, go next...')
                    continue
                rect = element.rect
                left = int(rect['x'])
                top = int(rect['y'])
                right = left + int(rect['width'])
                bottom = top + int(rect['height'])
                Logging.info('left: {}, top: {}, right: {}, bottom: {}'.format(left, top, right, bottom))
                key_name = 'item_{}'.format(counter)
                value_name = '{},{},{},{}'.format(left, top, right, bottom)
                blockoutsIni.set_ini(step_name, key_name, value_name)
                counter += 1
        except:
            traceback.print_exc()
            Logging.error('saving current screenshot has an exception, just aborting it.')

    def run(self):
        Logging.success('_run_case start')
        time_util.sleep(5)
        tc = TestClasss()
        tc.startTime = time_util.get_now_time()
        tc.case_list = []
        # 读取该用例集下的所有测试用例
        Logging.success('start reading all cases')
        case_list = get_test_case(self.settings, self.path_file, self.test_case_files)
        Logging.success('end reading all cases')
        self.suites.total = len(case_list)
        is_case_first_run = True
        for dic in case_list:
            # 忽略P4测试用例
            if isinstance(dic, CaseData) and dic.test_priority == 'P4':
                self.suites.total -= 1
                continue
            # 继承的测试用例不计入总的测试用例数
            if dic.is_inherit:
                self.suites.total -= 1
            # 重置重试计数变量
            retry_count = 0

            while retry_count < self.retry_times:
                cases = Cases()
                last_step = None
                try:
                    if dic.test_name:
                        test_name = str(dic.test_name)
                        Logging.info('Starting the test_case: {0}, test_case_id :{1}'.format(test_name, dic.id))
                    
                    if is_case_first_run:
                        # 测试用例第一次运行，处理进入主界面
                        is_case_first_run = False
                        self.handle_target_app_start()
                    else:
                        # 测试用例非第一次运行，启动应用即可
                        self.start_target_app()
                    time_util.sleep(5)
                    cases.result = 1
                    # 判断是否是测试用例
                    if isinstance(dic, CaseData):
                        cases.startTime = time_util.get_now_time()
                        self._append_case_log(cases, 'Start the file case: {}'.format(self.path_file))
                        self._append_case_log(cases, 'Start the test_case: {}, test_case_id: {}'.format(test_name, dic.id))
                        cases.case_id = dic.id
                        cases.case_name = test_name
                        cases.data_name = test_name
                        cases.group_name = str(dic.author)
                        cases.desc = test_name
                        cases.parameter = 'parameter is null'
                        
                        if len(dic.steps) > 0:
                            case_has_exception = False
                            for dic_step in dic.steps:
                                # 如果有步骤失败，则直接跳出
                                if case_has_exception:
                                    Logging.error('case has exception, abort all steps.')
                                    break
                                # 记录本此的执行步骤
                                last_step = dic_step.step_desc
                                Logging.info('step description: {}'.format(dic_step.step_desc))
                                Logging.info('step action: {}'.format(dic_step.test_action))

                                step_name = '{0}[]{1}[]{2}'.format(self.suites.suite_name, dic.test_name, dic_step.step_desc)
                                Logging.info('origin step name: {}'.format(step_name))
                                encode_step_name = base64_util.encode(step_name)
                                Logging.info('encoding step name: {}'.format(encode_step_name))
                                # 处理截屏操作
                                if dic_step.test_action.lower() == 'screenshot':
                                    if not self.need_comparison == '1':
                                        Logging.info('need comparsion is not set, just ignore screenshot action.')
                                        continue
                                    blocking_areas = dic_step.get_ignore_blocks()
                                    # do screenshot action
                                    if blocking_areas:
                                        # if blocking areas is empty, just ignore it
                                        self.capture_current_screen(encode_step_name, blocking_areas)
                                    continue

                                test_control_type, test_control = self.get_control_property(dic_step)
                                # 忽略空的操作，但不包括启动应用和等待
                                if not (test_control_type and test_control) \
                                    and dic_step.test_action != ActionType.StartApp.value[0] \
                                    and dic_step.test_action != ActionType.Wait.value[0]:
                                    Logging.error('step control type and control not specify, abort current step.')
                                    continue
                                Logging.info('step control type: {}'.format(test_control_type))
                                Logging.info('step control: {}'.format(test_control))
                                #continue

                                # handle :id property
                                if test_control and test_control.startswith(':id/'):
                                    # reset test control with package
                                    test_control = self.pkg_name + test_control
                                
                                range_num = 1
                                if isinstance(dic_step, SubCaseData):
                                    # 设置步骤重复次数
                                    if dic_step.test_range:
                                        range_num = int(dic_step.test_range)
                                    
                                    for i in range(0, range_num):
                                        # 如果有步骤失败，则直接跳出
                                        if case_has_exception:
                                            Logging.error('case has exception, abort all ranges.')
                                            break
                                        Logging.success('ignore_exception: {}'.format(dic_step.ignore_exception))
                                        # 点击事件
                                        if dic_step.test_action.lower() == ActionType.Click.value[0]:
                                            self._append_case_log(cases, 'click {}'.format(test_control))
                                            is_clicked = click((test_control_type, test_control))
                                            if is_clicked or dic_step.ignore_exception:
                                                Logging.success('click {} success'.format(test_control))
                                                self._append_case_log(cases, 'click {} success'.format(test_control))
                                            else:
                                                Logging.error('click {} fail'.format(test_control))
                                                # 标记为失败
                                                self._append_case_log(cases, 'click {} fail'.format(test_control), level='error')
                                                cases.result = 0
                                                case_has_exception = True
                                                # 保存截图
                                                img_name = '{0}_{1}_{2}.png'.format(self.suites.suite_name, dic.id, dic_step.step_id)
                                                self._append_case_snapshot(cases, img_name)
                                                self.__save_screen_file(img_name)
                                                break
                                        # 长点击事件
                                        elif dic_step.test_action.lower() == ActionType.LongClick.value[0]:
                                            self._append_case_log(cases, 'long click {}'.format(test_control))
                                            is_clicked = longclick((test_control_type, test_control))
                                            if is_clicked or dic_step.ignore_exception:
                                                Logging.success('long click {} success'.format(test_control))
                                                self._append_case_log(cases, 'long click {} success'.format(test_control))
                                            else:
                                                Logging.error('long click {} fail'.format(test_control))
                                                # 标记为失败
                                                self._append_case_log(cases, 'long click {} fail'.format(test_control), level='error')
                                                cases.result = 0
                                                case_has_exception = True
                                                # 保存截图
                                                img_name = '{0}_{1}_{2}.png'.format(self.suites.suite_name, dic.id, dic_step.step_id)
                                                self._append_case_snapshot(cases, img_name)
                                                self.__save_screen_file(img_name)
                                                break
                                        # 重启应用
                                        elif dic_step.test_action.lower() == ActionType.StartApp.value[0]:
                                            self._append_case_log(cases, 'start app')
                                            try:
                                                start_app(self.pkg_name, self.activity_name)
                                                sleep(5)
                                                Logging.success('start app success')
                                                self._append_case_log(cases, 'start app success')
                                            except:
                                                Logging.error('start app fail')
                                                # 标记为失败
                                                self._append_case_log(cases, 'start app fail', level='error')
                                                cases.result = 0
                                                case_has_exception = True
                                                # 保存截图
                                                img_name = '{0}_{1}_{2}.png'.format(self.suites.suite_name, dic.id, dic_step.step_id)
                                                self._append_case_snapshot(cases, img_name)
                                                self.__save_screen_file(img_name)
                                                break
                                        # 输入事件
                                        elif dic_step.test_action.lower() == ActionType.SendKeys.value[0]:
                                            test_text = str(dic_step.test_text)
                                            # 如果字符是以$开头，证明是变量，需要去系统环境的variables中获取
                                            if test_text and test_text.startswith('$'):
                                                test_text = self.get_variable(test_text.replace('$', ''))
                                            self._append_case_log(cases, 'set text: {}'.format(test_text))
                                            is_success = text((test_control_type, test_control), test_text)
                                            if is_success or dic_step.ignore_exception:
                                                Logging.success('set text: {} success'.format(test_text))
                                                self._append_case_log(cases, 'set text: {} success'.format(test_text))
                                            else:
                                                Logging.error('set text: {} success'.format(test_text))
                                                self._append_case_log(cases, 'set text: {} success'.format(test_text), level='error')
                                                cases.result = 0
                                                case_has_exception = True
                                                # 保存截图
                                                img_name = '{0}_{1}_{2}.png'.format(self.suites.suite_name, dic.id, dic_step.step_id)
                                                self._append_case_snapshot(cases, img_name)
                                                self.__save_screen_file(img_name)
                                                break
                                        # 点击坐标事件
                                        elif dic_step.test_action == ActionType.Tap.value[0]:
                                            locations = str(dic_step.test_control).split(',')
                                            self._append_case_log(cases, 'tap {}'.format(dic_step.test_control))
                                            if len(locations) == 2:
                                                tap(int(locations[0]), int(locations[1]))
                                                Logging.success('tap {} success'.format(dic_step.test_control))
                                                self._append_case_log(cases, 'tap {} success'.format(dic_step.test_control))
                                            else:
                                                Logging.error('tap {} fail'.format(dic_step.test_control))
                                                self._append_case_log(cases, 'tap {} fail'.format(dic_step.test_control), level='error')
                                                cases.result = 0
                                                case_has_exception = True
                                                # 保存截图
                                                img_name = '{0}_{1}_{2}.png'.format(self.suites.suite_name, dic.id, dic_step.step_id)
                                                self._append_case_snapshot(cases, img_name)
                                                self.__save_screen_file(img_name)
                                                break
                                        # 断言存在事件
                                        elif ActionType.AssertExists.value[0] == dic_step.test_action:
                                            test_wait = constant.ASSERT_WAIT_TIMEOUT
                                            if dic_step.test_wait:
                                                test_wait = int(dic_step.test_wait)
                                            Logging.debug('assert wait time:{}'.format(test_wait))
                                            self._append_case_log(cases, 'assertion {} exists'.format(test_control))
                                            is_exists = exists((test_control_type, test_control), wait=test_wait)
                                            if is_exists:
                                                Logging.success('assertion {} exists success'.format(test_control))
                                                self._append_case_log(cases, 'assertion {} exists success'.format(test_control))
                                            else:
                                                Logging.error('assertion {} exists fail.'.format(test_control))
                                                self._append_case_log(cases, 'assertion {} exists fail'.format(test_control), level='error')
                                                cases.result = 0
                                                case_has_exception = True
                                                # 保存截图
                                                img_name = '{0}_{1}_{2}.png'.format(self.suites.suite_name, dic.id, dic_step.step_id)
                                                self._append_case_snapshot(cases, img_name)
                                                self.__save_screen_file(img_name)
                                                break
                                        # 断言不存在事件
                                        elif ActionType.AssertNotExists.value[0] == dic_step.test_action:
                                            test_wait = constant.ASSERT_WAIT_TIMEOUT
                                            if dic_step.test_wait:
                                                test_wait = int(dic_step.test_wait)
                                            Logging.debug('assert wait time:{}'.format(test_wait))
                                            self._append_case_log(cases, 'assertion {} not exists'.format(test_control))
                                            is_exists = exists((test_control_type, test_control), wait=test_wait)
                                            if not is_exists:
                                                Logging.success('assertion {} not exists success'.format(test_control))
                                                self._append_case_log(cases, 'assertion {} not exists success'.format(test_control))
                                            else:
                                                Logging.error('assertion {} not exists fail, but it exists.'.format(test_control))
                                                self._append_case_log(cases, 'assertion {} not exists fail, but it exists.'.format(test_control), level='error')
                                                cases.result = 0
                                                case_has_exception = True
                                                # 保存截图
                                                img_name = '{0}_{1}_{2}.png'.format(self.suites.suite_name, dic.id, dic_step.step_id)
                                                self._append_case_snapshot(cases, img_name)
                                                self.__save_screen_file(img_name)
                                                break
                                        # 等待事件
                                        elif ActionType.WaitUntil.value[0] == dic_step.test_action:
                                            _sleep = 10
                                            if dic_step.test_wait:
                                                _sleep = dic_step.test_wait
                                            self._append_case_log(cases, 'Wait until {}-{} for {} seconds'.format(test_control_type, test_control, _sleep))
                                            found = wait_until((test_control_type, test_control), timeout=int(_sleep))
                                            if found or dic_step.ignore_exception:
                                                Logging.success('Wait until {}-{} for {} seconds success'.format(test_control_type, test_control, _sleep))
                                                self._append_case_log(cases, 'Wait until {}-{} for {} seconds success'.format(test_control_type, test_control, _sleep))
                                            else:
                                                Logging.error('Wait until {}-{} for {} seconds fail'.format(test_control_type, test_control, _sleep))
                                                self._append_case_log(cases, 'Wait until {}-{} for {} seconds fail'.format(test_control_type, test_control, _sleep), level='error')
                                                cases.result = 0
                                                case_has_exception = True
                                                # 保存截图
                                                img_name = '{0}_{1}_{2}.png'.format(self.suites.suite_name, dic.id, dic_step.step_id)
                                                self._append_case_snapshot(cases, img_name)
                                                self.__save_screen_file(img_name)
                                                break
                                        # 滑动事件
                                        elif ActionType.SwipeUntil.value[0] in dic_step.test_action:
                                            # 获取最大的滑动次数
                                            self._append_case_log(cases, 'Swipe until {}-{}'.format(test_control_type, test_control))
                                            # get max swipe times
                                            times = constant.MAX_SWIPE_TIMES
                                            if dic_step.test_range:
                                                times = dic_step.test_range
                                            # parsing swipe padding
                                            padding = constant.SWIPE_PADDING
                                            if dic_step.test_text:
                                                try:
                                                    padding = float(dic_step.test_text)
                                                    if not (padding > 0 and padding < 1):
                                                        Logging.error('illege swipe padding value: {}, reset back to: {}'.format(padding, constant.SWIPE_PADDING))
                                                        padding = constant.SWIPE_PADDING
                                                except:
                                                    Logging.error('parsing swipe padding has an exception.')
                                            Logging.info('swipe action padding: {}'.format(padding))
                                            direction = dic_step.test_action.lower()
                                            if direction == 'swipe_up_until':
                                                is_found = swipe_up_until((test_control_type, test_control), times=times, padding=padding)
                                            elif direction == 'swipe_down_until':
                                                is_found = swipe_down_until((test_control_type, test_control), times=times, padding=padding)
                                            elif direction == 'swipe_left_until':
                                                is_found = swipe_left_until((test_control_type, test_control), times=times, padding=padding)
                                            elif direction == 'swipe_right_until':
                                                is_found = swipe_right_until((test_control_type, test_control), times=times, padding=padding)
                                            else:
                                                Logging.error('swipe until action not in (swipe_up_until, swipe_down_until, swipe_left_until, swipe_right_until)')
                                                is_found = False
                                            Logging.info('swipe until result: {}'.format(is_found))
                                            if is_found or dic_step.ignore_exception:
                                                Logging.success('Swipe until {}-{} success'.format(test_control_type, test_control))
                                                self._append_case_log(cases, 'Swipe until {}-{} success'.format(test_control_type, test_control))
                                            else:
                                                Logging.error('Swipe until {}-{} fail'.format(test_control_type, test_control))
                                                self._append_case_log(cases, 'Swipe until {}-{} fail'.format(test_control_type, test_control), level='error')
                                                cases.result = 0
                                                case_has_exception = True
                                                # 保存截图
                                                img_name = '{0}_{1}_{2}.png'.format(self.suites.suite_name, dic.id, dic_step.step_id)
                                                self._append_case_snapshot(cases, img_name)
                                                self.__save_screen_file(img_name)
                                                break
                                        # 等待事件
                                        elif ActionType.Wait.value[0] == dic_step.test_action:
                                            _sleep = constant.WAIT_TIMEOUT
                                            if dic_step.test_wait:
                                                _sleep = dic_step.test_wait
                                            self._append_case_log(cases, 'Wait {} seconds'.format(_sleep))
                                            # sleep should no exception
                                            sleep(int(_sleep))
                                            Logging.success('Wait {} seconds'.format(_sleep))
                                            self._append_case_log(cases, 'Wait {} seconds success'.format(_sleep))
                                        else:
                                            Logging.error('Unknown step, just aborting it.')
                                decode_step_name = base64_util.decode(encode_step_name)
                                Logging.info('decoding step name: {}'.format(decode_step_name))
                    else:
                        self._append_case_log(cases, 'case file format error, the current {}, you need CaseData'.format(type(dic)), level='error')
                        cases.result = 0
                        Logging.error('case file format error, the current {}, you need CaseData'.format(type(dic)))
                except Exception as e:
                    traceback.print_exc()
                    msg = '执行出现未知错误，请先检测测试用例是否有误或通知开发者排查'
                    Logging.error(msg)
                    self._append_case_log(cases, msg, level='error')
                    cases.result = 0
                finally:
                    if dic.is_inherit:
                        Logging.info('sleep for inherit cases.')
                        time.sleep(5)
                    # 退出测试应用
                    self.quit_target_app()
                    retry_count += 1
                    if cases.result == 1 or (cases.result == 0 and retry_count >= self.retry_times):
                        Logging.info('test case running end.')
                        if not dic.is_inherit:
                            cases.endTime = time_util.get_now_time()
                            cases.fail_step = last_step
                            tc.case_list.append(cases)
                        break
                    else:
                        Logging.error('test case running failure, retry times: {}'.format(retry_count))
        # 统计测试用例集数据信息
        tc.endTime = time_util.get_now_time()
        self.suites.test_classes_list.append(tc)
        if len(self.suites.test_classes_list) > 0:
            list_case = self.suites.test_classes_list[0].case_list
            pass_list = list(filter(lambda x: x.result == 1, list_case))
            self.suites.success = len(pass_list)
            self.suites.fail = 0 if ((self.suites.total < 0) or (self.suites.total < self.suites.success)) else (self.suites.total - self.suites.success)
        self.suites.endTime = time_util.get_now_time()
        Logging.success('_run_case end')
        return True