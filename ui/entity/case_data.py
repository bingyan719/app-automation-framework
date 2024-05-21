#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2/24/18 7:24 PM
# @Author  : Icy Li


class CaseData(object):
    def __init__(self):
        self._id = 1
        self._test_name = ''
        self._test_priority = 1
        self._steps = []
        self._author = ''
        self._test_inherit = []

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def test_name(self):
        return self._test_name

    @test_name.setter
    def test_name(self, value):
        self._test_name = value

    @property
    def test_priority(self):
        return self._test_priority

    @test_priority.setter
    def test_priority(self, value):
        self._test_priority = value

    @property
    def steps(self):
        return self._steps

    @steps.setter
    def steps(self, value):
        self._steps = value

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        self._author = value

    @property
    def test_inherit(self):
        return self._test_inherit

    @test_inherit.setter
    def test_inherit(self, value):
        self._test_inherit = value
