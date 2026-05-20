# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2019 Albert Moky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

"""
    Utils
    ~~~~~

    I'm too lazy to write codes for demo project, so I borrow some utils here
    from the <dimsdk> packages, but I don't suggest you to do it also, because
    I won't promise these private utils will not be changed. Hia hia~ :P
                                             -- Albert Moky @ Jan. 23, 2019
"""

from startrek.skywalker import Runnable, Daemon
# from ipx import Notification, NotificationObserver, NotificationCenter as DefaultNotificationCenter

from dimples.utils import Singleton, Runner
from dimples.utils import Path
from dimples.utils import File, TextFile, JSONFile

from dimples.utils import SysArgvParser
from dimples.utils import Log, Logging
from dimples.utils import Config

from dimples.utils import utf8_encode, utf8_decode
from dimples.utils import json_encode, json_decode

from dimples.utils import get_msg_sig


# @Singleton
# class NotificationCenter(DefaultNotificationCenter):
#     pass


# def get_msg_sig(msg, cnt: int = 8) -> str:
#     sig = msg.get('signature')
#     if sig is not None:
#         sig = sig.rstrip()
#         if len(sig) > cnt:
#             sig = sig[-cnt:]
#     return sig


__all__ = [

    'Runnable', 'Runner',
    'Daemon',
    # 'Notification', 'NotificationObserver', 'NotificationCenter',

    'Singleton',
    'Path',
    'File', 'TextFile', 'JSONFile',

    'SysArgvParser',
    'Log', 'Logging',
    'Config',

    'utf8_encode', 'utf8_decode',
    'json_encode', 'json_decode',

    'get_msg_sig',

]
