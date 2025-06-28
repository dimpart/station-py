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

from typing import Optional, Any, List, Dict

from dimples import Converter
from dimples import DateTime
from dimples import ID
from dimples.utils import is_before
from dimples.database.dos.base import template_replace
from dimples.database.dos import Storage


class DeviceInfo:

    def __init__(self, info: Dict[str, Any]):
        super().__init__()
        self.__info = info

    @property
    def token(self) -> str:               # Hex encoded
        value = self.__info.get('token')
        if value is None:
            value = self.__info.get('device_token')
            if value is None:
                device = self.__info.get('device')
                if isinstance(device, Dict):
                    value = device.get('token')
        return value

    @property
    def topic(self) -> Optional[str]:     # 'chat.dim.sechat'
        return self.__info.get('topic')

    @property
    def sandbox(self) -> Optional[bool]:
        value = self.__info.get('sandbox')
        return Converter.get_bool(value=value, default=None)

    @property
    def time(self) -> Optional[DateTime]:
        value = self.__info.get('time')
        return Converter.get_datetime(value=value, default=None)

    @property
    def model(self) -> Optional[str]:     # 'iPad'
        return self.__info.get('model')

    @property
    def platform(self) -> Optional[str]:  # 'iOS'
        return self.__info.get('platform')

    @property
    def system(self) -> Optional[str]:    # 'iPadOS 16.3'
        return self.__info.get('system')

    @property
    def channel(self) -> Optional[str]:   # 'Firebase'
        return self.__info.get('channel')

    def __str__(self) -> str:
        clazz = self.__class__.__name__
        return '<%s token="%s" topic="%s" sandbox=%s />' % (clazz, self.token, self.topic, self.sandbox)

    def __repr__(self) -> str:
        clazz = self.__class__.__name__
        return '<%s token="%s" topic="%s" sandbox=%s>' \
               '%s (%s) %s' \
               '</%s>' % (clazz, self.token, self.topic, self.sandbox, self.model, self.platform, self.system, clazz)

    def to_json(self) -> Dict[str, Any]:
        return self.__info

    @classmethod
    def from_json(cls, info: Dict[str, Any]):  # -> Optional[DeviceInfo]:
        if isinstance(info, Dict):
            pass
        elif isinstance(info, str):
            info = {'token': info}
        else:
            # assert False, 'device info error: %s' % info
            return None
        return DeviceInfo(info=info)

    @classmethod
    def convert(cls, array: List[Dict[str, Any]]):  # -> List[DeviceInfo]:
        devices = []
        for item in array:
            info = cls.from_json(info=item)
            if info is None:
                continue
            devices.append(info)
        return devices

    @classmethod
    def revert(cls, devices) -> List[Dict[str, Any]]:
        array = []
        for item in devices:
            if isinstance(item, DeviceInfo):
                info = item.to_json()
            elif isinstance(item, Dict):
                info = item
            elif isinstance(item, str):
                info = {'token': str}
            else:
                continue
            array.append(info)
        return array


class DeviceStorage(Storage):
    """
        Device Tokens for APNS
        ~~~~~~~~~~~~~~~~~~~~~~

        file path: '.dim/protected/{ADDRESS}/devices.js'
    """
    devices_path = '{PROTECTED}/{ADDRESS}/devices.js'

    def show_info(self):
        path = self.protected_path(self.devices_path)
        print('!!!        devices path: %s' % path)

    def __devices_path(self, identifier: ID) -> str:
        path = self.protected_path(self.devices_path)
        return template_replace(path, 'ADDRESS', str(identifier.address))

    async def get_devices(self, identifier: ID) -> Optional[List[DeviceInfo]]:
        path = self.__devices_path(identifier=identifier)
        array = await self.read_json(path=path)
        if not isinstance(array, List):
            self.error(msg='devices not exists: %s' % path)
            return None
        self.info('loaded %d device(s) from: %s' % (len(array), path))
        return DeviceInfo.convert(array=array)

    async def save_devices(self, devices: List[DeviceInfo], identifier: ID) -> bool:
        path = self.__devices_path(identifier=identifier)
        self.info('saving %d device(s) into: %s' % (len(devices), path))
        return await self.write_json(container=DeviceInfo.revert(devices=devices), path=path)

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


def insert_device(info: DeviceInfo, devices: List[DeviceInfo]) -> Optional[List[DeviceInfo]]:
    index = find_device(info=info, devices=devices)
    if index < 0:
        # keep only last three records
        while len(devices) > 2:
            devices.pop()
    elif is_before(old_time=devices[index].time, new_time=info.time):
        # device info expired, drop it
        return None
    else:
        # token exists, replace with new device info
        devices.pop(index)
    # insert as the first device
    devices.insert(0, info)
    return devices


def find_device(info: DeviceInfo, devices: List[DeviceInfo]) -> int:
    index = 0
    for item in devices:
        if item.token == info.token:
            return index
        else:
            index += 1
    # device token not exists
    return -1
