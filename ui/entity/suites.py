#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Icy Li
# @Date  : 2018/7/16


class Suites(object):
    def __init__(self):
        self._success = 0
        self._fail = 0
        self._total = 0
        self._startTime = ''
        self._endTime = ''
        self._suite_name = ''
        self._test_classes_list = []
        self._retry_times = 0

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
    def suite_name(self):
        return self._suite_name

    @suite_name.setter
    def suite_name(self, value):
        self._suite_name = value

    @property
    def test_classes_list(self):
        return self._test_classes_list

    @test_classes_list.setter
    def test_classes_list(self, value):
        self._test_classes_list = value

    @property
    def retry_times(self):
        return self._retry_times

    @retry_times.setter
    def retry_times(self, value):
        self._retry_times = value