# -*- coding: utf-8 -*-

"""
    Android Push Notification service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A service for pushing notification to offline device
"""

import threading
import weakref
from abc import ABC, abstractmethod
from typing import Optional, List

from dimples import DateTime
from dimples import ID

from ..utils import Singleton, Logging, Runner
from ..common import PushInfo, PushItem
from ..database import DeviceInfo


class PushNotificationService(ABC):

    @abstractmethod
    async def push_notification(self, aps: PushInfo, device: DeviceInfo, receiver: ID) -> bool:
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.push_notification()'
        )


class PushTask:

    EXPIRES = 300

    def __init__(self, items: List[PushItem], msg_time: DateTime):
        super().__init__()
        self.__items = items
        self.__time = msg_time.timestamp

    @property
    def items(self) -> List[PushItem]:
        return self.__items

    @property
    def is_expired(self) -> bool:
        now = DateTime.now()
        return self.__time < (now.timestamp - self.EXPIRES)


@Singleton
class PushNotificationClient(Runner, Logging):

    class Delegate(ABC):
        """
            APNs Delegate
            ~~~~~~~~~~~~~
        """

        @abstractmethod
        async def get_devices(self, identifier: ID) -> Optional[List[DeviceInfo]]:
            """ get devices with token in hex format """
            pass

    def __init__(self):
        super().__init__(interval=Runner.INTERVAL_SLOW)
        self.__apple: Optional[PushNotificationService] = None
        self.__android: Optional[PushNotificationService] = None
        # delegate to get device token
        self.__delegate: Optional[weakref.ReferenceType] = None  # APNs Delegate
        # push tasks
        self.__tasks: List[PushTask] = []
        self.__lock = threading.Lock()
        # auto run
        self.start()

    @property
    def apple_pns(self) -> Optional[PushNotificationService]:
        return self.__apple

    @apple_pns.setter
    def apple_pns(self, pns: PushNotificationService):
        self.__apple = pns

    @property
    def android_pns(self) -> Optional[PushNotificationService]:
        return self.__android

    @android_pns.setter
    def android_pns(self, pns: PushNotificationService):
        self.__android = pns

    @property
    def delegate(self) -> Delegate:
        if self.__delegate is not None:
            return self.__delegate()

    @delegate.setter
    def delegate(self, value: Delegate):
        self.__delegate = weakref.ref(value)

    def add_task(self, items: List[PushItem], msg_time: DateTime):
        task = PushTask(items=items, msg_time=msg_time)
        with self.__lock:
            self.__tasks.append(task)

    def __next_task(self) -> Optional[PushTask]:
        with self.__lock:
            if len(self.__tasks) > 0:
                return self.__tasks.pop(0)

    def start(self):
        thr = Runner.async_thread(coro=self.run())
        thr.start()

    # Override
    async def process(self) -> bool:
        task = self.__next_task()
        if task is None:
            # nothing to do now, return False to have a rest
            return False
        array = task.items
        if task.is_expired:
            self.warning('task expired, drop %d item(s).', len(array))
            array = []
        # push items
        for item in array:
            try:
                await self.__push(aps=item.info, receiver=item.receiver)
            except Exception as error:
                self.error('push error: %s, item: %s', error, item)
        return True

    async def __push(self, aps: PushInfo, receiver: ID) -> bool:
        devices = await self.delegate.get_devices(identifier=receiver)
        if devices is None or len(devices) == 0:
            self.warning('cannot get device token for user %s', receiver)
            return False
        for item in devices:
            platform = item.platform
            if platform is None:
                self.error('device error: %s => %s', item, receiver)
                continue
            platform = platform.lower()
            if platform == 'ios':
                pns = self.apple_pns
            elif platform == 'android':
                pns = self.android_pns
            else:
                self.error('platform error: %s, %s => %s', platform, item, receiver)
                continue
            if pns is None:
                self.error('push notification service not found: %s', platform)
            elif await pns.push_notification(aps=aps, device=item, receiver=receiver):
                self.info('push notification success: %s', receiver)
                return True
            else:
                self.error('push notification error: %s', receiver)
