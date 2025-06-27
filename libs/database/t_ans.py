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
from typing import Optional, Union, Set, Dict

from aiou.mem import CachePool

from dimples import DateTime
from dimples import ID
from dimples.utils import Config
from dimples.database import DbTask, DataCache

from .redis import AddressNameCache
from .dos import AddressNameStorage


# noinspection PyAbstractClass
class AnsTask(DbTask):

    def __init__(self,
                 redis: AddressNameCache, storage: AddressNameStorage,
                 mutex_lock: Union[threading.Lock, threading.RLock], cache_pool: CachePool):
        super().__init__(mutex_lock=mutex_lock, cache_pool=cache_pool)
        self._redis = redis
        self._dos = storage


class AllTask(AnsTask):

    ALL_KEY = 'all_records'

    @property  # Override
    def cache_key(self) -> str:
        return self.ALL_KEY

    # Override
    async def _read_data(self) -> Optional[Dict[str, ID]]:
        return await self._dos.load_records()

    # Override
    async def _write_data(self, value: Dict[str, ID]) -> bool:
        pass


class IdTask(AnsTask):

    def __init__(self, name: str,
                 redis: AddressNameCache, storage: AddressNameStorage,
                 mutex_lock: Union[threading.Lock, threading.RLock], cache_pool: CachePool):
        super().__init__(redis=redis, storage=storage,
                         mutex_lock=mutex_lock, cache_pool=cache_pool)
        self._name = name

    @property  # Override
    def cache_key(self) -> str:
        return self._name

    # Override
    async def _read_data(self) -> Optional[ID]:
        return await self._redis.get_record(name=self._name)

    # Override
    async def _write_data(self, value: ID) -> bool:
        pass


class NameTask(AnsTask):

    def __init__(self, identifier: ID,
                 redis: AddressNameCache, storage: AddressNameStorage,
                 mutex_lock: Union[threading.Lock, threading.RLock], cache_pool: CachePool):
        super().__init__(redis=redis, storage=storage,
                         mutex_lock=mutex_lock, cache_pool=cache_pool)
        self._identifier = identifier

    @property  # Override
    def cache_key(self) -> ID:
        return self._identifier

    # Override
    async def _read_data(self) -> Optional[Set[str]]:
        return await self._redis.get_names(identifier=self._identifier)

    # Override
    async def _write_data(self, value: Set[str]) -> bool:
        pass


class AddressNameTable(DataCache):

    def __init__(self, config: Config):
        super().__init__(pool_name='ans')  # str => ID
        self._redis = AddressNameCache(config=config)
        self._dos = AddressNameStorage(config=config)

    def show_info(self):
        self._dos.show_info()

    def _new_all_task(self) -> AllTask:
        return AllTask(redis=self._redis, storage=self._dos,
                       mutex_lock=self._mutex_lock, cache_pool=self._cache_pool)

    def _new_id_task(self, name: str) -> IdTask:
        return IdTask(name=name,
                      redis=self._redis, storage=self._dos,
                      mutex_lock=self._mutex_lock, cache_pool=self._cache_pool)

    def _new_name_task(self, identifier: ID) -> NameTask:
        return NameTask(identifier=identifier,
                        redis=self._redis, storage=self._dos,
                        mutex_lock=self._mutex_lock, cache_pool=self._cache_pool)

    async def _load_records(self) -> Dict[str, ID]:
        task = self._new_all_task()
        records = await task.load()
        return {} if records is None else records

    async def save_record(self, name: str, identifier: ID) -> bool:
        now = DateTime.current_timestamp()
        with self.lock:
            #
            #  1. update memory cache
            #
            if identifier is not None:
                # remove: ID => Set[str]
                self.cache.erase(key=identifier)
            all_records = await self._load_records()
            all_records[name] = identifier
            self.cache.update(key=AllTask.ALL_KEY, value=all_records, life_span=AnsTask.MEM_CACHE_EXPIRES, now=now)
            #
            #  2. update redis server
            #
            await self._redis.save_record(name=name, identifier=identifier)
            #
            #  3. update local storage
            #
            return await self._dos.save_records(records=all_records)

    async def get_record(self, name: str) -> Optional[ID]:
        #
        #  1. get record with name
        #
        task = self._new_id_task(name=name)
        did = await task.load()
        if isinstance(did, ID):
            return did
        #
        #  2. load all records
        #
        task = self._new_all_task()
        all_records = await task.load()
        if isinstance(all_records, Dict):
            did = all_records.get(name)
        #
        #   3. update memory cache
        #
        with self.lock:
            if did is not None:
                await self._redis.save_record(name=name, identifier=did)
            self.cache.update(key=name, value=did, life_span=AnsTask.MEM_CACHE_EXPIRES)
        return did

    async def get_names(self, identifier: ID) -> Set[str]:
        #
        #  1. get names for id
        #
        task = self._new_name_task(identifier=identifier)
        names = await task.load()
        if isinstance(names, Set):
            return names
        #
        #  2. load all records
        #
        task = self._new_all_task()
        all_records = await task.load()
        if isinstance(all_records, Dict):
            names = get_names(records=all_records, identifier=identifier)
        else:
            names = set()
        #
        #   3. update memory cache
        #
        with self.lock:
            self.cache.update(key=identifier, value=names, life_span=AnsTask.MEM_CACHE_EXPIRES)
        return names


def get_names(records: Dict[str, ID], identifier: ID) -> Set[str]:
    strings = set()
    for key in records:
        if identifier == records[key]:
            strings.add(key)
    return strings
