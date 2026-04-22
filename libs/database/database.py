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

from typing import Optional, List, Set, Tuple, Dict

from dimples import SymmetricKey, PrivateKey, SignKey, DecryptKey
from dimples import ID, Meta, Document
from dimples import ReliableMessage
from dimples import Command, LoginCommand, GroupCommand, ResetCommand
from dimples import BlockCommand, MuteCommand
from dimples import AccountDBI, MessageDBI, SessionDBI
from dimples import ProviderInfo, StationInfo
from dimples import MetaUtils
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

from .dos import DeviceInfo

# from .t_ans import AddressNameTable
from .t_document import DocumentTable
from .t_device import DeviceTable
from .t_user import UserTable
from .t_active import ActiveTable


class Database(AccountDBI, MessageDBI, SessionDBI):

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
        return await self.__private_table.save_private_key(key=key, user=user, key_type=key_type)

    # Override
    async def private_keys_for_decryption(self, user: ID) -> List[DecryptKey]:
        return await self.__private_table.private_keys_for_decryption(user=user)

    # Override
    async def private_key_for_signature(self, user: ID) -> Optional[SignKey]:
        return await self.__private_table.private_key_for_signature(user=user)

    # Override
    async def private_key_for_visa_signature(self, user: ID) -> Optional[SignKey]:
        return await self.__private_table.private_key_for_visa_signature(user=user)

    """
        Meta file for entities
        ~~~~~~~~~~~~~~~~~~~~~~

        file path: '.dim/public/{ADDRESS}/meta.js'
        redis key: 'mkm.meta.{ID}'
    """

    # noinspection PyMethodMayBeStatic
    async def _verify_meta(self, meta: Meta, identifier: ID) -> bool:
        if MetaUtils.match_id(identifier=identifier, meta=meta):
            return True
        raise ValueError('meta not match ID: %s' % identifier)

    # Override
    async def save_meta(self, meta: Meta, identifier: ID) -> bool:
        if await self._verify_meta(meta=meta, identifier=identifier):
            return await self.__meta_table.save_meta(meta=meta, identifier=identifier)

    # Override
    async def get_meta(self, identifier: ID) -> Optional[Meta]:
        return await self.__meta_table.get_meta(identifier=identifier)

    """
        Document for Accounts
        ~~~~~~~~~~~~~~~~~~~~~

        file path: '.dim/public/{ADDRESS}/profile.js'
        redis key: 'mkm.document.{ID}'
        redis key: 'mkm.docs.keys'
    """

    async def _verify_document(self, document: Document, identifier: ID) -> bool:
        # if document.is_valid:
        #     return True
        meta = await self.get_meta(identifier=identifier)
        assert meta is not None, 'meta not exists: %s' % identifier
        if document.verify(public_key=meta.public_key):
            return True
        raise ValueError('document invalid: %s' % identifier)

    # Override
    async def save_document(self, document: Document, identifier: ID) -> bool:
        if await self._verify_document(document=document, identifier=identifier):
            return await self.__document_table.save_document(document=document, identifier=identifier)

    # Override
    async def get_documents(self, identifier: ID) -> List[Document]:
        return await self.__document_table.get_documents(identifier=identifier)

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

        file path: '.dim/protected/{ADDRESS}/contacts.txt'
        redis key: 'mkm.user.{ID}.contacts'
    """

    # Override
    async def save_contacts(self, contacts: List[ID], user: ID) -> bool:
        return await self.__user_table.save_contacts(contacts=contacts, user=user)

    # Override
    async def get_contacts(self, user: ID) -> List[ID]:
        return await self.__user_table.get_contacts(user=user)

    """
        Stored Contacts for User
        ~~~~~~~~~~~~~~~~~~~~~~~~

        file path: '.dim/protected/{ADDRESS}/contacts_stored.js'
        redis key: 'mkm.user.{ID}.cmd.contacts'
    """

    async def save_contacts_command(self, content: Command, identifier: ID) -> bool:
        return await self.__user_table.save_contacts_command(content=content, identifier=identifier)

    async def get_contacts_command(self, identifier: ID) -> Optional[Command]:
        return await self.__user_table.get_contacts_command(identifier=identifier)

    """
        Block-list of User
        ~~~~~~~~~~~~~~~~~~

        file path: '.dim/protected/{ADDRESS}/block_stored.js'
        redis key: 'mkm.user.{ID}.cmd.block'
    """

    async def save_block_command(self, content: BlockCommand, identifier: ID) -> bool:
        return await self.__user_table.save_block_command(content=content, identifier=identifier)

    async def get_block_command(self, identifier: ID) -> BlockCommand:
        return await self.__user_table.get_block_command(identifier=identifier)

    async def is_blocked(self, receiver: ID, sender: ID, group: ID = None) -> bool:
        cmd = await self.get_block_command(identifier=receiver)
        if cmd is None:
            return False
        array = cmd.block_list
        if array is None:
            return False
        if group is None:
            # check for personal message
            return sender in array
        else:
            # check for group message
            return group in array

    """
        Mute-list of User
        ~~~~~~~~~~~~~~~~~

        file path: '.dim/protected/{ADDRESS}/mute_stored.js'
        redis key: 'mkm.user.{ID}.cmd.mute'
    """

    async def save_mute_command(self, content: MuteCommand, identifier: ID) -> bool:
        return await self.__user_table.save_mute_command(content=content, identifier=identifier)

    async def get_mute_command(self, identifier: ID) -> MuteCommand:
        return await self.__user_table.get_mute_command(identifier=identifier)

    async def is_muted(self, receiver: ID, sender: ID, group: ID = None) -> bool:
        cmd = await self.get_mute_command(identifier=receiver)
        if cmd is None:
            return False
        array = cmd.mute_list
        if array is None:
            return False
        if group is None:
            # check for personal message
            return sender in array
        else:
            # check for group message
            return group in array

    """
        Device Tokens for APNS
        ~~~~~~~~~~~~~~~~~~~~~~

        file path: '.dim/protected/{ADDRESS}/devices.js'
        redis key: 'dim.user.{ID}.devices'
    """

    async def get_devices(self, identifier: ID) -> Optional[List[DeviceInfo]]:
        return await self.__device_table.get_devices(identifier=identifier)

    async def save_devices(self, devices: List[DeviceInfo], identifier: ID) -> bool:
        return await self.__device_table.save_devices(devices=devices, identifier=identifier)

    async def add_device(self, device: DeviceInfo, identifier: ID) -> bool:
        return await self.__device_table.add_device(device=device, identifier=identifier)

    """
        Group members
        ~~~~~~~~~~~~~

        file path: '.dim/protected/{ADDRESS}/members.txt'
        redis key: 'mkm.group.{ID}.members'
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
    async def get_group_keys(self, group: ID, sender: ID) -> Optional[Dict[str, str]]:
        return await self.__grp_keys_table.get_group_keys(group=group, sender=sender)

    # Override
    async def save_group_keys(self, group: ID, sender: ID, keys: Dict[str, str]) -> bool:
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

        redis key: 'mkm.user.{ID}.login'
    """

    # Override
    async def get_login_command_message(self, user: ID) -> Tuple[Optional[LoginCommand], Optional[ReliableMessage]]:
        return await self.__login_table.get_login_command_message(user=user)

    # Override
    async def save_login_command_message(self, user: ID, content: LoginCommand, msg: ReliableMessage) -> bool:
        return await self.__login_table.save_login_command_message(user=user, content=content, msg=msg)

    #
    #   Active DBI
    #

    async def clear_socket_addresses(self):
        """ clear before station start """
        await self.__active_table.clear_socket_addresses()

    async def get_active_users(self) -> Set[ID]:
        return await self.__active_table.get_active_users()

    async def add_socket_address(self, identifier: ID, address: Tuple[str, int]) -> Set[Tuple[str, int]]:
        return await self.__active_table.add_socket_address(identifier=identifier, address=address)

    async def remove_socket_address(self, identifier: ID, address: Tuple[str, int]) -> Set[Tuple[str, int]]:
        return await self.__active_table.remove_socket_address(identifier=identifier, address=address)

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
