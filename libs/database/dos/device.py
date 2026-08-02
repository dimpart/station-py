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

from typing import Optional, List

from dimples import Converter
from dimples import DateTime
from dimples import ID
from dimples.utils import is_before
from dimples.database.dos.base import template_replace
from dimples.database.dos import Storage

from ...utils import StrMap


class DeviceInfo:
    """
        Push Notification service
        ~~~~~~~~~~~~~~~~~~~~~~~~~
        Device info report from client


        Android
        ~~~~~~~
            data format: {
                "time"         : 123.45,
                "terminal"     : "HWMRX",

                "title"        : "c2dm",

                "platform"     : "Android",
                "channel"      : "firebase",
                "token"        : "..."
            }

        iOS
        ~~~
            data format: {
                "time"         : 123.45,
                "terminal"     : "iPhone9_2",

                "title"        : "apns",

                "platform"     : "iOS",
                "topic"        : "chat.dim.tarsier",
                "sandbox"      : true,
                "device_token" : "..."
            }
    """

    EXPIRES = 3600 * 24 * 90  # device token will be expired after 3 months

    def __init__(self, info: StrMap):
        super().__init__()
        self.__info = info

    @property
    def is_expired(self) -> bool:
        when = self.time
        if when is None:
            return True
        now = DateTime.current_timestamp()
        return when < (now - self.EXPIRES)

    @property
    def time(self) -> Optional[DateTime]:
        value = self.__info.get('time')
        return Converter.get_datetime(value=value, default=None)

    @property
    def terminal(self) -> Optional[str]:
        value = self.__info.get('terminal')
        return Converter.get_str(value=value, default='')

    @property
    def title(self) -> Optional[str]:
        value = self.__info.get('title')
        return Converter.get_str(value=value, default='')

    @property
    def platform(self) -> Optional[str]:  # 'iOS'
        value = self.__info.get('platform')
        return Converter.get_str(value=value, default='')

    @property
    def channel(self) -> Optional[str]:   # 'Firebase'
        value = self.__info.get('channel')
        return Converter.get_str(value=value, default=None)

    @property
    def topic(self) -> Optional[str]:     # 'chat.dim.sechat'
        value = self.__info.get('topic')
        return Converter.get_str(value=value, default=None)

    @property
    def sandbox(self) -> Optional[bool]:
        value = self.__info.get('sandbox')
        return Converter.get_bool(value=value, default=None)

    @property
    def token(self) -> str:
        value = self.__info.get('token')
        if value is None:
            value = self.__info.get('device_token')
            if value is None:
                # compact with old version
                device = self.__info.get('device')
                if isinstance(device, dict):
                    value = device.get('token')
        return Converter.get_str(value=value, default='')

    def is_matched(self, identifier: ID) -> bool:
        terminal = identifier.terminal
        if terminal is None:
            terminal = ''
        return terminal == self.terminal

    def to_str(self) -> str:
        clazz = self.__class__.__name__
        title = self.title
        platform = self.platform
        terminal = self.terminal
        token = self.token
        return '<%s title="%s" platform="%s" terminal="%s" time="%s">\n' \
               '    token: "%s"\n' \
               '    channel: %s\n' \
               '    topic: %s\n' \
               '    sandbox: %s\n' \
               '' \
               '</%s>'\
               % (clazz, title, platform, terminal, self.time, token, self.channel, self.token, self.sandbox, clazz)

    def __str__(self) -> str:
        return self.to_str()

    def __repr__(self) -> str:
        return self.to_str()

    def to_json(self) -> StrMap:
        return self.__info

    @classmethod
    def from_json(cls, info: StrMap):  # -> Optional[DeviceInfo]:
        if isinstance(info, dict):
            pass
        elif isinstance(info, str):
            info = {'token': info}
        else:
            # assert False, f'device info error: {info}'
            return None
        return DeviceInfo(info=info)

    @classmethod
    def convert(cls, array: List[StrMap]):  # -> List[DeviceInfo]:
        devices = []
        for item in array:
            info = cls.from_json(info=item)
            if info is None:
                continue
            devices.append(info)
        return devices

    @classmethod
    def revert(cls, devices) -> List[StrMap]:
        array = []
        for item in devices:
            if isinstance(item, DeviceInfo):
                info = item.to_json()
            elif isinstance(item, dict):
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
        if not isinstance(array, list):
            self.error('devices not exists: %s', path)
            return None
        self.info('loaded %d device(s) from: %s', len(array), path)
        return DeviceInfo.convert(array=array)

    async def save_devices(self, devices: List[DeviceInfo], identifier: ID) -> bool:
        path = self.__devices_path(identifier=identifier)
        self.info('saving %d device(s) into: %s', len(devices), path)
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
