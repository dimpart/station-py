# -*- coding: utf-8 -*-
#
#   APNs : Apple Push Notification service
#
#                                Written in 2019 by Moky <albert.moky@gmail.com>
#
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
    Apple Push Notification service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    APNs

    A service for pushing notification to offline device
"""

from typing import Optional

from apns2.client import APNsClient, NotificationPriority
from apns2.errors import APNsException
from apns2.payload import Payload, PayloadAlert

from dimples import ID

from ..utils import Logging
from ..common import PushInfo
from ..database import DeviceInfo

from .manager import PushNotificationService


class ApplePushNotificationService(PushNotificationService, Logging):

    def __init__(self, credentials, use_sandbox=False, use_alternative_port=False, proto=None, json_encoder=None,
                 password=None, proxy_host=None, proxy_port=None):
        super().__init__()
        # APNs client parameters
        self.credentials = credentials
        self.use_sandbox = use_sandbox
        self.use_alternative_port = use_alternative_port
        self.proto = proto
        self.json_encoder = json_encoder
        self.password = password
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        # APNsClient
        self.__client_prod = None  # production
        self.__client_test = None  # sandbox
        # topic
        self.topic = 'chat.dim.sechat'

    def __connect(self, sandbox: bool) -> Optional[APNsClient]:
        try:
            return APNsClient(credentials=self.credentials, use_sandbox=sandbox,
                              use_alternative_port=self.use_alternative_port,
                              proto=self.proto, json_encoder=self.json_encoder, password=self.password,
                              proxy_host=self.proxy_host, proxy_port=self.proxy_port)
        except IOError as error:
            self.error('failed to connect apple server: %s', error)

    @property
    def client_prod(self) -> Optional[APNsClient]:
        client = self.__client_prod
        if client is None:
            client = self.__connect(sandbox=False)
            self.__client_prod = client
        return client

    @property
    def client_test(self) -> Optional[APNsClient]:
        client = self.__client_test
        if client is None:
            client = self.__connect(sandbox=True)
            self.__client_test = client
        return client

    def send_notification(self, notification, token_hex, topic: Optional[str], sandbox: bool,
                          priority=NotificationPriority.Immediate, expiration=None, collapse_id=None) -> int:
        # get APNsClient
        if sandbox:
            client = self.client_test
        else:
            client = self.client_prod
        if client is None:
            self.error('cannot connect apple server, message dropped: %s', notification)
            return -503  # Service Unavailable
        # try to send notification
        try:
            # push to apple server
            client.send_notification(token_hex=token_hex, notification=notification, topic=topic,
                                     priority=priority, expiration=expiration, collapse_id=collapse_id)
            return 200  # OK
        except IOError as error:
            self.error('connection lost: %s, sandbox: %s', error, sandbox)
            return -408  # Request Timeout
        except APNsException as error:
            self.error('failed to push notification: %s, error: %s', notification, error)
            return -400  # Bad Request

    #
    #   PushService
    #

    # Override
    async def push_notification(self, aps: PushInfo, device: DeviceInfo, receiver: ID) -> bool:
        # 1. check parameters
        title = aps.title
        content = aps.content
        image = aps.image
        badge = aps.badge
        sound = aps.sound
        # 2. send
        alert = PayloadAlert(title=title, body=content, launch_image=image)
        payload = Payload(alert=alert, badge=badge, sound=sound)
        self.info('sending notification for %s (%s) to ios device: %s', receiver, content, device)
        # check for iOS platform
        platform = device.platform
        if platform is not None and platform.lower() != 'ios':
            self.warning('It is not an iOS device, skip it: %s', platform)
            return False
        token = device.token
        topic = device.topic
        sandbox = device.sandbox
        if topic is None:
            topic = self.topic
        if sandbox is None:
            sandbox = self.use_sandbox
        # first try
        result = self.send_notification(notification=payload, token_hex=token, topic=topic, sandbox=sandbox)
        if result == -503:  # Service Unavailable
            # connection failed
            return False
        elif result == -408:  # Request Timeout
            self.error('Broken pipe? try to reconnect again!')
            # reset APNs client
            if sandbox:
                self.__client_test = None
            else:
                self.__client_prod = None
            # try again
            result = self.send_notification(notification=payload, token_hex=token, topic=topic, sandbox=sandbox)
        if result == 200:  # OK
            self.info('notification sent for %s, badge=%d', receiver, badge)
            return True
