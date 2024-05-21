import sys
import argparse


def parse_args(args=sys.argv[1:]):
    """
    初始化命令行参数
    """
    parser = argparse.ArgumentParser(description='Init Command Line Args')
    # 指定当前是否是测试模式
    parser.add_argument('--debug', help='current is debug or release mode.', action='store_true', default=False)
    # 指定测试设备的序列号
    parser.add_argument('--device', help='specify device serial or udid', default='S2D0219126008969')
    # 指定测试类型，当前只支持Android或iOS
    parser.add_argument('--d_type', help='specify test type, current support type: Android, iOS', default='Android',choices=['Android', 'iOS'])
    # 指定测试项目
    parser.add_argument('--project', help="specify testing project", default='smt')
    # 指定case绝对路径
    parser.add_argument('--case_path', help='automation test cases root path', default='/Users/icyiy123889/projects/App_Auto_Testcase/tests/android/smt')
    # 指定要测试的用例集
    parser.add_argument('--specify_cases', help="specify automation test cases to run", default='发改委更新')
    # 指定测试的用例集下的用例
    parser.add_argument('--case_ids', help="specify test case ids", default='')
    # 指定任务的模式
    parser.add_argument('--mode', help="mode for this task, must be debug or release", default='debug', choices=['release', 'debug'])
    # 指定测试环境
    parser.add_argument('--env', help="specify testing environment", default='dev')
    # 指定任务原始sn
    parser.add_argument('--ori_sn', help="specify testing origin sn", default=0)
    # 指定任务sn
    parser.add_argument('--sn', help="specify testing sn", default=0)
    # 指定是否需要兼容图像比对
    parser.add_argument('--need_comparison', help="need comparison or not, mostly only for compatibility test", default='0')
    # 指定任务的task_token值
    parser.add_argument('--task_token', help="test task token", default='')
    # 指定任务的ftp_name值
    parser.add_argument('--ftp_name', help="ftp name for target testing application", default='')
    # 指定任务的apk_path值
    parser.add_argument('--apk_path', help="apk path for target testing application", default='')
    # 指定任务的build_url值
    parser.add_argument('--build_url', help="build url for this task", default='')
    # 指定任务的变量值
    parser.add_argument('--variables', help="variables for running environment", default='')
    # 指定任务测试用例在失败时重试次数
    parser.add_argument('--retry_times', help="max retry times for each test case", default='3')
    # 指定配置文件的路径
    parser.add_argument('--config', help='specify absolute path for config that hold all paramaters.')
    return parser.parse_args(args)