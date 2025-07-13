# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2021 Albert Moky
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
    Common extensions for MessagePacker
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from typing import Optional

from dimples import ReliableMessage

from dimples.common import Session
from dimples.common import CommonFacebook
from dimples.common import MessageDBI

# from dimples.client.packer import attach_key_digest
from dimples.client import ClientMessenger as SuperMessenger

from ..utils.mtp import MTPUtils


class ClientMessenger(SuperMessenger):

    MTP_JSON = 0x01
    MTP_DMTP = 0x02

    def __init__(self, session: Session, facebook: CommonFacebook, database: MessageDBI):
        super().__init__(session=session, facebook=facebook, database=database)
        # Message Transfer Protocol
        self.mtp_format = self.MTP_JSON

    # Override
    async def serialize_message(self, msg: ReliableMessage) -> bytes:
        # attach_key_digest(msg=msg, messenger=self.messenger)
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
