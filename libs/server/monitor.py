# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2023 Albert Moky
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
import time
import traceback
from abc import ABC, abstractmethod
from typing import Optional, Union, Tuple, List, Dict

from dimples import DateTime
from dimples import ID, ReliableMessage
from dimples import CustomizedContent
from dimples import SessionDBI

from ..utils import Singleton, Log, Logging
from ..utils import Runner
from ..common.protocol import PushItem, PushCommand

from .cpu import AnsCommandProcessor

from .emitter import ServerEmitter


#
#   Event Recorder
#
class Recorder(ABC):

    @abstractmethod
    def extract(self) -> Union[List, Dict]:
        """ get and clear records """
        raise NotImplemented


class Event(ABC):

    @abstractmethod
    async def handle(self, recorder: Recorder):
        """ handle the event """
        raise NotImplemented


@Singleton
class Monitor(Runner, Logging):

    INTERVAL = 60  # seconds

    def __init__(self):
        super().__init__(interval=Runner.INTERVAL_SLOW)
        self.__events = []
        self.__lock = threading.Lock()
        self.__next_time = 0
        # recorders
        self.__usr_recorder: Optional[Recorder] = None
        self.__msg_recorder: Optional[Recorder] = None
        # service bot
        self.__bot: Optional[ID] = None
        # emitter to send message
        self.__emitter: Optional[ServerEmitter] = None
        # auto start
        self.start()

    @property
    def bot(self) -> Optional[ID]:
        receiver = self.__bot
        if receiver is None:
            receiver = AnsCommandProcessor.ans_id(name='monitor')
            self.__bot = receiver
        return receiver

    @property
    def emitter(self) -> ServerEmitter:
        return self.__emitter

    @emitter.setter
    def emitter(self, delegate: ServerEmitter):
        self.__emitter = delegate

    def _append_event(self, event: Event):
        with self.__lock:
            self.__events.append(event)

    def _next_event(self) -> Optional[Event]:
        with self.__lock:
            if len(self.__events) > 0:
                return self.__events.pop(0)

    def start(self):
        # next time to flush
        self.__next_time = time.time() + self.INTERVAL
        # create recorders
        self.__usr_recorder = ActiveRecorder()
        self.__msg_recorder = MessageRecorder()
        # start a background thread
        thr = Runner.async_thread(coro=self.run())
        thr.start()

    # Override
    async def process(self) -> bool:
        emitter = self.emitter
        if emitter is None:
            self.warning(msg='emitter not ready yet')
            return False
        # 1. check to flush data
        now = time.time()
        if now > self.__next_time:
            users = self.__usr_recorder.extract()
            stats = self.__msg_recorder.extract()
            try:
                await self.__send(users=users, stats=stats)
            except Exception as e:
                self.error(msg='failed to send data: %s' % e)
            # flush next time
            self.__next_time = now + self.INTERVAL
        # 2. check for next event
        event = self._next_event()
        if event is None:
            # nothing to do now, return False to let the thread have a rest
            return False
        try:
            await self.__handle(event=event)
        except Exception as e:
            self.error(msg='handle event error: %s' % e)
            traceback.print_exc()
        return True

    async def __handle(self, event: Event):
        if isinstance(event, ActiveEvent):
            await event.handle(recorder=self.__usr_recorder)
        elif isinstance(event, MessageEvent):
            await event.handle(recorder=self.__msg_recorder)
        else:
            self.error(msg='event error: %s' % event)

    async def __send(self, users: List, stats: List):
        bot = self.bot
        assert bot is not None, 'monitor bot not set'
        emitter = self.emitter
        assert emitter is not None, 'emitter not set'
        self.info(msg='sending monitor reports: %s' % bot)
        # send users data
        content = CustomizedContent.create(app='chat.dim.monitor', mod='users', act='post')
        content['users'] = users
        await emitter.send_content(content=content, receiver=bot)
        # send stats data
        content = CustomizedContent.create(app='chat.dim.monitor', mod='stats', act='post')
        content['stats'] = stats
        await emitter.send_content(content=content, receiver=bot)

    #
    #   Events
    #

    def user_online(self, sender: ID, remote_address: Tuple[str, int], when: DateTime):
        event = ActiveEvent(sender=sender, remote_address=remote_address, online=True, when=when)
        self._append_event(event=event)

    def user_offline(self, sender: ID, remote_address: Tuple[str, int], when: DateTime):
        event = ActiveEvent(sender=sender, remote_address=remote_address, online=False, when=when)
        self._append_event(event=event)

    def message_received(self, msg: ReliableMessage):
        event = MessageEvent(msg=msg)
        self._append_event(event=event)


#
#   Event Handlers
#


class ActiveEvent(Event, Logging):

    def __init__(self, sender: ID, remote_address: Tuple[str, int], online: bool, when: DateTime):
        super().__init__()
        self.__sender = sender
        self.__remote_address = remote_address
        self.__online = online
        self.__when = when

    # Override
    async def handle(self, recorder: Recorder):
        assert isinstance(recorder, ActiveRecorder), 'recorder error: %s' % recorder
        sender = self.__sender
        remote = self.__remote_address
        recorder.add_user(identifier=sender, remote_address=remote)
        # TODO: temporary notification, remove after too many users online
        online = self.__online
        when = self.__when
        await _notify_masters(sender=sender, online=online, remote_address=remote, when=when)


class ActiveRecorder(Recorder):
    """
        Active users recorder
        ~~~~~~~~~~~~~~~~~~~~~
    """

    def __init__(self):
        super().__init__()
        self.__users = set()

    def add_user(self, identifier: ID, remote_address: Tuple[str, int]):
        record = (identifier, remote_address[0])
        self.__users.add(record)

    # Override
    def extract(self) -> Union[List, Dict]:
        users = self.__users
        self.__users = set()
        array = []
        for item in users:
            array.append({
                'U': str(item[0]),
                'IP': item[1],
            })
        return array


class MessageEvent(Event):

    def __init__(self, msg: ReliableMessage):
        super().__init__()
        self.msg = msg

    # Override
    async def handle(self, recorder: Recorder):
        assert isinstance(recorder, MessageRecorder), 'recorder error: %s' % recorder
        sender = self.msg.sender
        msg_type = self.msg.type
        if msg_type is None:
            msg_type = 0
        recorder.increase_counter(sender_type=sender.type, msg_type=msg_type)


class MessageRecorder(Recorder):
    """
        Message stats recorder
        ~~~~~~~~~~~~~~~~~~~~~~

        'S' - Sender type
        'C' - Counter
        'U' - User ID (reserved)
        'T' - message Type
    """

    def __init__(self):
        super().__init__()
        self.__data = []

    def increase_counter(self, sender_type: int, msg_type: int):
        array = self.__data
        # get data record
        record = None
        for item in array:
            if item.get('S') == sender_type and item.get('T') == msg_type:
                # got it
                record = item
                break
        # increase counter
        if record is None:
            # create new record
            record = {
                'S': sender_type,
                'T': msg_type,
                'C': 1,
            }
            array.append(record)
        else:
            # update old record
            count = record.get('C')
            record['C'] = 1 if count is None else count + 1

    # Override
    def extract(self) -> Union[List, Dict]:
        array = self.__data
        self.__data = []
        return array


# TODO: temporary function, remove it after too many users online
async def _notify_masters(sender: ID, online: bool, remote_address: Tuple[str, int], when: DateTime):
    emitter = _get_emitter()
    user = await emitter.facebook.current_user
    assert user is not None, 'failed to get current user'
    srv = await _get_nickname(identifier=user.identifier)
    # get sender's name
    name = await _get_nickname(identifier=sender)
    if online:
        title = 'Activity: Online (%s)' % when
        relay = await _get_relay(identifier=sender)
        extra = await _get_extra(identifier=sender)
        text = '%s: "%s" is online, socket %s, relay %s; %s' % (srv, name, remote_address, relay, extra)
    else:
        title = 'Activity: Offline (%s)' % when
        text = '%s: "%s" is offline, socket %s' % (srv, name, remote_address)
    # TODO: get masters from config.ini ?
    masters = ID.convert(array=[
        '0x952718A18C6b21abb593D84203282fe1c21773D6',
        '0x9527cFD9b6a0736d8417354088A4fC6e345E31F8',
    ])
    Log.warning(msg='notify masters %s: %s' % (masters, text))
    if len(masters) == 0:
        return False
    # center = PushCenter()
    # keeper = center.badge_keeper
    items = []
    for receiver in masters:
        badge = -1  # keeper.increase_badge(identifier=receiver)
        items.append(PushItem.create(receiver=receiver, title=title, content=text, badge=badge))
    # send to apns bot
    bot = AnsCommandProcessor.ans_id(name='announcer')
    if bot is None:
        Log.error(msg='apns bot not found')
        return
    content = PushCommand(items=items)
    await emitter.send_content(content=content, receiver=bot)
    Log.info(msg='push %d items to: %s' % (len(items), bot))


async def _get_nickname(identifier: ID) -> Optional[str]:
    emitter = _get_emitter()
    if emitter is None:
        Log.error(msg='emitter not found')
        return None
    facebook = emitter.facebook
    if facebook is None:
        Log.warning(msg='facebook not found')
        return None
    name = None
    doc = await facebook.get_document(identifier=identifier)
    if doc is not None:
        name = doc.name
    if name is None or len(name) == 0:
        return str(identifier)
    else:
        return name


async def _get_relay(identifier: ID) -> Optional[str]:
    db = _get_session_database()
    cmd, _ = await db.get_login_command_message(user=identifier)
    if cmd is None:
        Log.warning(msg='login command not found: %s' % identifier)
        return None
    station = cmd.get('station')
    if isinstance(station, Dict):
        host = station.get('host')
        port = station.get('port')
        return '%s:%s' % (host, port)


async def _get_extra(identifier: ID) -> Optional[str]:
    emitter = _get_emitter()
    if emitter is None:
        Log.error(msg='emitter not found')
        return None
    facebook = emitter.facebook
    if facebook is None:
        Log.warning(msg='facebook not found')
        return None
    doc = await facebook.get_document(identifier=identifier)
    if doc is not None:
        # check app.language
        app = doc.get_property(name='app')
        if isinstance(app, Dict):
            language = app.get('language')
            version = app.get('version')
        else:
            language = None
            version = None
        # check sys.*
        sys = doc.get_property(name='sys')
        if isinstance(sys, Dict):
            locale = sys.get('locale')
            model = sys.get('model')
            os = sys.get('os')
        else:
            locale = None
            model = None
            os = None
        # check language
        if language is None:
            language = locale
        elif locale is not None:
            language = '%s(%s)' % (language, locale)
        # check device info
        if model is None:
            device = os
        elif os is None:
            device = model
        else:
            device = '%s(%s)' % (model, os)
        # OK
        return '%s; %s, %s' % (language, device, version)


def _get_emitter() -> Optional[ServerEmitter]:
    monitor = Monitor()
    return monitor.emitter


def _get_session_database() -> Optional[SessionDBI]:
    emitter = _get_emitter()
    if emitter is not None:
        messenger = emitter.messenger
        if messenger is not None:
            session = messenger.session
            if session is not None:
                db = session.database
                if db is not None:
                    return db
                Log.warning(msg='session db not found')
            Log.warning(msg='session not found')
            db = messenger.database
            if isinstance(db, SessionDBI):
                return db
        Log.warning(msg='messenger not found')
        facebook = emitter.facebook
        if facebook is not None:
            db = facebook.barrack.database
            if isinstance(db, SessionDBI):
                return db
        Log.warning(msg='facebook not found')
    # FIXME: get from global variable?
    Log.error(msg='emitter not found')
