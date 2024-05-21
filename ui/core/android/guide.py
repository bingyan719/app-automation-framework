from ui.utils.log import Logging
from ui.utils import constant
from ui.utils import time_util
from ui.core.api import current_activity, swipe_left_full, tap, click, run_watcher

class GuideUtil(object):

    def __init__(self, settings, uuid):
        self.settings = settings
        self.uuid = uuid

    def handle_guide(self):
        Logging.info('handling android guide.')
        package_name = self.settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_PKG_NAME)
        package_name_list = ['com.ABCD.smt', 'com.ABCD.smt.test', 'com.ABCD.nt', 'com.ABCD.smt.template']
        activity_list = ['com.ABCD.smt.WelcomeGuideActivity',
        'com.ABCD.smt.activity.WelcomeGuideActivity',
        'com.ABCD.smt.ui.activity.WelcomeGuideActivity',
        'com.pasc.business.setting.activity.WelcomeGuideActivity',
        '.module.appstart.WelcomeGuideActivity']
        if str(package_name) in ('com.ABCD.smt.test', 'com.ABCD.smt'):
            num = 4
        elif str(package_name) in ('com.ABCD.nt', 'com.ABCD.smt.template'):
            num = 2
        else:
            num = 4
        _current_activity = str(current_activity())
        Logging.debug('current activity name: {}'.format(_current_activity))
        if _current_activity.startswith('.'):
            _current_activity = package_name + _current_activity
        if str(package_name) in package_name_list and _current_activity in activity_list:
            for i in range(num):
                swipe_left_full()
            time_util.sleep(3)
            if str(package_name) in ('com.ABCD.smt.test', 'com.ABCD.smt'):
                click(('id', '{}:id/btn_enter'.format(package_name)), runWatcher=False)
                # 第一次执行, 等待三秒钟，处理弹窗
                time_util.sleep(3)
                run_watcher()
            elif str(package_name) in ('com.ABCD.nt', 'com.ABCD.smt.template'):
                tap(10, 30)
        Logging.info('handling android guide ends.')
    
    