#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Icy Li
# @Date  : 2018/7/16


class Job(object):
    def __init__(self):
        self._success = 0
        self._fail = 0
        self._total = 0
        self._startTime = ''
        self._endTime = ''
        self._package_name = ''
        self._device_name = ''
        self._wifi_name = ''
        self._system_version = ''
        self._suites = []
        self._package_name_version = ''

    @property
    def success(self):
        return self._success

    @success.setter
    def success(self, value):
        self._success = value

    @property
    def fail(self):
        return self._fail

    @fail.setter
    def fail(self, value):
        self._fail = value

    @property
    def total(self):
        return self._total

    @total.setter
    def total(self, value):
        self._total = value

    @property
    def startTime(self):
        return self._startTime

    @startTime.setter
    def startTime(self, value):
        self._startTime = value

    @property
    def endTime(self):
        return self._endTime

    @endTime.setter
    def endTime(self, value):
        self._endTime = value

    @property
    def package_name(self):
        return self._package_name

    @package_name.setter
    def package_name(self, value):
        self._package_name = value

    @property
    def device_name(self):
        return self._device_name

    @device_name.setter
    def device_name(self, value):
        self._device_name = value

    @property
    def wifi_name(self):
        return self._wifi_name

    @wifi_name.setter
    def wifi_name(self, value):
        self._wifi_name = value

    @property
    def system_version(self):
        return self._system_version

    @system_version.setter
    def system_version(self, value):
        self._system_version = value

    @property
    def suites(self):
        return self._suites

    @suites.setter
    def suites(self, value):
        self._suites = value

    @property
    def package_name_version(self):
        return self._package_name_version

    @package_name_version.setter
    def package_name_version(self, value):
        self._package_name_version = value