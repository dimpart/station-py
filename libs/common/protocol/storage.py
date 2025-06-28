# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2019 by Moky <albert.moky@gmail.com>
#
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
    Storage Protocol
    ~~~~~~~~~~~~~~~~

    Storage data (may be encrypted) by title for VIP users
"""

from typing import Optional, Any, Dict

from dimples import base64_encode, base64_decode, json_decode, utf8_decode
from dimples import DecryptKey, SymmetricKey, ID
from dimples import BaseCommand


class StorageCommand(BaseCommand):
    """
        Storage Command
        ~~~~~~~~~~~~~~~

        data format: {
            type : 0x88,
            sn   : 123,

            command : "storage", // command name
            title   : "...",     // "contacts", "private_key", ...

            data    : "...",  // base64_encode(symmetric)
            key     : "...",  // base64_encode(asymmetric)
            //-- extra info
        }
    """

    STORAGE = 'storage'

    CONTACTS = 'contacts'
    PRIVATE_KEY = 'private_key'

    def __init__(self, content: Optional[Dict[str, Any]] = None,
                 title: Optional[str] = None):
        if content is None:
            super().__init__(cmd=StorageCommand.STORAGE)
        else:
            super().__init__(content=content)
        if title is not None:
            self['title'] = title
        # lazy
        self.__key: Optional[bytes] = None
        self.__data: Optional[bytes] = None
        self.__plaintext: object = None

    #
    #   Title
    #
    @property
    def title(self) -> str:
        string = self.get('title')
        if string is None:
            string = self.cmd
            assert string != self.STORAGE, 'storage command error: %s' % self
        return string

    #
    #   ID
    #
    @property
    def identifier(self) -> ID:
        return ID.parse(identifier=self.get('did'))

    @identifier.setter
    def identifier(self, value: ID):
        if value is None:
            self.pop('did', None)
        else:
            self['did'] = str(value)

    #
    #   Key (for decrypt data)
    #
    @property
    def key(self) -> Optional[bytes]:
        if self.__key is None:
            base64 = self.get('key')
            if base64 is not None:
                self.__key = base64_decode(base64)
        return self.__key

    @key.setter
    def key(self, value: bytes):
        if value is None:
            self.pop('key', None)
        else:
            self['key'] = base64_encode(value)
        self.__key = value

    #
    #   Data (encrypted)
    #
    @property
    def data(self) -> Optional[bytes]:
        if self.__data is None:
            base64 = self.get('data')
            if base64 is not None:
                self.__data = base64_decode(base64)
        return self.__data

    @data.setter
    def data(self, value: bytes):
        if value is None:
            self.pop('data', None)
        else:
            self['data'] = base64_encode(value)
        self.__data = value

    def decrypt(self, password: DecryptKey = None, private_key: DecryptKey = None) -> bytes:
        """
        Decrypt data
            1. decrypt key with private key (such as RSA) to a password
            2. decrypt data with password (symmetric key, such as AES, DES, ...)

        :param password:    symmetric key
        :param private_key: asymmetric private key
        :return: plaintext
        """
        if self.__plaintext is None:
            # get symmetric key
            key = None
            if password is not None:
                assert isinstance(password, SymmetricKey), 'password error: %s' % password
                key = password
            elif private_key is not None:
                # assert isinstance(private_key, PrivateKey), 'private key error: %s' % private_key
                key_data = private_key.decrypt(self.key, params={})
                js = utf8_decode(data=key_data)
                key = SymmetricKey.parse(key=json_decode(string=js))
            # get encrypted data
            data = self.data
            if key is not None and data is not None:
                self.__plaintext = key.decrypt(data=data, params={})
        return self.__plaintext
