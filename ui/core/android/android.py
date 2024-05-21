import platform
import time
import traceback

from ui.core.device import Device
from ui.core.android.adb import ADB
from ui.utils.log import Logging
from ui.core import common
from ui.utils import time_util
from ui.utils.config import Settings
from ui.utils import constant

from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.touch_action import TouchAction

from ui.core.error import ElementNotFoundException


class Android(Device):
    """Android Device Class"""

    def __init__(self, serialno=None, driver=None, host=None):
        super(Android, self).__init__()
        Logging.debug('android init begin...')
        self.serialno = serialno
        self.driver = driver
        # init adb
        self.adb = ADB(self.serialno)
        self.adb.wait_for_device()
        self.sdk_version = self.adb.sdk_version
        self.width, self.height = self.__get_window_size()
        self.settings = Settings()
        Logging.debug('android init ends...')

    def uuid(self):
        return self.serialno

    def install_app(self, filepath, replace=False, install_options=None):
        """
        Install the application on the device
        Args:
            filepath: full path to the `apk` file to be installed on the device
            replace: True or False to replace the existing application
            install_options: list of options, default is []
        Returns:
            output from installation process
        """
        return self.adb.install_app(filepath, replace=replace, install_options=install_options)

    def uninstall_app(self, package):
        """
        Uninstall the application from the device
        Args:
            package: package name
        Returns:
            output from the uninstallation process
        """
        Logging.debug('uninstall package: {}'.format(package))
        return self.adb.uninstall_app(package)

    def check_app(self, package):
        """
        Check if package exists on the device
        Args:
            package: package name
        Returns:
            True if package exists on the device, or False 
        """
        return self.adb.check_app(package)

    def start_app(self, package, activity=None):
        """
        Start the application and activity
        Args:
            package: package name
            activity: activity name
        Returns:
            None
        """
        return self.adb.start_app(package, activity)
    
    def stop_app(self, package):
        """
        Stop the application
        Args:
            package: package name
        Returns:
            None
        """
        return self.adb.stop_app(package)

    def clear_app(self, package):
        """
        Clear all application data
        Args:
            package: package name
        Returns:
            None
        """
        return self.adb.clear_app(package)

    def current_activity(self):
        """
        Fetch current application activity name
        Args:
            None
        Retruns:
            current activity name if exist
        """
        return self.adb.get_current_activity()

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
        self.driver.tap([(x, y), ])

    def click(self, locator, wait=2, runWatcher=True):
        """
        根据特征点点击
        """
        flag = False
        try:
            element = self.__find_element(locator, wait, runWatcher=runWatcher)
            if not element :
                Logging.debug('element not found.')
                return flag
            Logging.debug('element has found, click it.')
            time_util.sleep(0.8)
            element.click()
            time_util.sleep(0.4)
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
            if not element :
                Logging.debug('element not found.')
                return flag
            Logging.debug('element has found, click it.')
            time_util.sleep(0.8)
            actions = TouchAction(self.driver)
            actions.long_press(element)
            actions.perform()
            time_util.sleep(0.4)
            flag = True
        except AttributeError:
            Logging.error("未能在页面未能找到 %s 按钮" % (locator,))
        return flag

    def wait_until(self, locator, timeout=15, is_first=True):
        find_element = False
        try:
            _transform_locator = self.__get_transform_locator(locator)
            Logging.debug('transform locator: {}'.format(_transform_locator))
            find_element = WebDriverWait(self.driver, timeout).until(
                    lambda driver: driver.find_element(*_transform_locator).is_displayed())
        except:
            Logging.error('wait until has an exception, check popup dialog now.')
            if is_first and self.run_watcher():
                # popup exist
                Logging.debug('popup dialog exist, do wait until again.')
                find_element = self.wait_until(locator, timeout=5, is_first=False)
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
            # if el and el.rect['height'] >= 30:
            if el:
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
            is_success = True
        except AttributeError:
            Logging.error("未能在页面中找到 %s 元素" % (locator,))
        return is_success

    def exists(self, locator, wait=10):
        is_exists = False
        element = self.__find_element(locator, wait=wait, runWatcher=True)
        if element:
            is_exists = True
        return is_exists

    def find_element(self, locator, wait=10, runWatcher=False):
        return self.__find_element(locator, wait=wait, runWatcher=runWatcher)

    def screenshot(self, filename):
        return common.take_screenshot(self.driver, filename)

    def __find_element(self, locator, wait=15, runWatcher=True):
        """
        在给定的时间内根据特征点寻找元素
        """
        try:
            start_time = time.time()
            element = None
            _transform_locator = self.__get_transform_locator(locator)
            Logging.debug('transform locator: {}'.format(_transform_locator))
            # 等待元素出现
            try:
                find_element = WebDriverWait(self.driver, wait).until(
                    lambda driver: driver.find_element(*_transform_locator).is_displayed())
            except:
                find_element = False
            time.sleep(0.05)
            if not find_element:
                raise ElementNotFoundException
            # 再次查找，返回元素
            element = self.driver.find_element(*_transform_locator)
            print(element.rect)
            return element
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
        if 'smt' in str(package_name):
            button1 = ('id', package_name + ':id/iv_ride_code_guide')
            button2 = ('id', package_name + ':id/iv_card_bag_my_guide')
            button3 = ('id', package_name + ':id/temp_iv_cancel')
            button4 = ('id', package_name + ':id/temp_close_view')
            button5 = ('id', package_name + ':id/rl_guide')
            button6 = ('id', package_name + ':id/close_view')
            button7 = ('id', package_name + ':id/iv_cancel')
            opinion_next = ('id', package_name + ':id/high_opinion_next_view')
            button_list = [button1, button2, button3, button4, button5, button6, button7, opinion_next]
        elif 'nt' in str(package_name):
            button2 = ('id', package_name + ':id/tv_later_on')
            button_list = [button2]
        elif 'gxecard' in str(package_name):
            pass
        # generical popup window property
        button_perm = ('id', 'android:id/button1')
        button_allow = ('id', 'com.android.packageinstaller:id/permission_allow_button')
        cancel_text = ('xpath', "//*[@text='取消']")
        button_list.append(button_perm)
        button_list.append(button_allow)
        button_list.append(cancel_text)
        return button_list

    def run_watcher(self, max_retry=5):
        """
        this method should run when element not found, and set runWatcher at the same time
        """
        watchTriggered = False
        button_list = self._get_pop_list()
        _max_retry = max_retry
        ignore_pops = []
        #TODO fix this
        button_perm = 'android:id/button1'
        button_allow = 'com.android.packageinstaller:id/permission_allow_button'
        while _max_retry > 0:
            innerTrigger = False
            for button in button_list:
                (widget_control_type, widget_control) = button
                if widget_control in ignore_pops:
                    continue
                # wait should short, find_first: we do not need it
                flag = self.click((widget_control_type, widget_control), wait=0.3, runWatcher=False)
                if flag:
                    # 如果不是权限的弹窗，添加到下次的忽略列表中(权限弹窗有可能出现多次)
                    if widget_control not in (button_perm, button_allow):
                        ignore_pops.append(widget_control)
                    Logging.info('item with type: {} , control: {} exist, handle it.'.format(widget_control_type, widget_control))
                    innerTrigger = True
                    # if exist, sleep for a while
                    time_util.sleep(0.2)
                    break
            if not innerTrigger:
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
        if constant.CONTROL_TYPE_TEXT == _control_type.upper():
            _new_control_type = 'xpath'
            _new_control = "//*[@text='{}']".format(_control)
        elif constant.CONTROL_TYPE_TEXT_CONTAINS == _control_type.upper():
            _new_control_type = 'xpath'
            _new_control = "//*[contains(@text,'{}')]".format(_control)
        elif constant.CONTROL_TYPE_TEXT_STARTS_WITH == _control_type.upper():
            _new_control_type = 'xpath'
            _new_control = "//*[starts-with(@text,'{}')]".format(_control)
        elif constant.CONTROL_TYPE_ID == _control_type.upper():
            _new_control_type = 'id'
            # TODO convert :id to package:id
            _new_control = _control
        elif constant.CONTROL_TYPE_XPATH == _control_type.upper():
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
    
    def __keyevent(self, keyname, **kwargs):
        """
        Perform keyevent on the device
        Args:
            keyname: keyeven name
            **kwargs: optional arguments
        Returns:
            None
        """
        self.adb.keyevent(keyname)

    def disable_tbs(self):
        """
        use this to disable tbs
        """
        Logging.info('enter disable tbs.')
        # read current pkg name
        package_name = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_PKG_NAME)
        # first click search bar
        is_success = False 
        try:
            # wait for page appear
            page_control_type = 'xpath'
            page_control = "//*[@text='我的']"
            is_found = self.wait_until((page_control_type, page_control), timeout=20)
            if not is_found:
                Logging.info('{} not found, just continue it.')
            # first click search bar
            search_bar_control_type = 'id'
            search_bar_control = package_name + ":id/search_bar"
            Logging.info('search bar button:{}'.format(search_bar_control))
            clicked = self.click((search_bar_control_type, search_bar_control))
            if not clicked:
                raise Exception('search bar: {} click has failed.'.format(search_bar_control))
            Logging.info('click search bar:{} success.'.format(search_bar_control))
            # allow if exist
            allow_control_type = 'id'
            allow_control = "com.android.packageinstaller:id/permission_allow_button"
            el = self.find_element((allow_control_type, allow_control), wait=2)
            if el:
                Logging.info('permission allow button exist, click it.')
                el.click()
            # ensure in search page
            cancel_text_control_type = 'xpath'
            cancel_text_control = "//*[@text='取消']"
            Logging.info('cancel text:{}'.format(cancel_text_control))
            el = self.find_element((cancel_text_control_type, cancel_text_control), wait=5, runWatcher=True)
            if not el:
                raise Exception('cancel text with:{} not found.'.format(cancel_text_control))
            Logging.info('cancel text exists.')
            # enter open url
            tbs_url_control_type = 'id'
            tbs_url_control = package_name + ":id/et_search"
            tbs_openurl = '::openurl http://debugtbs.qq.com'
            self.text((tbs_url_control_type, tbs_url_control), tbs_openurl)
            Logging.info('enter tbs openurl has success.')
            # click search button
            search_pop_control_type = 'xpath'
            search_pop_control = "//*[contains(@text,'点击搜索')]"
            self.click((search_pop_control_type, search_pop_control), runWatcher=False)
            Logging.info('{} click success.'.format(search_pop_control))
            # ensure in debug page
            version_display_control_type = 'xpath'
            version_display_control = "//*[@text='查看版本信息']"
            el = self.find_element((version_display_control_type, version_display_control))
            if not el:
                raise Exception('open tbs debug page has failed, {} not found.'.format(version_display_control))
            Logging.info('ensure in tbs page.')
            # check tbs not disable text exist
            disable_tbs_control_type = 'xpath'
            disable_tbs_control = "//*[@text='内核未被禁用']"
            el = self.find_element((disable_tbs_control_type, disable_tbs_control), wait=5)
            if el:
                # click it
                time_util.sleep(0.8)
                el.click()
                time_util.sleep(0.4)
                # click reboot text
                reboot_control_type = 'xpath'
                reboot_control = "//*[@text='重启']"
                self.click((reboot_control_type, reboot_control))
                Logging.info('{} clicked.'.format(reboot_control))
                # wait for a while
                time_util.sleep(5)
            is_success = True
            Logging.info('disable tbs has success.')
        except Exception as e:
            Logging.info('disable tbs has an exception.')
            traceback.print_exc()
            Logging.info('wait for a while.')
            time_util.sleep(3)
        return is_success
