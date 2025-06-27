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
    Server extensions for MessageProcessor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import Optional

from dimples import ContentType
from dimples import ReportCommand
from dimples import HandshakeCommand
from dimples import MuteCommand, BlockCommand

from dimples import ContentProcessor
from dimples import ContentProcessorCreator
from dimples import BaseContentProcessor

from dimples import Facebook, Messenger

from dimples.server import ServerMessageProcessor
from dimples.server.cpu import ServerContentProcessorCreator

from .cpu import ServerHandshakeProcessor
from .cpu import ReportCommandProcessor
from .cpu import MuteCommandProcessor, BlockCommandProcessor
from .cpu import TextContentProcessor


class ServerProcessor(ServerMessageProcessor):

    # Override
    def _create_creator(self, facebook: Facebook, messenger: Messenger) -> ContentProcessorCreator:
        return ServerProcessorCreator(facebook=facebook, messenger=messenger)


class ServerProcessorCreator(ServerContentProcessorCreator):

    # Override
    def create_content_processor(self, msg_type: str) -> Optional[ContentProcessor]:
        # text
        if msg_type == ContentType.TEXT:
            return TextContentProcessor(facebook=self.facebook, messenger=self.messenger)
        # default
        if msg_type == 0:
            return BaseContentProcessor(facebook=self.facebook, messenger=self.messenger)
        # others
        return super().create_content_processor(msg_type=msg_type)

    # Override
    def create_command_processor(self, msg_type: str, cmd: str) -> Optional[ContentProcessor]:
        # handshake
        if cmd == HandshakeCommand.HANDSHAKE:
            return ServerHandshakeProcessor(facebook=self.facebook, messenger=self.messenger)
        # mute
        if cmd == MuteCommand.MUTE:
            return MuteCommandProcessor(facebook=self.facebook, messenger=self.messenger)
        # block
        if cmd == BlockCommand.BLOCK:
            return BlockCommandProcessor(facebook=self.facebook, messenger=self.messenger)
        # report
        if cmd in ['broadcast', ReportCommand.ONLINE, ReportCommand.OFFLINE]:
            return ReportCommandProcessor(facebook=self.facebook, messenger=self.messenger)
        # others
        return super().create_command_processor(msg_type=msg_type, cmd=cmd)
