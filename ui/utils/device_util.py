from ui.utils import command
from ui.utils.log import Logging

IOS_PRODUCT_MAPPING = {
    'iPhone1,1':'iPhone 1G',
    'iPhone1,2':'iPhone 3G',
    'iPhone2,1':'iPhone 3GS',
    'iPhone3,1':'iPhone 4',
    'iPhone3,2':'iPhone 4 Verizon',
    'iPhone4,1':'iPhone 4S',
    'iPhone5,2':'iPhone 5',
    'iPhone5,3':'iPhone 5c',
    'iPhone5,4':'iPhone 5c',
    'iPhone6,1':'iPhone 5s',
    'iPhone6,2':'iPhone 5s',
    'iPhone7,1':'iPhone 6 Plus',
    'iPhone7,2':'iPhone 6',
    'iPhone8,1':'iPhone 6s',
    'iPhone8,2':'iPhone 6s Plus',
    'iPhone8,4':'iPhone SE',
    'iPhone9,1':'iPhone 7',
    'iPhone9,2':'iPhone 7 Plus',
    'iPhone9,3':'iPhone 7',
    'iPhone9,4':'iPhone 7 Plus',
    'iPhone10,1':'iPhone 8',
    'iPhone10,2':'iPhone 8 Plus',
    'iPhone10,3':'iPhone X',
    'iPhone10,4':'iPhone 8',
    'iPhone10,5':'iPhone 8 Plus',
    'iPhone10,6':'iPhone X',
    'iPhone11,2':'iPhone XS',
    'iPhone11,4':'iPhone XS Max',
    'iPhone11,6':'iPhone XS Max',
    'iPhone11,8':'iPhone XR',
}

def get_android_platform_version(udid):
    outputs = command.cmd(['adb', '-s', udid, 'shell', 'getprop', 'ro.build.version.release'])
    platformName = 'N/A'
    for line in outputs.splitlines():
        platformName = line.strip().replace('\r\n', '')
        Logging.info('android platform version: {}'.format(line))
        break
    return platformName


def get_ios_platform_version(udid):
    outputs = command.cmd(['ideviceinfo', '-u', udid, '-k', 'ProductVersion'])
    platformName = 'N/A'
    for line in outputs.splitlines():
        platformName = line.strip().replace('\r\n', '')
        Logging.info('ios platform version: {}'.format(line))
        break
    return platformName


def get_android_device_manufacturer(udid):
    """
    :return: 手机厂商 :huawei
    """
    outputs = command.cmd(['adb', '-s', udid, 'shell', 'getprop', 'ro.product.manufacturer'])
    manufacturer = 'N/A'
    for line in outputs.splitlines():
        manufacturer = line.strip().replace('\r\n', '')
        Logging.info('android manufacturer: {}'.format(line))
        break
    return manufacturer.lower().replace(' ', '')


def get_ios_device_manufacturer(udid):
    return 'apple'


def get_android_device_name(udid):
    """
    :return: 设备名 :SM-G9006W
    """
    outputs = command.cmd(['adb', '-s', udid, 'shell', 'getprop', 'ro.product.model'])
    model = 'N/A'
    for line in outputs.splitlines():
        model = line.strip().replace('\r\n', '')
        Logging.info('android model: {}'.format(line))
        break
    return model.lower().replace(' ', '')


def get_ios_device_name(udid):
    outputs = command.cmd(['ideviceinfo', '-u', udid, '-k', 'ProductType'])
    model = 'N/A'
    for line in outputs.splitlines():
        model = line.strip().replace('\r\n', '')
        Logging.info('ios platform version: {}'.format(line))
        break
    model = IOS_PRODUCT_MAPPING.get(model, 'N/A')
    return model.lower().replace(' ', '')


def get_android_device_brand(udid):
    """
    :return: 品牌 :oppo
    """
    outputs = command.cmd(['adb', '-s', udid, 'shell', 'getprop', 'ro.product.brand'])
    brand = 'N/A'
    for line in outputs.splitlines():
        brand = line.strip().replace('\r\n', '')
        Logging.info('android brand: {}'.format(line))
        break
    return brand.lower().replace(' ', '')
