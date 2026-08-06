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
from ..common.protocol import PushCommand
from ..common import PushInfo
from ..database import DeviceInfo


class PushNotificationService(ABC):

    @abstractmethod
    async def push_notification(self, aps: PushInfo, device: DeviceInfo, receiver: ID) -> bool:
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.push_notification()'
        )


class PushTask(PushCommand):

    EXPIRES = 300

    # def __init__(self, content: Dict[str, Any]):
    #     super().__init__(content=content)

    @property
    def is_expired(self) -> bool:
        expired = DateTime.current_timestamp() - self.EXPIRES
        when = self.time
        return when is None or when < expired


@Singleton
class PushNotificationClient(Runner, Logging):

    class Delegate(ABC):
        """
            APNs Delegate
            ~~~~~~~~~~~~~
        """

        @abstractmethod
        async def get_devices(self, user: ID) -> List[DeviceInfo]:
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

    def add_task(self, content: PushCommand):
        info = content.to_map()
        task = PushTask(content=info)
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
        sid = task.get_str(key='MTA')
        # push items
        for item in array:
            try:
                await self.__push(aps=item.info, receiver=item.receiver, mta=sid)
            except Exception as error:
                self.error('push error: %s, item: %s', error, item)
        return True

    async def __push(self, aps: PushInfo, receiver: ID, mta: Optional[str]) -> bool:
        devices = await self.delegate.get_devices(user=receiver)
        cnt = len(devices)
        self.info('got %d device token(s) for user: %s', cnt, receiver)
        if cnt == 0:
            return False
        i = 0
        for item in devices:
            i += 1
            platform = item.platform
            if not item.is_matched(identifier=receiver):
                self.warning('[%d/%d] device not matched: %s -> "/%s" %s.', i, cnt, receiver, item.terminal, platform)
                continue
            elif item.is_expired:
                self.warning('[%d/%d] device info expired: %s -> %s.', i, cnt, receiver, item)
                continue
            elif platform is None:
                self.error('[%d/%d] device info error: %s -> %s.', i, cnt, receiver, item)
                continue
            else:
                platform = platform.strip()
                platform = platform.lower()
                self.info('[%d/%d] pushing to device: %s -> %s.', i, cnt, receiver, item)
            # checking platform
            if platform == 'ios':
                pns = self.apple_pns
            elif platform == 'android':
                pns = self.android_pns
            else:
                self.error('device platform error: %s -> %s.', receiver, item)
                continue
            if pns is None:
                self.error('push service not found: %s (%s)', receiver, platform)
            elif await pns.push_notification(aps=aps, device=item, receiver=receiver):
                self.info('push notification success: %s (%s), MTA: %s.', receiver, platform, mta)
                return True
            else:
                self.error('push notification error: %s (%s), MTA: %s', receiver, platform, mta)
