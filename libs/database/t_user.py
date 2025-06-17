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

import threading
from typing import Optional, List

from aiou.mem import CachePool

from dimples import ID, Command
from dimples import BlockCommand, MuteCommand
from dimples.utils import is_before
from dimples.utils import SharedCacheManager
from dimples.database import UserDBI, ContactDBI
from dimples.utils import Config
from dimples.database import DbTask

from .redis import UserCache
from .dos import UserStorage


# noinspection PyAbstractClass
class BaseTask(DbTask):

    def __init__(self, user: ID,
                 redis: UserCache, storage: UserStorage,
                 mutex_lock: threading.Lock, cache_pool: CachePool):
        super().__init__(mutex_lock=mutex_lock, cache_pool=cache_pool)
        self._user = user
        self._redis = redis
        self._dos = storage

    @property  # Override
    def cache_key(self) -> ID:
        return self._user


class UsrTask(BaseTask):

    # Override
    async def _read_data(self) -> Optional[List[ID]]:
        # 1. get from redis server
        contacts = await self._redis.get_contacts(identifier=self._user)
        if contacts is not None:
            return contacts
        # 2. get from local storage
        contacts = await self._dos.get_contacts(user=self._user)
        if contacts is not None:
            # 3. update redis server
            await self._redis.save_contacts(contacts=contacts, identifier=self._user)
            return contacts

    # Override
    async def _write_data(self, value: List[ID]) -> bool:
        # 1. store into redis server
        ok1 = await self._redis.save_contacts(contacts=value, identifier=self._user)
        # 2. save into local storage
        ok2 = await self._dos.save_contacts(contacts=value, user=self._user)
        return ok1 or ok2


class ConTask(BaseTask):

    # Override
    async def _read_data(self) -> Optional[Command]:
        # 1. get from redis server
        cmd = await self._redis.get_contacts_command(identifier=self._user)
        if cmd is not None:
            return cmd
        # 2. get from local storage
        cmd = await self._dos.get_contacts_command(identifier=self._user)
        if cmd is not None:
            # 3. update redis server
            await self._redis.save_contacts_command(content=cmd, identifier=self._user)
            return cmd

    # Override
    async def _write_data(self, value: Command) -> bool:
        # 1. store into redis server
        ok1 = await self._redis.save_contacts_command(content=value, identifier=self._user)
        # 2. save into local storage
        ok2 = await self._dos.save_contacts_command(content=value, identifier=self._user)
        return ok1 or ok2


class BloTask(BaseTask):

    # Override
    async def _read_data(self) -> Optional[BlockCommand]:
        # 1. get from redis server
        cmd = await self._redis.get_block_command(identifier=self._user)
        if cmd is not None:
            return cmd
        # 2. get from local storage
        cmd = await self._dos.get_block_command(identifier=self._user)
        if cmd is not None:
            # 3. update redis server
            await self._redis.save_block_command(content=cmd, identifier=self._user)
            return cmd

    # Override
    async def _write_data(self, value: BlockCommand) -> bool:
        # 1. store into redis server
        ok1 = await self._redis.save_block_command(content=value, identifier=self._user)
        # 2. save into local storage
        ok2 = await self._dos.save_block_command(content=value, identifier=self._user)
        return ok1 or ok2


class MutTask(BaseTask):

    # Override
    async def _read_data(self) -> Optional[MuteCommand]:
        # 1. get from redis server
        cmd = await self._redis.get_mute_command(identifier=self._user)
        if cmd is not None:
            return cmd
        # 2. get from local storage
        cmd = await self._dos.get_mute_command(identifier=self._user)
        if cmd is not None:
            # 3. update redis server
            await self._redis.save_mute_command(content=cmd, identifier=self._user)
            return cmd

    # Override
    async def _write_data(self, value: MuteCommand) -> bool:
        # 1. store into redis server
        ok1 = await self._redis.save_mute_command(content=value, identifier=self._user)
        # 2. save into local storage
        ok2 = await self._dos.save_mute_command(content=value, identifier=self._user)
        return ok1 or ok2


class UserTable(UserDBI, ContactDBI):
    """ Implementations of UserDBI """

    def __init__(self, config: Config):
        super().__init__()
        man = SharedCacheManager()
        self._cmd_contacts = man.get_pool(name='cmd.contacts')  # ID => StorageCommand
        self._cmd_block = man.get_pool(name='cmd.block')        # ID => BlockCommand
        self._cmd_mute = man.get_pool(name='cmd.mute')          # ID => MuteCommand
        self._cache = man.get_pool(name='contacts')             # ID => List[ID]
        self._redis = UserCache(config=config)
        self._dos = UserStorage(config=config)
        self._lock = threading.Lock()

    def show_info(self):
        self._dos.show_info()

    def _new_task(self, user: ID) -> UsrTask:
        return UsrTask(user=user, cache_pool=self._cache,
                       redis=self._redis, storage=self._dos, mutex_lock=self._lock)

    def _new_con_task(self, user: ID) -> ConTask:
        return ConTask(user=user, cache_pool=self._cmd_contacts,
                       redis=self._redis, storage=self._dos, mutex_lock=self._lock)

    def _new_blo_task(self, user: ID) -> BloTask:
        return BloTask(user=user, cache_pool=self._cmd_block,
                       redis=self._redis, storage=self._dos, mutex_lock=self._lock)

    def _new_mut_task(self, user: ID) -> MutTask:
        return MutTask(user=user, cache_pool=self._cmd_mute,
                       redis=self._redis, storage=self._dos, mutex_lock=self._lock)

    #
    #   User DBI
    #

    # Override
    async def get_local_users(self) -> List[ID]:
        return []

    # Override
    async def save_local_users(self, users: List[ID]) -> bool:
        pass

    #
    #   Contact DBI
    #

    # Override
    async def get_contacts(self, user: ID) -> List[ID]:
        task = self._new_task(user=user)
        contacts = await task.load()
        return [] if contacts is None else contacts

    # Override
    async def save_contacts(self, contacts: List[ID], user: ID) -> bool:
        task = self._new_task(user=user)
        return await task.save(value=contacts)

    #
    #   Contacts
    #

    async def _is_contacts_expired(self, user: ID, content: Command) -> bool:
        """ check old record with command time """
        new_time = content.time
        if new_time is None or new_time <= 0:
            return False
        # check old record
        old, _ = await self.get_contacts_command(identifier=user)
        if old is not None and is_before(old_time=old.time, new_time=new_time):
            # command expired
            return False

    async def save_contacts_command(self, content: Command, identifier: ID) -> bool:
        # check old record with time
        if await self._is_contacts_expired(user=identifier, content=content):
            # command expired, drop it
            return False
        task = self._new_con_task(user=identifier)
        return await task.save(value=content)

    async def get_contacts_command(self, identifier: ID) -> Optional[Command]:
        task = self._new_con_task(user=identifier)
        return await task.load()

    #
    #   Block List
    #

    async def _is_blocked_expired(self, user: ID, content: BlockCommand) -> bool:
        """ check old record with command time """
        new_time = content.time
        if new_time is None or new_time <= 0:
            return False
        # check old record
        old = await self.get_block_command(identifier=user)
        if old is not None and is_before(old_time=old.time, new_time=new_time):
            # command expired
            return False

    async def save_block_command(self, content: BlockCommand, identifier: ID) -> bool:
        # check old record with time
        if await self._is_blocked_expired(user=identifier, content=content):
            # command expired, drop it
            return False
        task = self._new_blo_task(user=identifier)
        return await task.save(value=content)

    async def get_block_command(self, identifier: ID) -> Optional[BlockCommand]:
        task = self._new_blo_task(user=identifier)
        return await task.load()

    #
    #   Mute List
    #

    async def _is_muted_expired(self, user: ID, content: MuteCommand) -> bool:
        """ check old record with command time """
        new_time = content.time
        if new_time is None or new_time <= 0:
            return False
        # check old record
        old = await self.get_mute_command(identifier=user)
        if old is not None and is_before(old_time=old.time, new_time=new_time):
            # command expired
            return False

    async def save_mute_command(self, content: MuteCommand, identifier: ID) -> bool:
        # check old record with time
        if await self._is_muted_expired(user=identifier, content=content):
            # command expired, drop it
            return False
        task = self._new_mut_task(user=identifier)
        return await task.save(value=content)

    async def get_mute_command(self, identifier: ID) -> Optional[MuteCommand]:
        task = self._new_mut_task(user=identifier)
        return await task.load()
