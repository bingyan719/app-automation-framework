from ui.utils import constant
from ui.utils.log import Logging
from ui.utils.db_util import get_test_platform_db_connection


def convert_testcase_suites(settings):
    env = settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_ENV)
    mode = settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_MODE)
    debug = str(settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_DEBUG))
    if 'true' == debug.lower():
        Logging.info('debug mode skip case convert.')
        return
    Logging.debug('converting testcase suite ids to text')
    all_suite_ids = settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_SPECIFY_CASES)
    if not all_suite_ids:
        return
    if all_suite_ids != '0':
        suite_list = []
        try:
            conn = get_test_platform_db_connection(mode)
            sql = 'select suite_name from app_automation_android_suites where id in ({})'.format(str(all_suite_ids).replace('|', ','))
            Logging.debug('query sql: {}'.format(sql))
            with conn.cursor() as cursor:
                cursor.execute(sql)
                for suite_name in cursor:
                    suite_list.append(suite_name[0])
            if not len(suite_list) > 0:
                Logging.error('no test suite in database, check it first.')
                exit()
            settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_SPECIFY_CASES, '|'.join(suite_list))
        finally:
            if conn:
                conn.close()
    else:
        settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_SPECIFY_CASES, 'All')