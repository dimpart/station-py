#! /usr/bin/env python3
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
    Service Bot
    ~~~~~~~~~~~
    Bot for statistics

    Data format:

        "users_log-{yyyy}-{mm}-{dd}.js"

            {
                "yyyy-mm-dd HH:MM": [
                    {
                        "U" : "user_id",
                        "IP": "127.0.0.1"
                    }
                ]
            }

        "stats_log-{yyyy}-{mm}-{dd}.js"

            {
                "yyyy-mm-dd HH:MM": [
                    {
                        "S": 0,
                        "T": 1,
                        "C": 2
                    }
                ]
            }

        "speeds_log-{yyyy}-{mm}-{dd}.js"

            {
                "yyyy-mm-dd HH:MM": [
                    {
                        "U"            : "user_id",
                        "provider"     : "provider_id",
                        "station"      : "host:port",
                        "client"       : "host:port",
                        "response_time": 0.125
                    }
                ]
            }

    Fields:
        'S' - Sender type
        'C' - Counter
        'U' - User ID
        'T' - message Type

    Sender type:
        https://github.com/dimchat/mkm-py/blob/master/mkm/protocol/entity.py

    Message type:
        https://github.com/dimchat/dkd-py/blob/master/dkd/protocol/types.py
"""

import sys
from typing import List

from dimples import ID, ReliableMessage
from dimples import Content
from dimples import CustomizedContent
from dimples import Messenger

from dimples.client import ClientFacebook, ClientMessenger
from dimples.client import ClientMessageProcessor
from dimples.client.cpu import BaseCustomizedContentHandler
from dimples.client.cpu.app.filter import get_app_filter

from dimples.utils import SysArgvParser
from dimples.utils import init_logger
from dimples.utils import Log, LogLevel, Logging
from dimples.utils import Runner
from dimples.utils import Path

path = Path.abs(path=__file__)
path = Path.dir(path=path)
path = Path.dir(path=path)
Path.add(path=path)

from sbots.shared import GlobalVariable
from sbots.shared import create_config, start_bot
from sbots.shared import show_help


def _get_listeners(name: str) -> List[ID]:
    shared = GlobalVariable()
    config = shared.config
    text = config.get_string(section='monitor', option=name)
    text = text.replace(' ', '')
    if len(text) == 0:
        return []
    array = text.split(',')
    return ID.convert(array=array)


class StatHandler(BaseCustomizedContentHandler, Logging):

    def __init__(self):
        super().__init__()
        self.__users_listeners = None
        self.__stats_listeners = None
        self.__speeds_listeners = None

    @property
    def users_listeners(self) -> List[ID]:
        listeners = self.__users_listeners
        if listeners is None:
            listeners = _get_listeners(name='users_listeners')
            self.__users_listeners = listeners
        return listeners

    @property
    def stats_listeners(self) -> List[ID]:
        listeners = self.__stats_listeners
        if listeners is None:
            listeners = _get_listeners(name='stats_listeners')
            self.__stats_listeners = listeners
        return listeners

    @property
    def speeds_listeners(self) -> List[ID]:
        listeners = self.__speeds_listeners
        if listeners is None:
            listeners = _get_listeners(name='speeds_listeners')
            self.__speeds_listeners = listeners
        return listeners

    # Override
    async def handle_action(self, content: CustomizedContent, msg: ReliableMessage,
                            messenger: Messenger) -> List[Content]:
        sender = msg.sender
        act = content.action
        if act != 'post':
            self.error('content error: %s', content)
            return await super().handle_action(content=content, msg=msg, messenger=messenger)
        mod = content.module
        if mod == 'users':
            listeners = self.users_listeners
        elif mod == 'stats':
            listeners = self.stats_listeners
        elif mod == 'speeds':
            listeners = self.speeds_listeners
            if 'U' not in content:
                # speeds stat contents are sent from client,
                # so the sender must be a user id here
                content['U'] = str(sender)
        else:
            self.error('unknown module: %s, action: %s', mod, act)
            return await super().handle_action(content=content, msg=msg, messenger=messenger)
        self.info('redirecting content "%s" to %s ...', mod, listeners)
        facebook = messenger.facebook
        assert isinstance(facebook, ClientFacebook), 'facebook error: %s' % facebook
        assert isinstance(messenger, ClientMessenger), 'messenger error: %s' % messenger
        current = await facebook.current_user
        assert current is not None, 'current user not found'
        uid = current.identifier
        assert uid not in listeners, 'should not happen: %s, %s' % (uid, listeners)
        assert sender not in listeners, 'should not happen: %s, %s' % (sender, listeners)
        if len(listeners) > 0:
            for bot in listeners:
                await messenger.send_content(sender=uid, receiver=bot, content=content)
        # respond nothing
        return []


# -----------------------------------------------------------------------------
#  Message Extensions
# -----------------------------------------------------------------------------


def register_customized_handlers():
    app_filter = get_app_filter()
    # 'chat.dim.monitor:*'
    handler = StatHandler()
    app = 'chat.dim.monitor'
    modules = ['users', 'stats', 'speeds']
    for mod in modules:
        app_filter.set_content_handler(app=app, mod=mod, handler=handler)


#
#  show logs
#
LOG_LEVEL = LogLevel.DEVELOP

BOT_NAME = 'monitor'

APP_NAME = 'ServiceBot: Monitor'

DEFAULT_CONFIG = '/etc/dim/config.ini'


async def async_main():
    #
    #  parse cmd parameters
    #
    sys_argv = SysArgvParser.parse(shortopts='hf:ld:',
                                   longopts=['help', 'config=', 'log-location', 'log-dir='])
    if sys_argv is None:
        show_help(app_name=APP_NAME, cmd=sys.argv[0], default_config=DEFAULT_CONFIG)
        sys.exit(1)
    #
    #  init logger
    #
    show_location = sys_argv.has_opt(opt='log-location')
    init_logger(name=BOT_NAME, level=LOG_LEVEL, show_location=show_location)
    #
    #  create config
    #
    config = await create_config(sys_argv=sys_argv, default_config=DEFAULT_CONFIG)
    if config is None:
        show_help(app_name=APP_NAME, cmd=sys.argv[0], default_config=DEFAULT_CONFIG)
        sys.exit(1)
    #
    #  register handlers
    #
    register_customized_handlers()
    #
    #  Create & start the bot
    #
    client = await start_bot(ans_name=BOT_NAME, processor_class=ClientMessageProcessor)
    Log.warning('bot stopped: %s', client)


def main():
    Runner.sync_run(main=async_main())


if __name__ == '__main__':
    main()
