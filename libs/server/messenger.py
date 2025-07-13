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
    Messenger for request handler in station
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Transform and send message
"""

from typing import Optional, List

from dimples import Singleton
from dimples import DateTime
from dimples import EntityType
from dimples import ReliableMessage
from dimples import ReceiptCommand

from dimples.common import Session
from dimples.common import CommonFacebook
from dimples.common import MessageDBI

from dimples.server import ServerMessenger as SuperMessenger

from ..utils.mtp import MTPUtils
from ..database import Database

from .monitor import Monitor


class ServerMessenger(SuperMessenger):

    MTP_JSON = 0x01
    MTP_DMTP = 0x02

    def __init__(self, session: Session, facebook: CommonFacebook, database: MessageDBI):
        super().__init__(session=session, facebook=facebook, database=database)
        # Message Transfer Protocol
        self.mtp_format = self.MTP_JSON

    # Override
    async def serialize_message(self, msg: ReliableMessage) -> bytes:
        if self.mtp_format == self.MTP_JSON:
            # JsON
            return await super().serialize_message(msg=msg)
        else:
            # D-MTP
            return MTPUtils.serialize_message(msg=msg)

    # Override
    async def deserialize_message(self, data: bytes) -> Optional[ReliableMessage]:
        if data is None or len(data) < 2:
            return None
        if data.startswith(b'{'):
            # JsON
            msg = await super().deserialize_message(data=data)
        else:
            # D-MTP
            msg = MTPUtils.deserialize_message(data=data)
            if msg is not None:
                # FIXME: just change it when first package received
                self.mtp_format = self.MTP_DMTP
        return msg

    # Override
    async def handshake_success(self):
        # monitor
        session = self.session
        monitor = Monitor()
        monitor.user_online(sender=session.identifier, remote_address=session.remote_address, when=DateTime.now())
        # process suspended messages
        await super().handshake_success()

    # Override
    async def process_reliable_message(self, msg: ReliableMessage) -> List[ReliableMessage]:
        if await self._is_blocked(msg=msg):
            sender = msg.sender
            receiver = msg.receiver
            group = msg.group
            self.warning(msg='user is blocked: %s -> %s (group: %s)' % (sender, receiver, group))
            facebook = self.facebook
            nickname = await facebook.get_name(identifier=receiver)
            if group is None:
                text = 'Message is blocked by "%s"' % nickname
            else:
                grp_name = await facebook.get_name(identifier=group)
                text = 'Message is blocked by "%s" in group "%s"' % (nickname, grp_name)
            # response
            res = ReceiptCommand.create(text=text, envelope=msg.envelope)
            res.group = group
            await self.send_content(sender=None, receiver=sender, content=res, priority=1)
            return []
        monitor = Monitor()
        monitor.message_received(msg=msg)
        return await super().process_reliable_message(msg=msg)

    async def _is_blocked(self, msg: ReliableMessage) -> bool:
        block_filter = FilterManager().block_filter
        if block_filter is None:
            self.warning(msg='block filter not set')
        else:
            return await block_filter.is_blocked(msg=msg)


"""
    Filter
    ~~~~~~

    Filters for delivering message
"""


class BlockFilter:

    def __init__(self, database: Database):
        super().__init__()
        self.__database = database

    async def is_blocked(self, msg: ReliableMessage) -> bool:
        sender = msg.sender
        receiver = msg.receiver
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
        sender = msg.sender
        receiver = msg.receiver
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
