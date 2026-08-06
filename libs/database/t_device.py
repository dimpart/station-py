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

from dimples import ID
from dimples.utils import Config
from dimples.database import DbTask, DataCache

from .redis import DeviceCache
from .dos import DeviceStorage, DeviceInfo
from .dos.device import insert_device


class DevTask(DbTask[ID, List[DeviceInfo]]):

    def __init__(self, user: ID,
                 redis: DeviceCache, storage: DeviceStorage,
                 mutex_lock: threading.Lock, cache_pool: CachePool):
        super().__init__(mutex_lock=mutex_lock, cache_pool=cache_pool)
        self._identifier = user
        self._redis = redis
        self._dos = storage

    @property  # Override
    def cache_key(self) -> ID:
        return self._identifier

    # Override
    async def _read_data(self) -> Optional[List[DeviceInfo]]:
        user = self._identifier
        # 1. the redis server will return None when cache not found
        # 2. when redis server return an empty array, no need to check local storage again
        devices = await self._redis.get_devices(user=user)
        if devices is not None:
            return devices
        # 3. try to load from local storage
        devices = await self._dos.get_devices(user=user)
        if devices is not None:
            # 4. create an empty array as a placeholder for the memory cache
            devices = []
        # 5. update redis server
        await self._redis.save_devices(devices=devices, user=user)
        return devices

    # Override
    async def _write_data(self, value: List[DeviceInfo]) -> bool:
        user = self._identifier
        # 1. store into redis server
        ok1 = await self._redis.save_devices(devices=value, user=user)
        # 2. save into local storage
        ok2 = await self._dos.save_devices(devices=value, user=user)
        return ok1 or ok2


class DeviceTable(DataCache):

    def __init__(self, config: Config):
        super().__init__(pool_name='devices')  # ID => DeviceInfo
        self._redis = DeviceCache(config=config)
        self._dos = DeviceStorage(config=config)

    def show_info(self):
        self._dos.show_info()

    def _new_task(self, user: ID) -> DevTask:
        assert user.terminal is None, f'not a naked id: {user}'
        return DevTask(user=user,
                       redis=self._redis, storage=self._dos,
                       mutex_lock=self._mutex_lock, cache_pool=self._cache_pool)

    async def get_devices(self, user: ID) -> Optional[List[DeviceInfo]]:
        task = self._new_task(user=user)
        return await task.load()

    async def save_devices(self, devices: List[DeviceInfo], user: ID) -> bool:
        task = self._new_task(user=user)
        return await task.save(value=devices)

    async def add_device(self, device: DeviceInfo, user: ID) -> bool:
        # get all devices info with ID
        array = await self.get_devices(user=user)
        if array is None:
            array = [device]
        else:
            array = insert_device(info=device, devices=array)
            if array is None:
                return False
        return await self.save_devices(devices=array, user=user)
