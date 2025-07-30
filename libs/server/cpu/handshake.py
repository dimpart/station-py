# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2024 Albert Moky
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

from typing import List

from dimples import ReliableMessage
from dimples import Content
from dimples import HandshakeCommand, BaseHandshakeCommand
from dimples.server.cpu import HandshakeCommandProcessor


class ServerHandshakeProcessor(HandshakeCommandProcessor):

    ASK_LOGIN = 'Hello world!'

    TEST_SPEED = 'Nice to meet you!'
    TEST_SPEED_RESPOND = 'Nice to meet you too!'

    # Override
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, HandshakeCommand), 'handshake command error: %s' % content
        title = content.title
        if title == self.ASK_LOGIN:
            # C -> S: Hello world!
            return await super().process_content(content=content, r_msg=r_msg)
        elif title == self.TEST_SPEED:
            # C -> S: Nice to meet you!
            messenger = self.messenger
            session = messenger.session
            res = BaseHandshakeCommand(title=self.TEST_SPEED_RESPOND)
            res['remote_address'] = session.remote_address
            return [res]
        elif title == self.TEST_SPEED_RESPOND:
            # just ignore it
            return []
        else:
            # error
            text = 'Command error.'
            return self._respond_receipt(text=text, envelope=r_msg.envelope, content=content, extra={
                'template': 'Handshake command error: title="${title}".',
                'replacements': {
                    'title': title,
                }
            })
