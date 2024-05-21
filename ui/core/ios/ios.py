import os
import time
import traceback

from ui.core.device import Device
from ui.utils.log import Logging
from ui.utils import command
from ui.core import common
from ui.utils import time_util
from ui.utils.config import Settings
from ui.utils import constant
from ui.core.common import get_ios_predicate_content, get_ios_predicate_content_contains, get_ios_predicate_content_starts_with, get_ios_predicate_content_ends_with

from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.touch_action import TouchAction

from ui.core.error import ElementNotFoundException


class IOS(Device):
    """ios client"""

    def __init__(self, uuid=None, driver=None):
        super(IOS, self).__init__()
        Logging.debug('ios init begin...')
        self.uuid = uuid
        self.driver = driver
        self.width, self.height = self.__get_window_size()
        self.settings = Settings()
        Logging.debug('ios init ends...')

    def uuid(self):
        return self.uuid

    def install_app(self, filepath):
        """
        Install the application on the device
        Args:
            filepath: full path to the `ipa` file to be installed on the device
        Returns:
            if installation has success, return True; otherwise, return False
        """
        Logging.debug('install app: {}'.format(filepath))
        is_success = False
        try:
            outputs = command.cmd(['ios-deploy', '-i', self.uuid, '-b', filepath])
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
        return is_success

    def uninstall_app(self, bundleId):
        """
        Uninstall the application from the device
        Args:
            bundleId: application's bundle id
        Returns:
            if uninstallation has success, return True; otherwise, return False
        """
        Logging.debug('uninstall app: {}'.format(bundleId))
        is_success = False
        try:
            outputs = command.cmd(['ios-deploy', '-i', self.uuid, '--uninstall_only', '--bundle_id', bundleId])
            for line in outputs.splitlines():
                line = line.strip()
                Logging.info('uninstall message: {}'.format(line))
                if 'Uninstalled package' in line:
                    Logging.info('uninstall target ipa has success.')
                    is_success = True
                    break
        except:
            traceback.print_exc()
            Logging.error('uninstall target ipa has an exception, try it again.')
        return is_success

    def check_app(self, bundleId):
        """
        Check if bundle id exists on the device
        Args:
            bundleId: bundle id
        Returns:
            True if bundleId exists on the device, or False 
        """
        Logging.debug('checking apps in target device.')
        is_exists = False
        try:
            outputs = command.cmd(['ios-deploy', '-i', self.uuid, '--list_bundle_id'])
            for line in outputs.splitlines():
                line = line.strip()
                Logging.info('check app message: {}'.format(line))
                if bundleId in line:
                    Logging.info('check app has success.')
                    is_exists = True
                    break
        except:
            traceback.print_exc()
            Logging.error('check app has an exception, try it again.')
        return is_exists

    def start_app(self, bundleId, activity=None):
        """
        Start the application
        Args:
            bundleId: bundle id
            activity: ignore it when target device is iOS
        Returns:
            None
        """
        Logging.debug('starting target application: {}'.format(bundleId))
        self.driver.launch_app()
    
    def stop_app(self, bundleId):
        """
        Stop the application
        Args:
            bundleId: bundle id
        Returns:
            None
        """
        Logging.debug('stop target application: {}'.format(bundleId))
        self.driver.close_app()

    def clear_app(self, bundleId):
        """
        Clear all application data
        Args:
            bundleId: bundle id
        Returns: 
            None
        """
        Logging.debug('clearing target application: {}'.format(bundleId))
        self.driver.clear()

    def home(self):
        """
        Press HOME button
        :return: None
        """
        self.__keyevent("HOME")

    def swipe(self, startX, startY, endX, endY):
        """
        滑动
        分别为:起始点startX, startY。结束点endX, endY. 滑动默认800
        """
        common.swipe(self.driver, startX, startY, endX, endY)
    
    def swipe_left_full(self):
        """
        左滑全屏
        """
        common.swipe_left_full(self.driver, self.width, self.height)

    def tap(self, x, y):
        """
        根据坐标点击
        """
        Logging.debug('doing tap action.')
        self.driver.tap([(x, y), ])

    def click(self, locator, wait=2, runWatcher=True):
        """
        根据特征点点击
        """
        flag = False
        try:
            element = self.__find_element(locator, wait, runWatcher=runWatcher)
            if not element:
                Logging.debug('element not found.')
                return flag
            Logging.debug('element has found, click it.')
            time_util.sleep(0.8)
            element.click()
            time_util.sleep(0.4)
            _, my_identify = locator
            # TODO FIX THIS
            if my_identify in ("我的",):
                Logging.info('check new login popup exist or not.')
                package_name = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_PKG_NAME)
                time_util.sleep(2)
                self.tap(int(self.width - 5), int(self.height - 5))
                time_util.sleep(2)
            flag = True
        except AttributeError:
            Logging.error("未能在页面未能找到 %s 按钮" % (locator,))
        return flag

    def longclick(self, locator, wait=2, runWatcher=True):
        """
        根据特征点长点击
        """
        flag = False
        try:
            element = self.__find_element(locator, wait, runWatcher=runWatcher)
            if not element:
                Logging.debug('element not found.')
                return flag
            Logging.debug('element has found, long click it.')
            time_util.sleep(0.8)
            rect = element.rect
            centerX = int(rect['x']) + int(rect['width'] / 2)
            centerY = int(rect['y']) + int(rect['height'] / 2)
            actions = TouchAction(self.driver)
            self.driver.swipe(centerX, centerY, centerX, centerY, 5000)
            time_util.sleep(0.4)
            flag = True
        except AttributeError:
            Logging.error("未能在页面未能找到 %s 按钮" % (locator,))
        return flag

    def wait_until(self, locator, timeout=15, is_first=True):
        find_element = False
        try:
            (find_method, find_control) = self.__get_transform_locator(locator)
            if find_method == 'predicate':
                Logging.debug('predicate content: {}'.format(find_control))
                find_element = WebDriverWait(self.driver, timeout).until(
                    lambda driver: driver.find_element_by_ios_predicate(find_control).is_displayed())
            else:
                find_element = WebDriverWait(self.driver, timeout).until(
                    lambda driver: driver.find_element(*locator).is_displayed())
        except:
            Logging.error('wait until has an exception, check popup dialog now.')
            if is_first and self.run_watcher():
                # popup exist
                Logging.debug('popup dialog exist, do wait until again.')
                try:
                    find_element = self.wait_until(locator, wait=5, is_first=False)
                except:
                    Logging.debug('wait until still not exist, break it.')
        return find_element
        
    def swipe_until(self, direction, locator, times=10, padding=0.2):
        """
        滑动到某一控件出现
        """
        Logging.debug('swipe_until begin...')
        cur_times = 0
        is_found = False
        middle_padding = 0.5
        while cur_times < times:
            # found element first
            el = self.__find_element(locator, wait=2, runWatcher=False)
            if el and el.rect['height'] > 15:
                is_found = True
                time_util.sleep(0.3)
                break
            else:
                if direction == constant.LEFT:
                    common.swipe_ratio(self.driver, self.width, self.height, (1 - padding), middle_padding, padding, middle_padding)
                elif direction == constant.RIGHT:
                    common.swipe_ratio(self.driver, self.width, self.height, padding, middle_padding, (1 - padding), middle_padding)
                elif direction == constant.UP:
                    common.swipe_ratio(self.driver, self.width, self.height, middle_padding, (1 - padding), middle_padding, padding)
                elif direction == constant.DOWN:
                    common.swipe_ratio(self.driver, self.width, self.height, middle_padding, padding, middle_padding, (1 - padding))
                time_util.sleep(0.3)
            cur_times += 1
            Logging.debug('current swipe times: {}'.format(cur_times))
        Logging.debug('swipe_until end...')
        return is_found

    def text(self, locator, content, click_first=True, clear_first=True):
        is_success = False
        try:
            # found it first
            element = self.__find_element(locator)
            if not element:
                Logging.error('element not found, aborting set text.')
                return is_success
            if click_first:
                Logging.info('element found, click it first.')
                element.click()
            if clear_first:
                Logging.info('element found, clear it first.')
                element.clear()
            Logging.info('element found, starting set text.')
            element.send_keys(content)
            time_util.sleep(0.8)
            is_success = True
        except AttributeError:
            Logging.error("未能在页面中找到 %s 元素" % (locator,))
        return is_success

    def exists(self, locator, wait=10):
        is_exists = False
        element = self.__find_element(locator, wait=wait, runWatcher=False)
        if element:
            is_exists = True
        return is_exists

    def find_element(self, locator, wait=10):
        return self.__find_element(locator, wait=wait, runWatcher=False)

    def screenshot(self, filename):
        start_time = int(time.time())
        result = common.take_screenshot(self.driver, filename)
        end_time = int(time.time())
        Logging.debug('speed time: {} '.format(end_time - start_time ))

    def __find_element(self, locator, wait=15, runWatcher=True):
        """
        在给定的时间内根据特征点寻找元素
        """
        try:
            element = None
            _transform_locator = self.__get_transform_locator(locator)
            Logging.debug('transform locator: {}'.format(_transform_locator))
            (find_method, find_content) = _transform_locator
            # 等待元素出现
            try:
                if 'predicate' == find_method:
                    find_element = WebDriverWait(self.driver, wait).until(
                        lambda driver: driver.find_element_by_ios_predicate(find_content).is_displayed())
                elif 'accessibility_id' == find_method:
                    find_element = WebDriverWait(self.driver, wait).until(
                        lambda driver: driver.find_element_by_accessibility_id(find_content).is_displayed())
                elif 'class_chian' == find_method:
                    find_element = WebDriverWait(self.driver, wait).until(
                        lambda driver: driver.find_element_by_ios_class_chain(find_content).is_displayed())
                else:
                    find_element = WebDriverWait(self.driver, wait).until(
                        lambda driver: driver.find_element(*_transform_locator).is_displayed())
            except:
                # Logging.error('finding element has an exception.')
                find_element = False
            time.sleep(0.05)
            if not find_element:
                raise ElementNotFoundException
            # 再次查找，返回元素
            if 'predicate' == find_method:
                return self.driver.find_element_by_ios_predicate(find_content)
            elif 'accessibility_id' == find_method:
                return self.driver.find_element_by_accessibility_id(find_content)
            elif 'class_chian' == find_method:
                return self.driver.find_element_by_ios_class_chain(find_content)
            return self.driver.find_element(*_transform_locator)    
        except Exception as error:
            # traceback.print_exc()
            if runWatcher and self.run_watcher():
                # find it again
                return self.__find_element(locator, wait, runWatcher=False)
            else:
                if runWatcher:
                    Logging.error("未能在页面中找到 %s 元素" % (locator,))

    def _get_pop_list(self):
        button_list = []
        package_name = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_PKG_NAME)
        # 添加处理的弹窗事件
        button_allow = ("predicate",  get_ios_predicate_content('允许'))
        button_list.append(button_allow)

        if 'smt' in str(package_name):
            button1 = [("predicate", get_ios_predicate_content('关闭 nor')),
                       ("predicate", get_ios_predicate_content('AD 关闭')),]
            button_list.extend(button1)
        return button_list

    def run_watcher(self, max_retry=3):
        """
        this method should run when element not found, and set runWatcher at the same time
        """
        watchTriggered = False
        
        button_list = self._get_pop_list()

        _max_retry = max_retry
        ignore_pops = []
        button_allow_control = get_ios_predicate_content('允许')
        btn_close = get_ios_predicate_content('关闭 nor')
        while _max_retry > 0:
            innerTrigger = False
            Logging.debug('current run watcher times: {}, innerTrigger: {}'.format((max_retry - _max_retry) + 1, innerTrigger))
            for button in button_list:
                test_control_type, test_control = button
                if test_control in ignore_pops:
                    continue
                flag = self.click(button, wait=0.8, runWatcher=False)
                if flag:
                    # 如果不是权限的弹窗，添加到下次的忽略列表中(权限弹窗有可能出现多次)
                    if test_control not in (button_allow_control, ):
                        ignore_pops.append(test_control)
                    Logging.info('item with type: {} , control: {} exist, handle it.'.format(test_control_type, test_control))
                    innerTrigger = True
                    # if exist, sleep for a while
                    time_util.sleep(0.2)
                    if test_control in (btn_close,):
                        self.tap(5, int(self.height - 5))
                    break
            if not innerTrigger:
                Logging.debug('no more condition meet, abort watcher.')
                break
            else:
                watchTriggered = True
                # try more times, because may have multiple popup windows
                _max_retry -= 1
        return watchTriggered
    
    def __get_transform_locator(self, locator):
        _control_type, _control = locator
        _new_control_type= None
        _new_control = None
        Logging.debug('transform control type: {}, control: {}'.format(_control_type, _control))
        if constant.CONTROL_TYPE_TEXT == _control_type.upper():
            _new_control_type = 'predicate'
            _new_control = get_ios_predicate_content(_control)
        elif constant.CONTROL_TYPE_TEXT_CONTAINS == _control_type.upper():
            _new_control_type = 'predicate'
            _new_control = get_ios_predicate_content_contains(_control)
        elif constant.CONTROL_TYPE_TEXT_STARTS_WITH == _control_type.upper():
            _new_control_type = 'predicate'
            _new_control = get_ios_predicate_content_starts_with(_control)
        elif constant.CONTROL_TYPE_TEXT_ENDS_WITH == _control_type.upper():
            _new_control_type = 'predicate'
            _new_control = get_ios_predicate_content_ends_with(_control)
        elif constant.CONTROL_TYPE_ID == _control_type.upper():
            _new_control_type = 'id'
            # TODO fix this
            _new_control = _control
        elif constant.CONTROL_TYPE_XPATH == _control_type.upper():
            _new_control_type= _control_type
            _new_control = _control
        elif 'predicate' == _control_type.lower() or 'accessibility_id' == _control_type.lower() \
            or 'class_chain' == _control_type.lower():
            _new_control_type= _control_type
            _new_control = _control
        else:
            Logging.error('Unknown control type...')
        return (_new_control_type, _new_control)

    def __get_window_size(self):
        """
        获取屏幕分辨率
        {u'width': 1080, u'height': 1920}
        :return: 1080,1920
        """
        screen_size = self.driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        return width, height

    def disable_tbs(self):
        """
        use this to disable tbs
        """
        Logging.info('ignore ios disable tbs actions.')