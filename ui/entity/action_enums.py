#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Icy Li
# @Date  : 2018/8/11


from enum import Enum


class ActionType(Enum):
    Click = 'click',
    LongClick = 'longclick',
    SendKeys = 'send_keys',
    StartApp = 'start_app',
    Tap = 'tap',
    Wait = 'wait',
    WaitUntil = 'wait_until',
    SwipeUntil = 'swipe_',
    AssertExists = 'assert_exist',
    AssertNotExists = 'assert_not_exist',
