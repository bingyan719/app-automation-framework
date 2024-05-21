from ui.utils.log import Logging
from ui.utils import constant
from ui.utils import time_util
from ui.core.api import swipe_left_full, click, run_watcher
from ui.core.common import get_ios_predicate_content

class GuideUtil(object):

    def __init__(self, settings, uuid):
        self.settings = settings
        self.uuid = uuid

    def handle_guide(self):
        Logging.info('handling ios guide.')
        # 先处理权限弹窗, 第一次执行, 等待三秒钟，处理弹窗
        Logging.info('handling ios permission dialogs.')
        time_util.sleep(3)
        run_watcher()
        # 处理首屏
        Logging.info('handling ios splash screens.')
        time_util.sleep(0.8)
        package_name = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_PKG_NAME)
        package_name_list = ['com.ABCD.epsmtsz', ]
        if str(package_name) == 'com.ABCD.epsmtsz':
            num = 4
        else:
            num = 4
        for i in range(num):
            swipe_left_full()
        time_util.sleep(3)
        if str(package_name) == 'com.ABCD.epsmtsz':
            Logging.info('handling ios introduce button.')
            is_clicked = click(("predicate", get_ios_predicate_content('introduce 按钮')), runWatcher=False)
            if is_clicked:
                Logging.info('ios introduce button has clicked.')
            # 第一次执行, 等待三秒钟，处理弹窗
            time_util.sleep(3)
            run_watcher()
        Logging.info('handling ios guide ends.')