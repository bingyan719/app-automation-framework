#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Icy Li
# @Date  : 2018/7/9
import os
import subprocess

from ui.utils.log import Logging
import platform


def cmd(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)


class Cp(object):

    def __darwin(self, port, device):
        for line in cmd(
                "ps -A | grep logcat | grep %s" % device).stdout.readlines():
            line = line.decode('utf-8').strip()
            pid = str(line.split(' ')[0].strip())
            cmd('kill -9 %s' % pid)
            Logging.debug('CleanProcess:Darwin:kill logcat')

    def darwin_kill_appium(self, port):
        if 'nt' not in os.name:
            os.system("lsof -n -i:%d | grep LISTEN | awk '{print $2}' | xargs kill -9" % int(port))
            Logging.debug('CleanProcess:Darwin:kill appium')
        else:
            Logging.debug('Windows no need kill appium,please close appium-desktop on your pc')

    def __linux(self, port, device):
        for line in cmd("ps -ef | grep logcat | grep %s|awk '{print $2}'" % device).stdout.readlines():
            cmd('kill -9 %s' % line.strip())
            Logging.debug('CleanProcess:linux:kill logcat')

    def __darwin_all(self, ):
        for line in cmd("ps -A | grep logcat|awk '{print $1}'").stdout.readlines():
            cmd('kill -9 %s' % line.strip())
            Logging.debug('CleanProcess:Darwin:kill logcat')
        for line in cmd("ps -A | grep appium|awk '{print $1}'").stdout.readlines():
            cmd('kill -9 %s' % line.strip())
            Logging.debug('CleanProcess:Darwin:kill appium')

    def __linux_all(self):
        for line in cmd("ps -ef | grep logcat|grep -v grep|awk '{print $2}'").stdout.readlines():
            cmd('kill -9 %s' % line.strip())
            Logging.debug('CleanProcess:linux:kill logcat')

        for line in cmd("ps -ef |grep appium |grep -v grep|awk '{print $2}'").stdout.readlines():
            cmd('kill -9 %s' % line.strip())
            Logging.debug('CleanProcess:linux:kill appium')

    def __windows(self):
        # todo windows
        for line in cmd("netstat -aon|findstr 4700").stdout.readlines():
            pid = line.strip().split(' ')[-1]
            process_name = cmd(
                'tasklist|findstr {}'.format(pid)).stdout.read().split(' ')[0]
            cmd('taskkill /f /t /im {}'.format(process_name))

    def clean_p(self, port, device):
        """
        clean logcat and appium specify process
        :return:
        """
        if platform.system() == 'Darwin':
            self.__darwin(port, device)
        elif platform.system() == 'Linux':
            self.__linux(port, device)
        else:
            Logging.debug('CleanProcess:Not identifying your operating system')

    def clean_all(self, ):
        """
        clean logcat and appium all process
        :return:
        """
        if platform.system() == 'Darwin':
            self.__darwin_all()
        elif platform.system() == 'Linux':
            self.__linux_all()
        else:
            Logging.debug('CleanProcess:Not identifying your operating system')

