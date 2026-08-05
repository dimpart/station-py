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
    Filter
    ~~~~~~

    Filters for delivering message
"""

from dimples import Singleton
from dimples import EntityType
from dimples import ReliableMessage

from dimples import MessageUtils

from ..database import Database


class BlockFilter:

    def __init__(self, database: Database):
        super().__init__()
        self.__database = database

    async def is_blocked(self, msg: ReliableMessage) -> bool:
        sender = MessageUtils.real_sender(msg=msg)
        receiver = MessageUtils.real_receiver(msg=msg)
        group = msg.group
        # check block-list
        db = self.__database
        return await db.is_blocked(sender=sender, receiver=receiver, group=group)


class MuteFilter:
    """ Filter for Push Notification service """

    def __init__(self, database: Database):
        super().__init__()
        self.__database = database

    # Override
    async def is_muted(self, msg: ReliableMessage) -> bool:
        if msg.get_bool(key='muted', default=False):
            return True
        sender = MessageUtils.real_sender(msg=msg)
        receiver = MessageUtils.real_receiver(msg=msg)
        group = msg.group
        if sender.type == EntityType.STATION or receiver.type == EntityType.STATION:
            # mute all messages for stations
            return True
        elif sender.type == EntityType.BOT:
            # mute group message from bot
            if receiver.is_group or group is not None or 'GF' in msg:
                return True
        elif receiver.type == EntityType.BOT:
            # mute all messages to bots
            return True
        # check block-list
        db = self.__database
        return await db.is_muted(sender=sender, receiver=receiver, group=group)


@Singleton
class FilterManager:

    def __init__(self):
        super().__init__()
        self.__block_filter = None
        self.__mute_filter = None

    @property
    def block_filter(self) -> BlockFilter:
        return self.__block_filter

    @block_filter.setter
    def block_filter(self, delegate: BlockFilter):
        self.__block_filter = delegate

    @property
    def mute_filter(self) -> MuteFilter:
        return self.__mute_filter

    @mute_filter.setter
    def mute_filter(self, delegate: MuteFilter):
        self.__mute_filter = delegate
