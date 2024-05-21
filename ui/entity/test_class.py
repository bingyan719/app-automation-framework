#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Icy Li
# @Date  : 2018/7/16


class TestClasss(object):
    def __init__(self):
        self._class_name = ''
        self._data_path = ''
        self._data_path_key = ''
        self._data_file = ''
        self._endTime = ''
        self._startTime = ''
        self._case_list = []

    @property
    def class_name(self):
        return self._class_name

    @class_name.setter
    def class_name(self, value):
        self._class_name = value

    @property
    def data_path(self):
        return self._data_path

    @data_path.setter
    def data_path(self, value):
        self._data_path = value

    @property
    def data_path_key(self):
        return self._data_path_key

    @data_path_key.setter
    def data_path_key(self, value):
        self._data_path_key= value

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
    def data_file(self):
        return self._data_file

    @data_file.setter
    def data_file(self, value):
        self._data_file = value

    @property
    def case_list(self):
        return self._case_list

    @case_list.setter
    def case_list(self, value):
        self._case_list = value