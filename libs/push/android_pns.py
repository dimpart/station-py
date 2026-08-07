# -*- coding: utf-8 -*-

"""
    Android Push Notification service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    C2DM / FCM

    A service for pushing notification to offline device
"""

import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

from dimples import DateTime
from dimples import ID

from ..utils import Logging
from ..common import PushInfo
from ..database import DeviceInfo

from .manager import PushNotificationService


class AndroidPushNotificationService(PushNotificationService, Logging):

    def __init__(self, cert: str):
        super().__init__()
        self.__cert = cert
        self.__ready = False

    def _check_ready(self) -> bool:
        if self.__ready:
            return True
        cert = self.__cert
        if cert is None or len(cert) == 0:
            return False
        else:
            # only init once
            self.__cert = None
        self.info('initializing FCM client: %s', cert)
        cred = credentials.Certificate(cert)
        firebase_admin.initialize_app(cred)
        self.__ready = True
        return True

    def send_notification(self, notification: messaging.AndroidNotification, token: str):
        try:
            if not self._check_ready():
                self.error('FCM client not ready')
                return None
            # badge count
            badge = notification.notification_count
            if badge is None:
                badge = '0'
            elif not isinstance(badge, str):
                badge = str(badge)
            # build message
            now = DateTime.current_timestamp()
            message = messaging.Message(
                android=messaging.AndroidConfig(
                    notification=notification,
                    data={
                        'badge_count': badge,
                    },
                ),
                data={
                    'badge': badge,
                    'time': str(now),
                },
                token=token,
            )
            # send message
            return messaging.send(message)
        except Exception as error:
            self.error('failed to push notification: %s, error: %s', notification, error)

    def send_message(self, title: str, body: str, image: str, badge: int, sound: str, token: str):
        notification = messaging.AndroidNotification(
            title=title,
            body=body,
            sound=sound,
            image=image,
            notification_count=badge,
        )
        responses = self.send_notification(notification=notification, token=token)
        self.info('message "%s" sent, respond: %s', title, responses)
        return responses

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
        self.info('sending notification for %s (%s) to android device: %s', receiver, content, device)
        # 2. check channel
        channel = device.channel
        platform = device.platform
        if platform is None or platform.lower() != 'android':
            self.warning('It is not an Android device, skip it: %s, %s', platform, receiver)
            return False
        elif channel is None or channel.lower() != 'firebase':
            self.warning('C2DM channel not support yet: %s, %s', channel, receiver)
            return False
        token = device.token
        res = self.send_message(title=title, body=content, image=image, badge=badge, sound=sound, token=token)
        return res is not None
