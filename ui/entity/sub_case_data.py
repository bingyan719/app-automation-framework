#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2/24/18 7:24 PM
# @Author  : Icy Li


class SubCaseData(object):

    def __init__(self):
        self._step_id = 1
        self._step_desc = ''
        self._test_action = ''
        self._test_control_type = ''
        self._test_control = ''
        self._ios_control_type = ''
        self._ios_control = ''
        self._test_text = ''
        self._test_range = 1
        self._test_wait = 0
        self._screen_shot = ''
        self._ignore_blocks = []
        self._ignore_exception = ''

    @property
    def step_id(self):
        return self._step_id

    @step_id.setter
    def step_id(self, value):
        self._step_id = value

    @property
    def step_desc(self):
        return self._step_desc

    @step_desc.setter
    def step_desc(self, value):
        self._step_desc = value

    @property
    def test_control_type(self):
        return self._test_control_type

    @test_control_type.setter
    def test_control_type(self, value):
        self._test_control_type = value

    @property
    def test_action(self):
        return self._test_action

    @test_action.setter
    def test_action(self, value):
        self._test_action = value

    @property
    def test_control(self):
        return self._test_control

    @test_control.setter
    def test_control(self, value):
        self._test_control = value

    @property
    def test_text(self):
        return self._test_text

    @test_text.setter
    def test_text(self, value):
        self._test_text = value

    @property
    def test_range(self):
        return self._test_range

    @test_range.setter
    def test_range(self, value):
        self._test_range = value

    @property
    def test_wait(self):
        return self._test_wait

    @test_wait.setter
    def test_wait(self, value):
        self._test_wait = value

    @property
    def screen_shot(self):
        return self._screen_shot

    @screen_shot.setter
    def screen_shot(self, value):
        self._screen_shot = value

    @property
    def ios_control_type(self):
        return self._ios_control_type

    @ios_control_type.setter
    def ios_control_type(self, value):
        self._ios_control_type = value

    @property
    def ios_control(self):
        return self._ios_control

    @ios_control.setter
    def ios_control(self, value):
        self._ios_control = value

    def get_ignore_blocks(self):
        return self._ignore_blocks

    def append_ignore_blocks(self, new_block):
        self._ignore_blocks.append(new_block)

    @property
    def ignore_exception(self):
        return self._ignore_exception

    @ignore_exception.setter
    def ignore_exception(self, value):
        self._ignore_exception = value