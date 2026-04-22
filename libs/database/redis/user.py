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

from typing import Optional

from dimples import utf8_encode, utf8_decode, json_encode, json_decode
from dimples import ID, Content, Command
from dimples import MuteCommand, BlockCommand

from dimples.database.redis import UserCache as SuperCache


class UserCache(SuperCache):

    """
        Contacts Command
        ~~~~~~~~~~~~~~~~

        redis key: 'mkm.user.{ID}.cmd.contacts'
    """
    def __contacts_command_cache_name(self, identifier: ID) -> str:
        return '%s.%s.%s.cmd.contacts' % (self.db_name, self.tbl_name, identifier)

    async def save_contacts_command(self, content: Command, identifier: ID) -> bool:
        key = self.__contacts_command_cache_name(identifier=identifier)
        return await self.__save_command(key=key, content=content)

    async def get_contacts_command(self, identifier: ID) -> Optional[Command]:
        key = self.__contacts_command_cache_name(identifier=identifier)
        dictionary = await self.__load_command(key=key)
        if dictionary is not None:
            return Content.parse(content=dictionary)  # -> StorageCommand

    async def __save_command(self, key: str, content: Command) -> bool:
        dictionary = content.to_dict()
        js = json_encode(container=dictionary)
        value = utf8_encode(string=js)
        return await self.set(name=key, value=value, expires=self.EXPIRES)

    async def __load_command(self, key: str) -> Optional[dict]:
        value = await self.get(name=key)
        if value is None:
            return None
        js = utf8_decode(data=value)
        dictionary = json_decode(string=js)
        assert dictionary is not None, 'cmd error: %s' % value
        return dictionary

    """
        Block Command
        ~~~~~~~~~~~~~

        redis key: 'mkm.user.{ID}.cmd.block'
    """
    def __block_command_cache_name(self, identifier: ID) -> str:
        return '%s.%s.%s.cmd.block' % (self.db_name, self.tbl_name, identifier)

    async def save_block_command(self, content: BlockCommand, identifier: ID) -> bool:
        key = self.__block_command_cache_name(identifier=identifier)
        return await self.__save_command(key=key, content=content)

    async def get_block_command(self, identifier: ID) -> Optional[BlockCommand]:
        key = self.__block_command_cache_name(identifier=identifier)
        dictionary = await self.__load_command(key=key)
        if dictionary is not None:
            return BlockCommand(content=dictionary)

    """
        Mute Command
        ~~~~~~~~~~~~~

        redis key: 'mkm.user.{ID}.cmd.mute'
    """
    def __mute_command_cache_name(self, identifier: ID) -> str:
        return '%s.%s.%s.cmd.mute' % (self.db_name, self.tbl_name, identifier)

    async def save_mute_command(self, content: MuteCommand, identifier: ID) -> bool:
        key = self.__mute_command_cache_name(identifier=identifier)
        return await self.__save_command(key=key, content=content)

    async def get_mute_command(self, identifier: ID) -> Optional[MuteCommand]:
        key = self.__mute_command_cache_name(identifier=identifier)
        dictionary = await self.__load_command(key=key)
        if dictionary is not None:
            return MuteCommand(content=dictionary)
