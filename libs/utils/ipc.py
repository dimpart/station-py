# -*- coding: utf-8 -*-
#
#   IPC: Inter-Process Communication
#
#                                Written in 2021 by Moky <albert.moky@gmail.com>
#
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

import threading
from abc import ABC
from typing import Optional, Tuple, Any

from small.skywalker import Runner

from ipx import Arrow, SharedMemoryArrow
# from ipx.shm.mmap import MmapSharedMemoryController as DefaultController
# from ipx.shm.mp import MpSharedMemoryController as DefaultController
from .sysv import SysvSharedMemoryController as DefaultController


# noinspection PyAbstractClass
class AutoArrow(Runner, ABC):

    # Memory cache size: 64KB
    SHM_SIZE = 1 << 16

    def __init__(self, name: str):
        super().__init__(interval=Runner.INTERVAL_SLOW)
        controller = DefaultController.new(size=self.SHM_SIZE, name=name)
        self.__arrow = SharedMemoryArrow(controller=controller)

    @property  # protected
    def arrow(self) -> Arrow:
        return self.__arrow


class IncomeArrow(AutoArrow):
    """ auto receiving """

    def __init__(self, name: str):
        super().__init__(name=name)
        self.__lock = threading.Lock()
        self.__pool = []

    def receive(self) -> Optional[Any]:
        with self.__lock:
            if len(self.__pool) > 0:
                return self.__pool.pop(0)

    # Override
    async def process(self) -> bool:
        # drive the arrow to receive objects
        obj = self.arrow.receive()
        if obj is None:
            return False
        with self.__lock:
            self.__pool.append(obj)
        return True


class OutgoArrow(AutoArrow):
    """ auto sending """

    def __init__(self, name: str):
        super().__init__(name=name)
        self.__lock = threading.Lock()

    def send(self, obj: Optional[Any]) -> int:
        """ return -1 on failed """
        with self.__lock:
            try:
                cnt = self.arrow.send(obj=obj)
                if cnt < 0:
                    print('[IPC] waiting queue is full, dropped: %s' % obj)
                return cnt
            except Exception as error:
                print('[IPC] failed to send: %s, %s' % (obj, error))
                return -1

    # Override
    async def process(self) -> bool:
        # send None to drive the arrow to re-send delay objects
        self.send(obj=None)
        return False


class Pipe(Runner):

    def __init__(self, arrows: Tuple[Optional[IncomeArrow], Optional[OutgoArrow]]):
        super().__init__(interval=Runner.INTERVAL_SLOW)
        self.__income_arrow = arrows[0]
        self.__outgo_arrow = arrows[1]

    def send(self, obj: Optional[Any]) -> int:
        return self.__outgo_arrow.send(obj=obj)

    def receive(self) -> Optional[Any]:
        return self.__income_arrow.receive()

    # Override
    async def process(self) -> bool:
        incoming = self.__income_arrow
        outgoing = self.__outgo_arrow
        # drive outgo arrow to re-send delay objects
        if outgoing is not None:
            await outgoing.process()
        # drive income arrow to receive objects
        if incoming is not None:
            return await incoming.process()


class SHM:
    """
        Station process IDs
        ~~~~~~~~~~~~~~~~~~~

            0 - main           dispatcher, filter
            1 - receptionist   offline messages
            2 - archivist      search engine
            3 - pusher         notification (ios, android)
            7 - monitor        statistic, session
            8 - octopus        station bridge
    """

    RECEPTIONIST_KEY1 = '0x%X' % 0xD1350101  # A -> B
    RECEPTIONIST_KEY2 = '0x%X' % 0xD1350102  # B -> A

    ARCHIVIST_KEY1 = '0x%X' % 0xD1350201  # A -> B
    ARCHIVIST_KEY2 = '0x%X' % 0xD1350202  # B -> A

    PUSHER_KEY = "0x%X" % 0xD1350301  # A -> B

    MONITOR_KEY = "0x%X" % 0xD1350701  # A -> B

    OCTOPUS_KEY1 = '0x%X' % 0xD1350801  # A -> B
    OCTOPUS_KEY2 = '0x%X' % 0xD1350802  # B -> A


class ReceptionistPipe(Pipe):
    """ arrows between router and receptionist """

    @classmethod
    def primary(cls) -> Pipe:  # arrows for router
        incoming = IncomeArrow(name=SHM.RECEPTIONIST_KEY2)
        outgoing = OutgoArrow(name=SHM.RECEPTIONIST_KEY1)
        return cls(arrows=(incoming, outgoing))

    @classmethod
    def secondary(cls) -> Pipe:  # arrows for receptionist
        incoming = IncomeArrow(name=SHM.RECEPTIONIST_KEY1)
        outgoing = OutgoArrow(name=SHM.RECEPTIONIST_KEY2)
        return cls(arrows=(incoming, outgoing))


class ArchivistPipe(Pipe):
    """ arrows between router and archivist """

    @classmethod
    def primary(cls) -> Pipe:  # arrows for router
        incoming = IncomeArrow(name=SHM.ARCHIVIST_KEY2)
        outgoing = OutgoArrow(name=SHM.ARCHIVIST_KEY1)
        return cls(arrows=(incoming, outgoing))

    @classmethod
    def secondary(cls) -> Pipe:  # arrows for archivist
        incoming = IncomeArrow(name=SHM.ARCHIVIST_KEY1)
        outgoing = OutgoArrow(name=SHM.ARCHIVIST_KEY2)
        return cls(arrows=(incoming, outgoing))


class OctopusPipe(Pipe):
    """ arrows between router and bridge """

    @classmethod
    def primary(cls) -> Pipe:  # arrows for router
        incoming = IncomeArrow(name=SHM.OCTOPUS_KEY2)
        outgoing = OutgoArrow(name=SHM.OCTOPUS_KEY1)
        return cls(arrows=(incoming, outgoing))

    @classmethod
    def secondary(cls) -> Pipe:  # arrows for octopus
        incoming = IncomeArrow(name=SHM.OCTOPUS_KEY1)
        outgoing = OutgoArrow(name=SHM.OCTOPUS_KEY2)
        return cls(arrows=(incoming, outgoing))


class PusherPipe(Pipe):
    """ arrow from router(dispatcher) to pusher """

    @classmethod
    def primary(cls) -> Pipe:  # arrow for router(dispatcher)
        outgoing = OutgoArrow(name=SHM.PUSHER_KEY)
        return cls(arrows=(None, outgoing))

    @classmethod
    def secondary(cls) -> Pipe:  # arrow for pusher
        incoming = IncomeArrow(name=SHM.PUSHER_KEY)
        return cls(arrows=(incoming, None))


class MonitorPipe(Pipe):
    """ arrow from router(dispatcher) to monitor """

    @classmethod
    def primary(cls) -> Pipe:  # arrow for router(dispatcher)
        outgoing = OutgoArrow(name=SHM.MONITOR_KEY)
        return cls(arrows=(None, outgoing))

    @classmethod
    def secondary(cls) -> Pipe:  # arrow for monitor
        incoming = IncomeArrow(name=SHM.MONITOR_KEY)
        return cls(arrows=(incoming, None))
