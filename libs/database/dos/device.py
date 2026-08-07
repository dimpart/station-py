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
from dimples import Dictionary
from dimples import ID
from dimples.utils import is_before
from dimples.database.dos.base import template_replace
from dimples.database.dos import Storage

from ...utils import StrMap


class DeviceInfo(Dictionary):
    """
        Push Notification service
        ~~~~~~~~~~~~~~~~~~~~~~~~~
        Device info report from client


        Android
        ~~~~~~~
            data format: {
                "time"         : 123.45,
                "did"          : "[name@]address[/terminal]",

                "title"        : "c2dm",

                "platform"     : "Android",
                "channel"      : "firebase",
                "token"        : "..."
            }

        iOS
        ~~~
            data format: {
                "time"         : 123.45,
                "did"          : "[name@]address[/terminal]",

                "title"        : "apns",

                "platform"     : "iOS",
                "topic"        : "chat.dim.tarsier",
                "sandbox"      : true,
                "device_token" : "..."
            }
    """

    EXPIRES = 3600 * 24 * 183  # device token will be expired after half a year

    def __init__(self, info: StrMap):
        super().__init__(dictionary=info)
        self.__identifier: Optional[ID] = None

    @property
    def is_expired(self) -> bool:
        when = self.time
        if when is None:
            return True
        elif self.channel == 'firebase':
            # TODO: timeout for firebase
            return False
        now = DateTime.current_timestamp()
        return when < (now - self.EXPIRES)

    @property
    def time(self) -> Optional[DateTime]:
        return self.get_datetime(key='time')

    @property
    def identifier(self) -> Optional[ID]:
        did = self.__identifier
        if did is None:
            text = self.get('did')
            did = ID.parse(identifier=text)
            self.__identifier = did
        return did

    @property
    def terminal(self) -> Optional[str]:
        device = self.get_str(key='terminal')
        if device is not None and len(device) > 0:
            return device
        did = self.identifier
        if did is not None:
            return did.terminal

    @property
    def title(self) -> Optional[str]:
        return self.get_str(key='title', default='')

    @property
    def platform(self) -> Optional[str]:  # 'iOS'
        return self.get_str(key='platform', default='')

    @property
    def channel(self) -> Optional[str]:   # 'Firebase'
        return self.get_str(key='channel')

    @property
    def topic(self) -> Optional[str]:     # 'chat.dim.sechat'
        return self.get_str(key='topic')

    @property
    def sandbox(self) -> Optional[bool]:
        return self.get_str(key='sandbox')

    @property
    def token(self) -> str:
        value = self.get('device_token')
        if value is None:
            value = self.get('token')
            if value is None:
                # compact with old version
                device = self.get('device')
                if isinstance(device, dict):
                    value = device.get('token')
        return Converter.get_str(value=value, default='')

    def is_matched(self, identifier: ID) -> bool:
        terminal = identifier.terminal
        device = self.terminal
        return terminal == device

    def to_str(self) -> str:
        clazz = self.__class__.__name__
        title = self.title
        platform = self.platform
        identifier = self.identifier
        token = self.token
        return '<%s title="%s" platform="%s" time="%s">\n' \
               '    user id : "%s"\n' \
               '    token   : "%s"\n' \
               '    channel : %s\n' \
               '    topic   : %s\n' \
               '    sandbox : %s\n' \
               '' \
               '</%s>'\
               % (clazz, title, platform, self.time, identifier, token, self.channel, self.topic, self.sandbox, clazz)

    def __str__(self) -> str:
        return self.to_str()

    def __repr__(self) -> str:
        return self.to_str()

    def to_json(self) -> StrMap:
        return self.to_map()

    @classmethod
    def from_json(cls, info: StrMap):  # -> Optional[DeviceInfo]:
        # check token
        token = info.get('device_token')
        if token is None or token == '':
            token = info.get('token')
            if token is None or token == '':
                return None
        # OK
        return DeviceInfo(info=info)

    @classmethod
    def convert(cls, array: List[StrMap]):  # -> List[DeviceInfo]:
        devices = []
        for item in array:
            if isinstance(item, dict):
                info = cls.from_json(info=item)
            elif isinstance(item, str):
                # old version
                info = cls.from_json(info={
                    'token': item,
                })
            else:
                # error
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

    def __devices_path(self, user: ID) -> str:
        path = self.protected_path(self.devices_path)
        address = str(user.address)
        return template_replace(path, 'ADDRESS', address)

    async def get_devices(self, user: ID) -> Optional[List[DeviceInfo]]:
        path = self.__devices_path(user=user)
        array = await self.read_json(path=path)
        if not isinstance(array, list):
            self.error('devices not exists: %s', path)
            return None
        self.info('loaded %d device(s) from: %s', len(array), path)
        return DeviceInfo.convert(array=array)

    async def save_devices(self, devices: List[DeviceInfo], user: ID) -> bool:
        path = self.__devices_path(user=user)
        self.info('saving %d device(s) into: %s', len(devices), path)
        return await self.write_json(container=DeviceInfo.revert(devices=devices), path=path)

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


def insert_device(info: DeviceInfo, devices: List[DeviceInfo]) -> Optional[List[DeviceInfo]]:
    index = find_device(info=info, devices=devices)
    if index < 0:
        # keep only last eight records
        while len(devices) > 7:
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
