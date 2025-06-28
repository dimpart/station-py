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

from typing import List, Optional

from dimples import json_encode, json_decode, utf8_encode, utf8_decode
from dimples import ID
from dimples.database.redis import RedisCache

from ..dos.device import insert_device
from ..dos import DeviceInfo


class DeviceCache(RedisCache):

    # device info cached in Redis will be removed after 30 minutes, after that
    # it will be reloaded from local storage if it's still need.
    EXPIRES = 1800  # seconds

    @property  # Override
    def db_name(self) -> Optional[str]:
        return 'mkm'

    @property  # Override
    def tbl_name(self) -> str:
        return 'user'

    """
        Device Tokens for APNS
        ~~~~~~~~~~~~~~~~~~~~~~

        redis key: 'dim.user.{ID}.devices'
    """
    def __cache_name(self, identifier: ID) -> str:
        return '%s.%s.%s.devices' % (self.db_name, self.tbl_name, identifier)

    async def get_devices(self, identifier: ID) -> Optional[List[DeviceInfo]]:
        name = self.__cache_name(identifier=identifier)
        value = await self.get(name=name)
        if value is not None:
            js = utf8_decode(data=value)
            assert js is not None, 'failed to decode string: %s' % value
            array = json_decode(string=js)
            assert isinstance(array, List), 'devices error: %s' % value
            return DeviceInfo.convert(array=array)

    async def save_devices(self, devices: List[DeviceInfo], identifier: ID) -> bool:
        array = DeviceInfo.revert(devices=devices)
        js = json_encode(obj=array)
        value = utf8_encode(string=js)
        name = self.__cache_name(identifier=identifier)
        return await self.set(name=name, value=value, expires=self.EXPIRES)

    async def add_device(self, device: DeviceInfo, identifier: ID) -> bool:
        # get all devices info with ID
        array = await self.get_devices(identifier=identifier)
        if array is None:
            array = [device]
        else:
            array = insert_device(info=device, devices=array)
            if array is None:
                return False
        return await self.save_devices(devices=array, identifier=identifier)
