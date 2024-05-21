import re

from ui.utils.log import Logging
from ui.utils.command import cmd


class Environment(object):

    def __init__(self, uuid):
        self.uuid = uuid

    def check(self):
        Logging.info('enter android environment check.')
        if not self.is_device_present():
            Logging.error('device not ready.')
            exit()
        Logging.info('android environment check ok...')

    def get_all_adroid_devices(self, state='device'):
        cmds = ['adb', 'devices']
        patten = re.compile(r'^[\w\d.:-]+\t[\w]+$')
        device_list = []
        outputs = cmd(cmds)
        for line in outputs.splitlines():
            line = line.strip()
            if not line or not patten.match(line):
                continue
            serialno, cstate = line.split('\t')
            if state and cstate != state:
                continue
            device_list.append(serialno)
        return device_list

    def is_device_present(self):
        devices = self.get_all_adroid_devices()
        return self.uuid in devices