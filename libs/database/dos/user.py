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

from typing import Optional

from dimples import ID, Content, Command
from dimples import MuteCommand, BlockCommand

from dimples.database.dos.base import template_replace
from dimples.database import UserStorage as SuperStorage


class UserStorage(SuperStorage):

    """
        Contacts Command
        ~~~~~~~~~~~~~~~~

        file path: '.dim/protected/{ADDRESS}/contacts_stored.js'
    """
    contacts_command_path = '{PROTECTED}/{ADDRESS}/contacts_stored.js'

    def show_info(self):
        super().show_info()
        path3 = self.protected_path(self.contacts_command_path)
        path4 = self.protected_path(self.block_command_path)
        path5 = self.protected_path(self.mute_command_path)
        print('!!!       contacts path: %s' % path3)
        print('!!!      block cmd path: %s' % path4)
        print('!!!       mute cmd path: %s' % path5)

    def __contacts_command_path(self, identifier: ID) -> str:
        path = self.protected_path(self.contacts_command_path)
        return template_replace(path, 'ADDRESS', str(identifier.address))

    async def save_contacts_command(self, content: Command, identifier: ID) -> bool:
        assert content is not None, 'contacts command cannot be empty'
        path = self.__contacts_command_path(identifier=identifier)
        self.info('Saving contacts command into: %s' % path)
        info = content.to_dict()
        return await self.write_json(container=info, path=path)

    async def get_contacts_command(self, identifier: ID) -> Optional[Command]:
        path = self.__contacts_command_path(identifier=identifier)
        self.info('Loading stored contacts command from: %s' % path)
        dictionary = await self.read_json(path=path)
        if dictionary is not None:
            return Content.parse(content=dictionary)  # -> StorageCommand

    """
        Block Command
        ~~~~~~~~~~~~~

        file path: '.dim/protected/{ADDRESS}/block_stored.js'
    """
    block_command_path = '{PROTECTED}/{ADDRESS}/block_stored.js'

    def __block_command_path(self, identifier: ID) -> str:
        path = self.protected_path(self.block_command_path)
        return template_replace(path, 'ADDRESS', str(identifier.address))

    async def save_block_command(self, content: BlockCommand, identifier: ID) -> bool:
        assert content is not None, 'block command cannot be empty'
        path = self.__block_command_path(identifier=identifier)
        self.info('Saving block command into: %s' % path)
        info = content.to_dict()
        return await self.write_json(container=info, path=path)

    async def get_block_command(self, identifier: ID) -> Optional[BlockCommand]:
        path = self.__block_command_path(identifier=identifier)
        self.info('Loading stored block command from: %s' % path)
        dictionary = await self.read_json(path=path)
        if dictionary is not None:
            return BlockCommand(content=dictionary)

    """
        Mute Command
        ~~~~~~~~~~~~~

        file path: '.dim/protected/{ADDRESS}/mute_stored.js'
    """
    mute_command_path = '{PROTECTED}/{ADDRESS}/mute_stored.js'

    def __mute_command_path(self, identifier: ID) -> str:
        path = self.protected_path(self.mute_command_path)
        return template_replace(path, 'ADDRESS', str(identifier.address))

    async def save_mute_command(self, content: MuteCommand, identifier: ID) -> bool:
        assert content is not None, 'mute command cannot be empty'
        path = self.__mute_command_path(identifier=identifier)
        self.info('Saving mute command into: %s' % path)
        info = content.to_dict()
        return await self.write_json(container=info, path=path)

    async def get_mute_command(self, identifier: ID) -> Optional[MuteCommand]:
        path = self.__mute_command_path(identifier=identifier)
        self.info('Loading stored mute command from: %s' % path)
        dictionary = await self.read_json(path=path)
        if dictionary is not None:
            return MuteCommand(content=dictionary)
