#! /usr/bin/env python3
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
    Send SMS
    ~~~~~~~~

    Usage:
        ./send.py moky@4DnqXWdTV8wuZgfqSCX9GjE2kNq7HJrUgQ "Hello!"
"""

import sys
from typing import Optional, List

from apns2.client import APNsClient
from apns2.payload import Payload

from dimples import *
from dimples.utils import Path, Log, Runner
from dimples.database.dos import Storage

path = Path.abs(path=__file__)
path = Path.dir(path=path)
path = Path.dir(path=path)
Path.add(path=path)

from libs.database import DeviceInfo


"""
    Configuration
    ~~~~~~~~~~~~~
    
    openssl pkcs12 -nodes -in Certificates.p1k2 -out credentials.pem
"""
base_dir = '/data/.dim'

credentials = '/srv/dims/etc/apns/credentials.pem'
use_sandbox = True
default_topic = 'chat.dim.tarsier'


class DeviceLoader:
    """ Get device tokens """

    def __init__(self, identifier: str):
        self.__identifier = ID.parse(identifier=identifier)

    @property
    def path(self) -> str:
        address = self.__identifier.address
        return base_dir + '/private/' + str(address) + '/devices.js'

    @property
    async def devices(self) -> List[DeviceInfo]:
        array = await Storage.read_json(path=self.path)
        if not isinstance(array, list):
            array = []
        Log.info('loaded %d device(s) from: %s' % (len(array), path))
        return DeviceInfo.convert(array=array)


class SMS:
    """ Push SMS via APNs """

    def __init__(self):
        super().__init__()
        self.__client_prod = None  # production
        self.__client_test = None  # sandbox

    @classmethod
    def connect(cls, sandbox: bool) -> Optional[APNsClient]:
        try:
            return APNsClient(credentials=credentials, use_sandbox=sandbox)
        except IOError as error:
            Log.error('failed to connect apple server: %s' % error)

    @property
    def client_prod(self) -> Optional[APNsClient]:
        client = self.__client_prod
        if client is None:
            client = self.connect(sandbox=False)
            self.__client_prod = client
        return client

    @property
    def client_test(self) -> Optional[APNsClient]:
        client = self.__client_test
        if client is None:
            client = self.connect(sandbox=True)
            self.__client_test = client
        return client

    async def send(self, identifier: str, text: str) -> int:
        identifier = ID.parse(identifier=identifier)
        payload = Payload(alert=text)
        # get devices
        loader = DeviceLoader(identifier)
        devices = await loader.devices
        if devices is None or len(devices) == 0:
            print('Device token not found, failed to push message: %s' % payload.alert)
            return 0
        count = 0
        for item in devices:
            topic = item.topic
            if topic is None:
                topic = default_topic
            sandbox = item.sandbox
            if sandbox is None:
                sandbox = use_sandbox
            # get APNsClient
            if sandbox:
                client = self.client_test
            else:
                client = self.client_prod
            # try to send
            client.send_notification(token_hex=item.token, notification=payload, topic=topic)
            count += 1
        print('Message has been sent to %d device(s)' % count)
        return count


async def send(text: str, identifier: str) -> bool:
    msg = SMS()
    count = await msg.send(identifier=identifier, text=text)
    return count > 0


async def async_main():
    # check arguments
    if len(sys.argv) == 3:
        coro = send(text=sys.argv[2], identifier=sys.argv[1])
        Runner.sync_run(main=coro)
    else:
        print('Usage:')
        print('    %s "ID" "text"' % sys.argv[0])
        print('')


def main():
    Runner.sync_run(main=async_main())


if __name__ == '__main__':
    main()
