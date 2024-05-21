# for settings.conf file name
SETTINGS_CONFIG_PATH = ''


# for settings

# section device info
SECTION_DEVICE_INFO = 'device_info'
SECTION_DEVICE_INFO_ID = 'device'
SECTION_DEVICE_INFO_TYPE = 'type'

# section test info
SECTION_TEST_INFO = 'test_info'
SECTION_TEST_PKG_NAME = 'pkg_name'
SECTION_TEST_ACTIVITY_NAME = 'main_activity'
SECTION_TEST_INFO_DEBUG = 'debug'
SECTION_TEST_INFO_CASE_PATH = 'case_path'
SECTION_TEST_INFO_SPECIFY_CASES = 'specify_cases'
SECTION_TEST_INFO_ENV = 'env'
SECTION_TEST_INFO_PROJECT = 'project'
SECTION_TEST_INFO_ORI_SN = 'ori_sn'
SECTION_TEST_INFO_SN = 'sn'
SECTION_TEST_INFO_CASE_IDS = 'case_ids'
SECTION_TEST_INFO_NEED_COMPARISON = 'need_comparison'
SECTION_TEST_INFO_TASK_TOKEN = 'task_token'
SECTION_TEST_INFO_FTP_NAME = 'ftp_name'
SECTION_TEST_INFO_APK_PATH = 'apk_path'
SECTION_TEST_INFO_VARIABLES = 'variables'
SECTION_TEST_INFO_RETRY_TIMES = 'retry_times'
SECTION_TEST_INFO_RUN_PATH = 'run_path'
SECTION_TEST_INFO_MODE = 'mode'
SECTION_TEST_INFO_PASS_COUNTER = 'pass_counter'
SECTION_TEST_INFO_FAIL_COUNTER = 'fail_counter'
SECTION_TEST_INFO_NO_EXEC_COUNTER = 'no_execute_counter'
SECTION_TEST_INFO_FAIL_CASES_NAME = 'fail_case_names'
SECTION_TEST_INFO_NEED_COMPARE = 'need_compare'

# section report info
SECTION_REPORT_INFO = 'report_info'
SECTION_REPORT_INFO_BUILD_URL = 'build_url'
SECTION_REPORT_INFO_ROOT_PATH = 'root_path'
SECTION_REPORT_INFO_REPORT_PATH = 'report_path'
SECTION_REPORT_INFO_RESULT_DIR= 'result_dir'
SECTION_REPORT_INFO_SOURCE_DIR = 'source_dir'

# section variables info
SECTION_VARIABLES_INFO = 'variables_info'

# section tool info
SECTION_TOOL_INFO = 'tool_info'
SECTION_TOOL_INFO_MINICAP = 'minicap_path'
SECTION_TOOL_INFO_MINITOUCH = 'minitouch_path'
SECTION_TOOL_INFO_MINICAP_SO = 'minicapso_path'

# project info
PROJECT_NAME_SMT = 'smt'
PROJECT_NAME_SMT_TEST = 'smt_test'
PROJECT_NAME_SMT_IOS = 'smt_ios'
PROJECT_NAME_NTSMT = 'nt_smt'
PROJECT_NAME_BASICSMT = 'basic_smt'
PROJECT_NAME_NTSMT_TEST = 'nt_smt_test'
PROJECT_NAME_BASICSMT_TEST = 'basic_smt_test'
PROJECT_NAME_GMSH = 'gmsh'
PROJECT_NAME_GMSH_TEST = 'gmsh_test'
PROJECT_NAME_ZS_PATIENT = 'zs_patient'

# env info
SANDBOX = 'sandbox'

# only for uimonitor task for cache apps
DIR_FOR_CACHE_APPS = '/Users/Shared/App/CacheApps'

# for ftp
FTP_SERVER = '10.161.121.23'
FTP_PORT = 2121
FTP_USER = 'admin'
FTP_PASSWORD = 'admin'

# for db
DB_HOST = '10.161.121.23'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWROD = 'root'

# max install retry times
INSTALL_RETRY_TIMES = 3

# appium max retry times
APPIUM_MAX_RETRY_TIMES = 5

# default appium port
APPIUM_PORT = 4723

# for assertion wait timeout
ASSERT_WAIT_TIMEOUT = 15

# for wait timeout
WAIT_TIMEOUT = 5

# for operation delay
OPDELAY = 0.1
MAX_SWIPE_TIMES = 10
SWIPE_PADDING = 0.2

# constant for direction
UP = 'UP'
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'

# action type
CONTROL_TYPE_TEXT = 'TEXT'
CONTROL_TYPE_TEXT_CONTAINS = 'TEXT_CONTAINS'
CONTROL_TYPE_TEXT_STARTS_WITH = 'TEXT_STARTS_WITH'
CONTROL_TYPE_TEXT_ENDS_WITH = 'TEXT_ENDS_WITH'
CONTROL_TYPE_ID = 'ID'
CONTROL_TYPE_XPATH = 'XPATH'

# FOR icyiy SITE
icyiy_DEBUG_DOMAIN = 'http://10.161.62.199:8001'
icyiy_RELEASE_DOMAIN = 'http://10.161.38.76:8001'
icyiy_WECHAT_MESSAGE_GROUP = '服务监控群'