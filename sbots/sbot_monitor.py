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

from typing import Optional, List

from dimples import ID, ReliableMessage
from dimples import ContentType, Content
from dimples import CustomizedContent
from dimples import ContentProcessor, ContentProcessorCreator
from dimples import Facebook, Messenger
from dimples.utils import Log, Logging
from dimples.utils import Runner
from dimples.utils import Path
from dimples.client import ClientMessenger
from dimples.client import ClientMessageProcessor
from dimples.client.cpu import ClientContentProcessorCreator
from dimples.client.cpu import CustomizedContentProcessor

path = Path.abs(path=__file__)
path = Path.dir(path=path)
path = Path.dir(path=path)
Path.add(path=path)

from sbots.shared import GlobalVariable
from sbots.shared import create_config, start_bot


def _get_listeners(name: str) -> List[ID]:
    shared = GlobalVariable()
    config = shared.config
    text = config.get_string(section='monitor', option=name)
    text = text.replace(' ', '')
    if len(text) == 0:
        return []
    array = text.split(',')
    return ID.convert(array=array)


class StatContentProcessor(CustomizedContentProcessor, Logging):
    """ Process customized stat content """

    def __init__(self, facebook, messenger):
        super().__init__(facebook=facebook, messenger=messenger)
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

    @property
    def messenger(self) -> ClientMessenger:
        transceiver = super().messenger
        assert isinstance(transceiver, ClientMessenger), 'messenger error: %s' % transceiver
        return transceiver

    # Override
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, CustomizedContent), 'stat content error: %s' % content
        app = content.application
        mod = content.module
        act = content.action
        sender = r_msg.sender
        self.debug(msg='received content from %s: %s, %s, %s' % (sender, app, mod, act))
        return await super().process_content(content=content, r_msg=r_msg)

    # Override
    def _filter(self, app: str, content: CustomizedContent, msg: ReliableMessage) -> Optional[List[Content]]:
        if app == 'chat.dim.monitor':
            # app ID matched
            return None
        # unknown app ID
        return super()._filter(app=app, content=content, msg=msg)

    # Override
    async def handle_action(self, act: str, sender: ID,
                            content: CustomizedContent, msg: ReliableMessage) -> List[Content]:
        if act != 'post':
            self.error(msg='content error: %s' % content)
            return []
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
            self.error(msg='unknown module: %s, action: %s' % (mod, act))
            return []
        self.info(msg='redirecting content "%s" to %s ...' % (mod, listeners))
        current = await self.messenger.facebook.current_user
        assert current is not None, 'current user not found'
        uid = current.identifier
        assert uid not in listeners, 'should not happen: %s, %s' % (uid, listeners)
        assert sender not in listeners, 'should not happen: %s, %s' % (sender, listeners)
        if len(listeners) > 0:
            messenger = self.messenger
            for bot in listeners:
                await messenger.send_content(sender=uid, receiver=bot, content=content)
        # respond nothing
        return []


class BotContentProcessorCreator(ClientContentProcessorCreator):

    # Override
    def create_content_processor(self, msg_type: str) -> Optional[ContentProcessor]:
        # application customized
        if msg_type == ContentType.CUSTOMIZED:
            return StatContentProcessor(facebook=self.facebook, messenger=self.messenger)
        # others
        return super().create_content_processor(msg_type=msg_type)


class BotMessageProcessor(ClientMessageProcessor):

    # Override
    def _create_creator(self, facebook: Facebook, messenger: Messenger) -> ContentProcessorCreator:
        return BotContentProcessorCreator(facebook=self.facebook, messenger=self.messenger)


#
# show logs
#
Log.LEVEL = Log.DEVELOP


DEFAULT_CONFIG = '/etc/dim/config.ini'


async def async_main():
    # create global variable
    shared = GlobalVariable()
    config = await create_config(app_name='ServiceBot: Monitor', default_config=DEFAULT_CONFIG)
    await shared.prepare(config=config)
    #
    #  Create & start the bot
    #
    client = await start_bot(ans_name='monitor', processor_class=BotMessageProcessor)
    Log.warning(msg='bot stopped: %s' % client)


def main():
    Runner.sync_run(main=async_main())


if __name__ == '__main__':
    main()
