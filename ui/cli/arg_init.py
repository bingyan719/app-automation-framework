import os
import time
import sys

from ui.utils.log import Logging
from ui.utils.config import Settings, Apps
from ui.utils import constant
from ui.utils.package_enums import PackageName


run_path = os.path.dirname(os.path.dirname(os.path.split(os.path.realpath(sys.argv[0]))[0]))


def init_from_file(file_path):
    Logging.info('init all settings from file:{}'.format(file_path))
    if not os.path.exists(file_path):
        Logging.error('specify init config file not exist, please check it first.')
        exit(2)
    constant.SETTINGS_CONFIG_PATH = file_path


def init_variables(settings, variables):
    """
    初始化命令行传递的运行变量，保存到settings.conf中
    """
    if not variables:
        Logging.info('no variables, aborting.')
        return
    if ';' in variables:
        items = variables.split(';')
        for item in items:
            item_name = item.split(':')[0]
            item_value = item.split(':')[1]
            settings.set_ini(constant.SECTION_VARIABLES_INFO, item_name, item_value)
    elif ':' in variables:
        item_name = item.split(':')[0]
        item_value = item.split(':')[1]
        settings.set_ini(constant.SECTION_VARIABLES_INFO, item_name, item_value)


def init_tools_info(settings):
    settings.set_ini(constant.SECTION_REPORT_INFO, constant.SECTION_REPORT_INFO_ROOT_PATH, run_path)
    settings.set_ini(constant.SECTION_REPORT_INFO, constant.SECTION_REPORT_INFO_RESULT_DIR, run_path + os.path.sep +'result')
    settings.set_ini(constant.SECTION_REPORT_INFO, constant.SECTION_REPORT_INFO_SOURCE_DIR, \
        run_path + os.path.sep + str(os.path.sep).join(['resources', 'core-reporter']))


def init_projects(settings, args):
    case_path = args.case_path
    apps = Apps()
    debug = settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_DEBUG)
    if debug.lower() != 'true':
        if args.project in (constant.PROJECT_NAME_SMT, constant.PROJECT_NAME_SMT_TEST, constant.PROJECT_NAME_SMT_IOS):
            case_path = '/Users/Shared/Jenkins/Home/workspace/App_Auto_Testcase/tests/android/smt'
        elif args.project == constant.PROJECT_NAME_NTSMT:
            case_path = '/Users/Shared/Jenkins/Home/workspace/App_Auto_Testcase/tests/android/nt_smt'
        elif args.project == constant.PROJECT_NAME_BASICSMT:
            case_path = '/Users/Shared/Jenkins/Home/workspace/App_Auto_Testcase/tests/android/smt_basic'
        elif args.project in (constant.PROJECT_NAME_GMSH, constant.PROJECT_NAME_GMSH_TEST):
            case_path = '/Users/Shared/Jenkins/Home/workspace/App_Auto_Testcase/tests/android/gmsh'
        elif args.project in (constant.PROJECT_NAME_ZS_PATIENT, ):
            case_path = '/Users/Shared/Jenkins/Home/workspace/App_Auto_Testcase/tests/android/zs_patient'
    Logging.info('init case path: {}'.format(case_path))
    settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_CASE_PATH, case_path)
    project = args.project
    Logging.info('project: {}'.format(project))
    try:
        section_info = apps.get_section(project)
    except:
        Logging.debug('section: {} not exists in apps.conf.')
        exit()
    # setup pkg name and app main activity name
    for item in section_info:
        if item == 'appPackage'.lower():
            settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_PKG_NAME, section_info[item])
        elif item == 'appActivity'.lower():
            settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_ACTIVITY_NAME, section_info[item])
        else:
            Logging.debug('unknown item: {} with value: {}'.format(item, section_info[item]))


def init_args(args):
    Logging.info('init args begins.')
    Logging.info('run path: {}'.format(run_path))
    settings = Settings()
    # set run path first
    settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_RUN_PATH, run_path)
    init_tools_info(settings)
    if args.config:
        Logging.info('--config specified, ignore all other command-line args.')
        init_from_file(args.config)
        return
    Logging.info('init from command-line args.')
    
    # check current test mode
    debug = 'False'
    if (type(args.debug) is bool and args.debug) \
            or (type(args.debug) is not bool and 'True' == args.debug):
        debug = 'True'
    Logging.info('--debug set it to: {}'.format(debug))
    settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_DEBUG, debug)
    # check device id specify it or not
    if not args.device:
        Logging.error('device not specify, please check it first.')
        exit(2)
    Logging.info('--device name: {}'.format(args.device))
    settings.set_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_ID, args.device)
    # check device type, if not specify it, set it to Android
    d_type = 'Android'
    if args.d_type and 'ios' == args.d_type.lower():
        d_type = 'iOS'
    Logging.info('--d_type set it to: {}'.format(d_type))
    settings.set_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_TYPE, d_type)
    # check cases path
    Logging.info('case path: {}'.format(args.case_path))
    settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_CASE_PATH, args.case_path)
    # check specify cases
    Logging.info('specify cases: {}'.format(args.specify_cases))
    settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_SPECIFY_CASES, args.specify_cases)
    # check testing environment
    Logging.info('testing environment: {}'.format(args.env))
    settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_ENV, args.env)
    # check testing project
    Logging.info('testing project: {}'.format(args.project))
    settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_PROJECT, args.project)
    # check testing origin sn
    Logging.info('testing origin sn: {}'.format(args.ori_sn))
    settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_ORI_SN, str(args.ori_sn))
    # check testing sn
    sn = args.sn
    if not sn :
        sn = int(time.time())
    Logging.info('testing sn: {}'.format(str(sn)))
    settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_SN, str(sn))
    # check specify case ids
    Logging.info('specify case ids: {}'.format(args.case_ids))
    settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_CASE_IDS, str(args.case_ids))
    # need comparison
    Logging.info('need comparison: {}'.format(args.need_comparison))
    settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_NEED_COMPARISON, str(args.need_comparison))
    # task token
    Logging.info('task token: {}'.format(args.task_token))
    settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_TASK_TOKEN, args.task_token)
    # FTP_NAME
    Logging.info('ftp name: {}'.format(args.ftp_name))
    settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_FTP_NAME, args.ftp_name)
    # apk path
    Logging.info('apk path: {}'.format(args.apk_path))
    settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_APK_PATH, args.apk_path)
    # build path
    Logging.info('build url: {}'.format(args.build_url))
    settings.set_ini(constant.SECTION_REPORT_INFO, constant.SECTION_REPORT_INFO_BUILD_URL, args.build_url)
    if args.build_url:
        report_path = str(args.build_url) + 'testreport'
        Logging.info('report path: {}'.format(report_path))
        settings.set_ini(constant.SECTION_REPORT_INFO, constant.SECTION_REPORT_INFO_REPORT_PATH, report_path)
    # init variables
    init_variables(settings, args.variables)
    # set retry times
    retry_times = int(args.retry_times)
    if debug.lower() == 'true':
        retry_times = 1
    Logging.info('test case retry times: {}'.format(retry_times))
    settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_RETRY_TIMES, str(retry_times))
    # set task mode
    mode = str(args.mode)
    Logging.info('task mode: {}'.format(mode))
    settings.set_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_MODE, mode)
    # init project
    init_projects(settings, args)
    Logging.info('init args ends.')
