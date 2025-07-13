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

from dimples.client import ClientMessagePacker as SuperPacker

from .messenger import ClientMessenger


class ClientPacker(SuperPacker):

    @property
    def messenger(self) -> ClientMessenger:
        transceiver = super().messenger
        assert isinstance(transceiver, ClientMessenger), 'messenger error: %s' % transceiver
        return transceiver

    # # Override
    # def encrypt_message(self, msg: InstantMessage) -> Optional[SecureMessage]:
    #     # make sure visa.key exists before encrypting message
    #     # call super to encrypt message
    #     s_msg = super().encrypt_message(msg=msg)
    #     receiver = msg.receiver
    #     if receiver.is_group:
    #         # reuse group message keys
    #         key = self.messenger.get_cipher_key(sender=msg.sender, receiver=receiver)
    #         key['reused'] = True
    #     # TODO: reuse personal message key?
    #     return s_msg
