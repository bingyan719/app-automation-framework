import re

from ui.utils.log import Logging
from ui.utils.command import cmd

class Environment(object):

    def __init__(self, uuid):
        self.uuid = uuid

    def check(self):
        Logging.info('enter ios environment check.')
        if not self.is_device_present():
            Logging.error('device not ready.')
            exit()
        Logging.info('ios environment check ok...')

    def get_all_adroid_devices(self, state='device'):
        cmds = ['idevice_id', '-l']
        device_list = []
        outputs = cmd(cmds)
        for line in outputs.splitlines():
            line = line.strip()
            device_list.append(line)
        return device_list

    def is_device_present(self):
        devices = self.get_all_adroid_devices()
        return self.uuid in devices