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
    Command Processor for 'report'
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Report protocol
"""

from typing import List, Dict

from dimples import ReliableMessage
from dimples import Content, ReportCommand
from dimples import BaseCommandProcessor

from ...utils import Logging

from ...database import DeviceInfo
from ...database import Database
from ...common import CommonFacebook


class ReportCommandProcessor(BaseCommandProcessor, Logging):

    @property
    def facebook(self) -> CommonFacebook:
        barrack = super().facebook
        assert isinstance(barrack, CommonFacebook), 'facebook error: %s' % barrack
        return barrack

    @property
    def database(self) -> Database:
        db = self.facebook.barrack.database
        assert isinstance(db, Database), 'database error: %s' % db
        return db

    # Override
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, ReportCommand), 'report command error: %s' % content
        # report title
        title = content.title
        if title == 'apns':
            return await self.__process_apns(content=content, msg=r_msg)
        if title == 'c2dm':
            return await self.__process_apns(content=content, msg=r_msg)
        # other reports
        return await super().process_content(content=content, r_msg=r_msg)

    async def __process_apns(self, content: ReportCommand, msg: ReliableMessage) -> List[Content]:
        # submit device token for APNs
        info = content.dictionary
        token = info.get('device_token')
        if token is None:
            token = info.get('token')
            if token is None:
                # token not found, try to get device
                info = info.get('device')
                if isinstance(info, Dict):
                    # device info found
                    token = info.get('token')
                else:
                    self.error(msg='device info not found: %s' % self)
                    return []
        if token is None or len(token) == 0:
            return []
        sender = msg.sender
        device = DeviceInfo.from_json(info=info)
        assert device is not None, 'failed to parse device info: %s' % info
        db = self.database
        await db.add_device(device=device, identifier=sender)
        text = 'Device token received.'
        return self._respond_receipt(text=text, content=content, envelope=msg.envelope, extra={
            'template': 'Device token received: ${ID}.',
            'replacements': {
                'ID': str(sender),
            }
        })
