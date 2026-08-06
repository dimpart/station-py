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
    Database module
    ~~~~~~~~~~~~~~~

"""

from typing import Optional, List, Set, Tuple

from dimples import SymmetricKey, PrivateKey, SignKey, DecryptKey
from dimples import ID, Meta, Document, Visa
from dimples import ReliableMessage
from dimples import Command, LoginCommand, GroupCommand, ResetCommand
from dimples import BlockCommand, MuteCommand
from dimples import AccountDBI, MessageDBI, SessionDBI
from dimples import ProviderInfo, StationInfo
from dimples import IDUtils, MetaUtils, DocumentUtils
from dimples import CommandMessageUtils
from dimples.utils import Config
from dimples.database import PrivateKeyTable
from dimples.database import CipherKeyTable
from dimples.database import MetaTable
from dimples.database import LoginTable
from dimples.database import GroupTable
from dimples.database import GroupHistoryTable
from dimples.database import GroupKeysTable
from dimples.database import ReliableMessageTable
from dimples.database import StationTable

from ..utils import Logging
from ..utils import StringPairing

from .dos import DeviceInfo

# from .t_ans import AddressNameTable
from .t_document import DocumentTable
from .t_device import DeviceTable
from .t_user import UserTable
from .t_active import ActiveTable


class Database(Logging, AccountDBI, MessageDBI, SessionDBI):

    def __init__(self, config: Config):
        super().__init__()
        # Entity
        self.__private_table = PrivateKeyTable(config=config)
        self.__meta_table = MetaTable(config=config)
        self.__document_table = DocumentTable(config=config)
        self.__device_table = DeviceTable(config=config)
        self.__user_table = UserTable(config=config)
        self.__group_table = GroupTable(config=config)
        self.__history_table = GroupHistoryTable(config=config)
        # Message
        self.__grp_keys_table = GroupKeysTable(config=config)
        self.__cipherkey_table = CipherKeyTable(config=config)
        self.__message_table = ReliableMessageTable(config=config)
        # # ANS
        # self.__ans_table = AddressNameTable(info=info)
        # Login info
        self.__login_table = LoginTable(config=config)
        self.__active_table = ActiveTable(config=config)
        # ISP
        self.__station_table = StationTable(config=config)

    def show_info(self):
        # Entity
        self.__private_table.show_info()
        self.__meta_table.show_info()
        self.__document_table.show_info()
        self.__device_table.show_info()
        self.__user_table.show_info()
        self.__group_table.show_info()
        self.__history_table.show_info()
        # Message
        self.__grp_keys_table.show_info()
        self.__cipherkey_table.show_info()
        self.__message_table.show_info()
        # # ANS
        # self.__ans_table.show_info()
        # Login info
        self.__login_table.show_info()
        self.__active_table.show_info()
        # ISP
        self.__station_table.show_info()

    """
        Private Key file for Users
        ~~~~~~~~~~~~~~~~~~~~~~~~~~

        file path: '.dim/private/{ADDRESS}/secret.js'
        file path: '.dim/private/{ADDRESS}/secret_keys.js'
    """

    # Override
    async def save_private_key(self, key: PrivateKey, user: ID, key_type: str = 'M') -> bool:
        user = user.without_terminal()  # Naked ID
        return await self.__private_table.save_private_key(key=key, user=user, key_type=key_type)

    # Override
    async def private_keys_for_decryption(self, user: ID) -> List[DecryptKey]:
        user = user.without_terminal()  # Naked ID
        return await self.__private_table.private_keys_for_decryption(user=user)

    # Override
    async def private_key_for_signature(self, user: ID) -> Optional[SignKey]:
        user = user.without_terminal()  # Naked ID
        return await self.__private_table.private_key_for_signature(user=user)

    # Override
    async def private_key_for_visa_signature(self, user: ID) -> Optional[SignKey]:
        user = user.without_terminal()  # Naked ID
        return await self.__private_table.private_key_for_visa_signature(user=user)

    """
        Meta file for entities
        ~~~~~~~~~~~~~~~~~~~~~~

        file path: '.dim/public/{ADDRESS}/meta.js'
        redis key: 'mkm.meta.{ADDRESS}'
    """

    async def _verify_meta(self, meta: Meta, identifier: ID) -> bool:
        if MetaUtils.match_id(identifier=identifier, meta=meta):
            return True
        else:
            self.error('meta not match: %s => %s', identifier, meta)
            return False

    # Override
    async def save_meta(self, meta: Meta, identifier: ID) -> bool:
        identifier = identifier.without_terminal()  # Naked ID
        # check meta with ID
        if await self._verify_meta(meta=meta, identifier=identifier):
            # OK, save it
            return await self.__meta_table.save_meta(meta=meta, identifier=identifier)

    # Override
    async def get_meta(self, identifier: ID) -> Optional[Meta]:
        identifier = identifier.without_terminal()  # Naked ID
        return await self.__meta_table.get_meta(identifier=identifier)

    """
        Document for Accounts
        ~~~~~~~~~~~~~~~~~~~~~

        file path: '.dim/public/{ADDRESS}/profile.js'
        file path: '.dim/public/{ADDRESS}/document.js'
        file path: '.dim/public/{ADDRESS}/documents.js'
        redis key: 'mkm.documents.{ADDRESS}'
        redis key: 'mkm.docs.keys'
    """

    async def _verify_document(self, document: Document, identifier: ID) -> bool:
        # if document.is_valid:
        #     return True
        meta = await self.get_meta(identifier=identifier)
        assert meta is not None, f'meta not exists: {identifier}'
        if document.verify(public_key=meta.public_key):
            return True
        else:
            self.error('document error: %s => %s', identifier, document)
            return False

    # Override
    async def save_document(self, document: Document, identifier: ID) -> bool:
        # check did
        did = DocumentUtils.get_document_id(document=document)
        if did is None:
            self.warning('set id for document: %s, %s', identifier, document)
            document['did'] = str(identifier)
        elif not did.is_same_as(other=identifier):
            self.error('document id not match: %s, %s', identifier, document)
            return False
        # check terminal
        terminal = identifier.terminal
        if terminal is not None:
            identifier = identifier.without_terminal()  # Naked ID
            # check terminal in visa document
            if isinstance(document, Visa):
                # old = DocumentUtils.get_visa_terminal(document=document)
                old = document.get('terminal')
                if old is None or old == '':
                    document['terminal'] = terminal
        # elif isinstance(document, Bulletin):
        #     # check founder of group in bulletin document
        #     founder = document.founder
        #     if founder is not None:
        #         g_meta = await self.get_meta(identifier=identifier)
        #         f_meta = await self.get_meta(identifier=founder)
        #         if g_meta is None or f_meta is None or g_meta.public_key != f_meta.public_key:
        #             raise ValueError(f'founder error: {founder}, group: {identifier}')
        # check document with meta.key
        if await self._verify_document(document=document, identifier=identifier):
            # OK, save it
            return await self.__document_table.save_document(document=document, identifier=identifier)

    # Override
    async def get_documents(self, identifier: ID) -> List[Document]:
        terminal = identifier.terminal
        if terminal is not None:
            identifier = identifier.without_terminal()  # Naked ID
        # load
        documents = await self.__document_table.get_documents(identifier=identifier)
        if terminal is not None:
            # filter for terminal
            array = []
            for doc in documents:
                if isinstance(doc, Visa) and DocumentUtils.get_visa_terminal(document=doc) != terminal:
                    self.info('skip document: %s "%s", %s', identifier, terminal, doc)
                    continue
                # terminal matched
                array.append(doc)
            documents = array
        return documents

    async def scan_documents(self) -> List[Document]:
        return await self.__document_table.scan_documents()

    #
    #   User DBI
    #

    # Override
    async def get_local_users(self) -> List[ID]:
        return await self.__user_table.get_local_users()

    # Override
    async def save_local_users(self, users: List[ID]) -> bool:
        return await self.__user_table.save_local_users(users=users)

    """
        User contacts
        ~~~~~~~~~~~~~

        file path: '.dim/private/{ADDRESS}/contacts.js'
        redis key: 'mkm.user.{ADDRESS}.contacts'
    """

    # Override
    async def save_contacts(self, contacts: List[ID], user: ID) -> bool:
        user = user.without_terminal()  # Naked ID
        return await self.__user_table.save_contacts(contacts=contacts, user=user)

    # Override
    async def get_contacts(self, user: ID) -> List[ID]:
        user = user.without_terminal()  # Naked ID
        return await self.__user_table.get_contacts(user=user)

    """
        Stored Contacts for User
        ~~~~~~~~~~~~~~~~~~~~~~~~

        file path: '.dim/protected/{ADDRESS}/contacts_stored.js'
        redis key: 'mkm.user.{ADDRESS}.cmd.contacts'
    """

    async def save_contacts_command(self, content: Command, user: ID) -> bool:
        user = user.without_terminal()  # Naked ID
        return await self.__user_table.save_contacts_command(content=content, user=user)

    async def get_contacts_command(self, user: ID) -> Optional[Command]:
        user = user.without_terminal()  # Naked ID
        return await self.__user_table.get_contacts_command(user=user)

    """
        Block-list of User
        ~~~~~~~~~~~~~~~~~~

        file path: '.dim/protected/{ADDRESS}/block_stored.js'
        redis key: 'mkm.user.{ADDRESS}.cmd.block'
    """

    async def save_block_command(self, content: BlockCommand, user: ID) -> bool:
        user = user.without_terminal()  # Naked ID
        return await self.__user_table.save_block_command(content=content, user=user)

    async def get_block_command(self, user: ID) -> BlockCommand:
        user = user.without_terminal()  # Naked ID
        return await self.__user_table.get_block_command(user=user)

    async def is_blocked(self, receiver: ID, sender: ID, group: ID = None) -> bool:
        cmd = await self.get_block_command(user=receiver)
        if cmd is None:
            return False
        array = cmd.block_list
        if array is None:
            return False
        if group is None:
            # check for personal message
            return IDUtils.contains(sender, array)
        else:
            # check for group message
            return group in array

    """
        Mute-list of User
        ~~~~~~~~~~~~~~~~~

        file path: '.dim/protected/{ADDRESS}/mute_stored.js'
        redis key: 'mkm.user.{ADDRESS}.cmd.mute'
    """

    async def save_mute_command(self, content: MuteCommand, user: ID) -> bool:
        user = user.without_terminal()  # Naked ID
        return await self.__user_table.save_mute_command(content=content, user=user)

    async def get_mute_command(self, user: ID) -> MuteCommand:
        user = user.without_terminal()  # Naked ID
        return await self.__user_table.get_mute_command(user=user)

    async def is_muted(self, receiver: ID, sender: ID, group: ID = None) -> bool:
        cmd = await self.get_mute_command(user=receiver)
        if cmd is None:
            return False
        array = cmd.mute_list
        if array is None:
            return False
        if group is None:
            # check for personal message
            return IDUtils.contains(sender, array)
        else:
            # check for group message
            return group in array

    """
        Device Tokens for APNS
        ~~~~~~~~~~~~~~~~~~~~~~

        file path: '.dim/protected/{ADDRESS}/devices.js'
        redis key: 'dim.user.{ADDRESS}.devices'
    """

    async def get_devices(self, user: ID) -> Optional[List[DeviceInfo]]:
        terminal = user.terminal
        if terminal is not None:
            user = user.without_terminal()  # Naked ID
        # load
        devices = await self.__device_table.get_devices(user=user)
        if terminal is not None:
            # filter for terminal
            array = []
            for info in devices:
                if info.terminal != terminal:
                    self.info('skip device: %s "%s", %s', user, terminal, info)
                    continue
                # terminal matched
                array.append(info)
            devices = array
        return devices

    # async def save_devices(self, devices: List[DeviceInfo], user: ID) -> bool:
    #     user = user.without_terminal()  # Naked ID
    #     return await self.__device_table.save_devices(devices=devices, user=user)

    async def add_device(self, device: DeviceInfo, user: ID) -> bool:
        if 'did' not in device:
            device['did'] = str(user)
        user = user.without_terminal()  # Naked ID
        return await self.__device_table.add_device(device=device, user=user)

    """
        Group members
        ~~~~~~~~~~~~~

        file path: '.dim/protected/{ADDRESS}/members.js'
        file path: '.dim/protected/{ADDRESS}/administrators.js'
        redis key: 'mkm.group.{ADDRESS}.members'
        redis key: 'mkm.group.{ADDRESS}.administrators'
    """

    # Override
    async def get_founder(self, group: ID) -> Optional[ID]:
        return await self.__group_table.get_founder(group=group)

    # Override
    async def get_owner(self, group: ID) -> Optional[ID]:
        return await self.__group_table.get_owner(group=group)

    # Override
    async def get_members(self, group: ID) -> List[ID]:
        return await self.__group_table.get_members(group=group)

    # Override
    async def save_members(self, members: List[ID], group: ID) -> bool:
        return await self.__group_table.save_members(members=members, group=group)

    # Override
    async def get_administrators(self, group: ID) -> List[ID]:
        return await self.__group_table.get_administrators(group=group)

    # Override
    async def save_administrators(self, administrators: List[ID], group: ID) -> bool:
        return await self.__group_table.save_administrators(administrators=administrators, group=group)

    #
    #   Group History DBI
    #

    # Override
    async def save_group_history(self, group: ID, content: GroupCommand, message: ReliableMessage) -> bool:
        return await self.__history_table.save_group_history(group=group, content=content, message=message)

    # Override
    async def get_group_histories(self, group: ID) -> List[Tuple[GroupCommand, ReliableMessage]]:
        return await self.__history_table.get_group_histories(group=group)

    # Override
    async def get_reset_command_message(self, group: ID) -> Tuple[Optional[ResetCommand], Optional[ReliableMessage]]:
        return await self.__history_table.get_reset_command_message(group=group)

    # Override
    async def clear_group_member_histories(self, group: ID) -> bool:
        return await self.__history_table.clear_group_member_histories(group=group)

    # Override
    async def clear_group_admin_histories(self, group: ID) -> bool:
        return await self.__history_table.clear_group_admin_histories(group=group)

    """
        Reliable message for Receivers
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        redis key: 'dkd.msg.{ID}.{sig}'
        redis key: 'dkd.msg.{ID}.messages'
    """

    # Override
    async def get_reliable_messages(self, receiver: ID, limit: int = 1024) -> List[ReliableMessage]:
        return await self.__message_table.get_reliable_messages(receiver=receiver, limit=limit)

    # Override
    async def cache_reliable_message(self, msg: ReliableMessage, receiver: ID) -> bool:
        return await self.__message_table.cache_reliable_message(msg=msg, receiver=receiver)

    # Override
    async def remove_reliable_message(self, msg: ReliableMessage, receiver: ID) -> bool:
        return await self.__message_table.remove_reliable_message(msg=msg, receiver=receiver)

    """
        Message Keys
        ~~~~~~~~~~~~

        redis key: 'dkd.key.{sender}'
    """

    # Override
    async def get_cipher_key(self, sender: ID, receiver: ID, generate: bool = False) -> Optional[SymmetricKey]:
        return await self.__cipherkey_table.get_cipher_key(sender=sender, receiver=receiver, generate=generate)

    # Override
    async def cache_cipher_key(self, key: SymmetricKey, sender: ID, receiver: ID):
        return await self.__cipherkey_table.cache_cipher_key(key=key, sender=sender, receiver=receiver)

    # Override
    async def get_group_keys(self, group: ID, sender: ID) -> Optional[StringPairing]:
        return await self.__grp_keys_table.get_group_keys(group=group, sender=sender)

    # Override
    async def save_group_keys(self, group: ID, sender: ID, keys: StringPairing) -> bool:
        return await self.__grp_keys_table.save_group_keys(group=group, sender=sender, keys=keys)

    # """
    #     Address Name Service
    #     ~~~~~~~~~~~~~~~~~~~~
    #
    #     file path: '.dim/ans.txt'
    #     redis key: 'dim.ans'
    # """
    #
    # async def ans_save_record(self, name: str, identifier: ID) -> bool:
    #     return await self.__ans_table.save_record(name=name, identifier=identifier)
    #
    # async def ans_record(self, name: str) -> ID:
    #     return await self.__ans_table.get_record(name=name)
    #
    # async def ans_names(self, identifier: ID) -> Set[str]:
    #     return await self.__ans_table.get_names(identifier=identifier)

    """
        Login Info
        ~~~~~~~~~~

        file path: '.dim/public/{ADDRESS}/login_commands.js'
        redis key: 'mkm.user.{ADDRESS}.login_commands'
    """

    # Override
    async def get_login_command_messages(self, user: ID) -> List[Tuple[LoginCommand, ReliableMessage]]:
        terminal = user.terminal
        if terminal is not None:
            user = user.without_terminal()  # Naked ID
        # load
        records = await self.__login_table.get_login_command_messages(user=user)
        if terminal is not None:
            # filter for terminal
            array = []
            for pair in records:
                cmd = pair[0]
                if CommandMessageUtils.get_login_terminal(content=cmd) != terminal:
                    self.info('skip login record: %s "%s", %s', user, terminal, cmd)
                    continue
                # terminal matched
                array.append(pair)
            records = array
        return records

    # Override
    async def save_login_command_message(self, user: ID, content: LoginCommand, msg: ReliableMessage) -> bool:
        terminal = user.terminal
        if terminal is not None:
            user = user.without_terminal()  # Naked ID
            # old = CommandMessageUtils.get_login_terminal(content=new_cmd)
            old = content.get('terminal')
            if old is None or old == '':
                content['terminal'] = terminal
        # save
        return await self.__login_table.save_login_command_message(user=user, content=content, msg=msg)

    #
    #   Active DBI
    #

    async def clear_socket_addresses(self):
        """ clear before station start """
        await self.__active_table.clear_socket_addresses()

    async def get_active_users(self) -> Set[ID]:
        return await self.__active_table.get_active_users()

    async def add_socket_address(self, user: ID, address: Tuple[str, int]) -> Set[Tuple[str, int]]:
        return await self.__active_table.add_socket_address(user=user, address=address)

    async def remove_socket_address(self, user: ID, address: Tuple[str, int]) -> Set[Tuple[str, int]]:
        return await self.__active_table.remove_socket_address(user=user, address=address)

    #
    #   Provider DBI
    #

    # Override
    async def all_providers(self) -> List[ProviderInfo]:
        """ get list of (SP_ID, chosen) """
        return await self.__station_table.all_providers()

    # Override
    async def add_provider(self, identifier: ID, chosen: int = 0) -> bool:
        return await self.__station_table.add_provider(identifier=identifier, chosen=chosen)

    # Override
    async def update_provider(self, identifier: ID, chosen: int) -> bool:
        return await self.__station_table.update_provider(identifier=identifier, chosen=chosen)

    # Override
    async def remove_provider(self, identifier: ID) -> bool:
        return await self.__station_table.remove_provider(identifier=identifier)

    # Override
    async def all_stations(self, provider: ID) -> List[StationInfo]:
        """ get list of (host, port, SP_ID, chosen) """
        return await self.__station_table.all_stations(provider=provider)

    # Override
    async def add_station(self, identifier: Optional[ID], host: str, port: int, provider: ID,
                          chosen: int = 0) -> bool:
        return await self.__station_table.add_station(identifier=identifier, host=host, port=port,
                                                      provider=provider, chosen=chosen)

    # Override
    async def update_station(self, identifier: Optional[ID], host: str, port: int, provider: ID,
                             chosen: int = None) -> bool:
        return await self.__station_table.update_station(identifier=identifier, host=host, port=port,
                                                         provider=provider, chosen=chosen)

    # Override
    async def remove_station(self, host: str, port: int, provider: ID) -> bool:
        return await self.__station_table.remove_station(host=host, port=port, provider=provider)

    # Override
    async def remove_stations(self, provider: ID) -> bool:
        return await self.__station_table.remove_stations(provider=provider)
