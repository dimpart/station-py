# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2020 Albert Moky
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

from dimples.common.compat import CommonExtensionLoader

from .protocol import *


class ExtensionLoader(CommonExtensionLoader):

    # Override
    def register_command_factories(self):
        super().register_command_factories()
        # APNs
        self._set_command_factory(cmd=PushCommand.PUSH, command_class=PushCommand)
        # Report extra
        self._set_command_factory(cmd='broadcast', command_class=ReportCommand)
        self._set_command_factory(cmd=ReportCommand.ONLINE, command_class=ReportCommand)
        self._set_command_factory(cmd=ReportCommand.OFFLINE, command_class=ReportCommand)

        # Storage (contacts, private_key)
        self._set_command_factory(cmd=StorageCommand.STORAGE, command_class=StorageCommand)
        self._set_command_factory(cmd=StorageCommand.CONTACTS, command_class=StorageCommand)
        self._set_command_factory(cmd=StorageCommand.PRIVATE_KEY, command_class=StorageCommand)
        # Search (users)
        self._set_command_factory(cmd=SearchCommand.SEARCH, command_class=SearchCommand)
        self._set_command_factory(cmd=SearchCommand.ONLINE_USERS, command_class=SearchCommand)
