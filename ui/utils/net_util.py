import socket
import requests

from ui.utils import constant
from ui.utils.log import Logging


def get_random_port_with_retry(port, ip='127.0.0.1', retry=5):
    new_port = port
    retry_counter = 0
    while( retry_counter < 5):
        is_open = _is_port_open(ip, port)
        if is_open:
            # 端口被占用，自动加1重试
            new_port += 1
        else:
            # 端口未被占用，跳出循环返回
            break
        # 重试次数变量自增
        retry_counter += 1
    return new_port

def _is_port_open(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(ip, int(port))
        s.shutdown(2)
        return True
    except:
        return False


def send_start_status(settings, serial):
    Logging.info('begin sending device starting status to server...')
    env = settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_ENV)
    mode = settings.get_ini(constant.SECTION_TEST_INFO,  constant.SECTION_TEST_INFO_MODE)
    debug = str(settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_DEBUG))
    if 'true' == debug.lower():
        Logging.info('debug mode, ignore sending device starting status to server...')
        return
    task_token = settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_TASK_TOKEN)
    params = {'task_id': task_token,
            'serial': serial,
            'status': '1',}
    send_status(env, mode, params)

def send_finish_status(settings, serial):
    Logging.info('begin sending device finish status to server...')
    env = settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_ENV)
    mode = settings.get_ini(constant.SECTION_TEST_INFO,  constant.SECTION_TEST_INFO_MODE)
    debug = str(settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_DEBUG))
    if 'true' == debug.lower():
        Logging.info('debug mode, ignore sending device finish status to server...')
        return
    task_token = settings.get_ini(constant.SECTION_TEST_INFO,  constant.SECTION_TEST_INFO_TASK_TOKEN)
    pass_counter = settings.get_ini(constant.SECTION_TEST_INFO,  constant.SECTION_TEST_INFO_PASS_COUNTER)
    fail_counter = settings.get_ini(constant.SECTION_TEST_INFO,  constant.SECTION_TEST_INFO_FAIL_COUNTER)
    no_execute_counter = settings.get_ini(constant.SECTION_TEST_INFO,  constant.SECTION_TEST_INFO_NO_EXEC_COUNTER)
    report_path = settings.get_ini(constant.SECTION_REPORT_INFO,  constant.SECTION_REPORT_INFO_REPORT_PATH)
    need_compare = settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_NEED_COMPARE)
    fail_case_names = 'N/A'
    if int(fail_counter) > 0:
        fail_case_names = settings.get_ini(constant.SECTION_TEST_INFO,  'fail_case_names')
    params = {'task_id': task_token,
            'serial': serial,
            'status': '2',
            'pass_counter': pass_counter,
            'fail_counter': fail_counter,
            'no_execute_counter': no_execute_counter,
            'report_path': report_path,
            'fail_cases': fail_case_names,
            'need_compare': need_compare,
            }
    if int(fail_counter) > 0 and env.lower() == 'uimonitorsandbox':
        # just ui monitor sending wechat message
        total_counter = int(pass_counter) + int(fail_counter)
        send_wechat_messages_record(mode, task_token, total_counter, pass_counter, fail_counter, fail_case_names)
    send_status(env, mode, params)

def send_wechat_messages_record(mode, task_token, total_counter, pass_counter, fail_counter, fail_case_names):
    try:
        params = {'task_id': task_token,
                    'group': constant.icyiy_WECHAT_MESSAGE_GROUP,
                    'total_counter': total_counter,
                    'pass_counter': pass_counter,
                    'fail_counter': fail_counter,
                    'fail_case_names': fail_case_names,
                    }
        if mode == 'debug':
            request_url = constant.icyiy_DEBUG_DOMAIN + '/app_api/wechat_message_record'
        else:
            request_url = constant.icyiy_RELEASE_DOMAIN + '/app_api/wechat_message_record'
        if not int(pass_counter) == 0 and int(fail_counter) < 6:
            response = requests.post(url=request_url, data=params)
            if response.status_code != 200:
                Logging.info('sending wechat message to server failure. reason: {}'.format(response.text))
                return
            Logging.info('sending wechat message to server success.')
    except Exception as e:
        # we can not do anything about this, because network is down
        Logging.info('sending wechat message to server failure: {}'.format(e))

def send_status(env, mode, params):
    try:
        if mode == 'debug':
            if env.upper() == 'UISANDBOX':
                request_url = constant.icyiy_DEBUG_DOMAIN + '/ui_function/device_status_update'
            elif env.upper() == 'COMPATISANDBOX':
                request_url = constant.icyiy_DEBUG_DOMAIN + '/compatibility/device_status_update'
            else:
                request_url = constant.icyiy_DEBUG_DOMAIN + '/ui_monitor/device_status_update'
        else:
            if env.upper() == 'UISANDBOX':
                request_url = constant.icyiy_RELEASE_DOMAIN + '/ui_function/device_status_update'
            elif env.upper() == 'COMPATISANDBOX':
                request_url = constant.icyiy_RELEASE_DOMAIN + '/compatibility/device_status_update'
            else:
                request_url = constant.icyiy_RELEASE_DOMAIN + '/ui_monitor/device_status_update'
        response = requests.post(url=request_url, data=params)
        if response.status_code != 200:
            Logging.info('sending device status to server failure. reason: {}'.format(response.text))
            return
        Logging.info('sending device status to server success.')
    except Exception as e:
        # we can not do anything about this, because network is down
        Logging.info('sending device status to server failure: {}'.format(e))

def send_comparison_request(mode, task, serial, project, version, system, brand, model):
    try:
        if mode == 'debug':
            request_url = 'http://10.161.121.23:5005/image_comparison/debug/{}/{}/{}/{}/{}/{}/{}'.format(task, serial, project, version, system, brand, model)
        else:
            request_url = 'http://10.161.121.23:5005/image_comparison/{}/{}/{}/{}/{}/{}/{}'.format(task, serial, project, version, system, brand, model)
        Logging.info('comparison request url: {}'.format(request_url))
        response = requests.get(url=request_url)
        if response.status_code != 200:
            Logging.info('sending comparison to server failure. reason: {}'.format(response.text))
            return
        Logging.info('sending comparison to server success.')
    except Exception as e:
        # we can not do anything about this, because network is down
        Logging.info('sending comparison to server failure: {}'.format(e))