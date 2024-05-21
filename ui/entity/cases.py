#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Icy Li
# @Date  : 2018/7/16


class Cases(object):
    def __init__(self):
        self._case_name = ''
        self._result = ''
        self._data_name = ''
        self._group_name = ''
        self._endTime = ''
        self._startTime = ''
        self._parameter = ''
        self._exception = ''
        self._case_id = ''
        self._desc = ''
        self._logs = []

    @property
    def case_id(self):
        return self._case_id

    @case_id.setter
    def case_id(self, value):
        self._case_id = value

    @property
    def case_name(self):
        return self._case_name

    @case_name.setter
    def case_name(self, value):
        self._case_name = value

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value

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
    def data_name(self):
        return self._data_name

    @data_name.setter
    def data_name(self, value):
        self._data_name = value

    @property
    def group_name(self):
        return self._group_name

    @group_name.setter
    def group_name(self, value):
        self._group_name = value

    @property
    def parameter(self):
        return self._parameter

    @parameter.setter
    def parameter(self, value):
        self._parameter = value

    @property
    def exception(self):
        return self._exception

    @exception.setter
    def exception(self, value):
        self._exception = value

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, value):
        self._desc = value

    @property
    def logs(self):
        return self._logs

    @logs.setter
    def logs(self, value):
        self._logs = value