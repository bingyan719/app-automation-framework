from ui.utils import constant
from ui.utils import command
from ui.utils.log import Logging


def grant_permissions(settings):
    package_name = settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_PKG_NAME)
    device_id = settings.get_ini(constant.SECTION_DEVICE_INFO, constant.SECTION_DEVICE_INFO_ID)
    requested_permissions = __get_requested_permissions(device_id, package_name)
    __do_grant_permissions(device_id, package_name, requested_permissions)


def __get_requested_permissions(udid, package_name):
    requested_permissions = []
    require_flag = False
    outputs = command.cmd(['adb', '-s', udid, 'shell', 'pm', 'dump', package_name])
    for line in outputs.splitlines():
        line = line.strip()
        if 'requested permissions:' in line:
            require_flag = True
            continue
        if require_flag:
            if ('install permissions:' in line) or ('User 0:' in line):
                break
            requested_permissions.append(line.replace("\r\n", ""))
    return requested_permissions


def __do_grant_permissions(udid, package_name, requested_permissions):
    if not requested_permissions:
        return 
    for permission in requested_permissions:
        Logging.debug('granting permission: {}'.format(permission))
        try:
            outputs = command.cmd(['adb', '-s', udid, 'shell', 'pm', 'grant', package_name, permission], ignore_error=True, print_error=False)
            for line in outputs.splitlines():
                Logging.debug('granting permission output: {}'.format(line))
        except:
            Logging.error('granting permission has an exception, ignore it.')