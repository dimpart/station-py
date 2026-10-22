# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2024 Albert Moky
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
    Text Content Processor
    ~~~~~~~~~~~~~~~~~~~~~~

    Text commands
"""

import random
import threading
import weakref
from socketserver import StreamRequestHandler
from typing import Optional, Tuple, List, Set

from dimples import ID
from dimples import ReliableMessage
from dimples import Content, TextContent
from dimples import BaseContentProcessor
from dimples.server import SessionCenter, ServerSession

from ...utils import Singleton, Logging


# The text commands below list every connected user, with the IP address and port
# it connects from, so the station answers them only for its operators.
# Override in config.ini with `[admin] ids = ID1, ID2`; an empty value disables them.
DEFAULT_ADMINS = [
    '0x952718A18C6b21abb593D84203282fe1c21773D6',
    '0x9527cFD9b6a0736d8417354088A4fC6e345E31F8',
]
ADMIN_COMMANDS = ('all users', 'active users', 'request handlers')

_admins: Set[str] = set(DEFAULT_ADMINS)


def set_admins(array: List[str]) -> Set[str]:
    """ Replace the IDs allowed to run the text commands (device terminals ignored) """
    _admins.clear()
    _admins.update(str(item).strip().split('/', 1)[0] for item in array if str(item).strip())
    return set(_admins)


def is_admin(identifier: ID) -> bool:
    return str(identifier).split('/', 1)[0] in _admins


class TextContentProcessor(BaseContentProcessor, Logging):
    """
        Text Content Processor
        ~~~~~~~~~~~~~~~~~~~~~~

    """

    # Override
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, TextContent), 'text content error: %s' % content
        text = content.text
        self.info(msg='received text message from %s: "%s"' % (r_msg.sender, text))
        if text is None or len(text) == 0:
            return []
        else:
            text = text.lower()
        if text in ADMIN_COMMANDS and not is_admin(identifier=r_msg.sender):
            self.warning(msg='refused text command "%s" from %s' % (text, r_msg.sender))
            return []
        # text commands
        if text == 'all users':
            return _all_users()
        if text == 'active users':
            return _active_users()
        if text == 'request handlers':
            return _request_handlers()
        # error
        return []


def _all_users() -> List[Content]:
    center = SessionCenter()
    all_users = center.all_users()
    text = '%d users\n' % len(all_users)
    text += '\n----\n'
    for user in all_users:
        text += '- %s\n' % user
    content = TextContent.create(text=text)
    content['format'] = 'markdown'
    return [content]


def _active_users() -> List[Content]:
    center = SessionCenter()
    all_users = center.all_users()
    text = 'Totally %d users\n' % len(all_users)
    text += '\n'
    text += '| ID | Sockets |\n'
    text += '|----|---------|\n'
    count = 0
    for user in all_users:
        active_sessions = center.active_sessions(identifier=user)
        if len(active_sessions) == 0:
            continue
        else:
            count += 1
        text += '| %s |' % user
        for sess in active_sessions:
            text += ' _%s_' % str(sess.remote_address)
        text += ' |\n'
    text += '\n'
    text += '%d active users.' % count
    content = TextContent.create(text=text)
    content['format'] = 'markdown'
    return [content]


def _request_handlers() -> List[Content]:
    marker = RequestHandlerMarker()
    all_handlers = marker.all_handlers
    text = 'Totally %d handlers\n' % len(all_handlers)
    text += '\n'
    text += '| Tag | Sockets | ID |\n'
    text += '|-----|---------|----|\n'
    for info in all_handlers:
        text += '| %d | _%s_ | %s |\n' % (info.tag, info.client_address, info.identifier)
    text += '\n'
    text += '%d request handlers.' % len(all_handlers)
    content = TextContent.create(text=text)
    content['format'] = 'markdown'
    return [content]


class RequestHandlerInfo:

    def __init__(self, tag: int, client_address: Tuple[str, int], identifier: ID):
        super().__init__()
        self.__tag = tag
        self.__client_address = client_address
        self.__identifier = identifier

    @property
    def tag(self) -> int:
        return self.__tag

    @property
    def client_address(self) -> Tuple[str, int]:
        return self.__client_address

    @property
    def identifier(self) -> ID:
        return self.__identifier


@Singleton
class RequestHandlerMarker(Logging):

    def __init__(self):
        super().__init__()
        self.__handlers = set()
        self.__lock = threading.Lock()

    @property
    def all_handlers(self) -> List[RequestHandlerInfo]:
        with self.__lock:
            handlers = []
            array = self.__handlers.copy()
            for ref in array:
                item: StreamRequestHandler = ref()
                if item is None:
                    self.__handlers.remove(ref)
                    continue
                tag = getattr(item, '_cli_req_tag', 0)
                client_address = item.client_address
                identifier = _get_session_id(handler=item)
                info = RequestHandlerInfo(tag=tag, client_address=client_address, identifier=identifier)
                handlers.append(info)
            return handlers

    def setup_handler(self, handler: StreamRequestHandler):
        with self.__lock:
            tag = random.randint(2**30, 2**32 - 1)
            setattr(handler, '_cli_req_tag', tag)
            ref = weakref.ref(handler)
            self.__handlers.add(ref)

    def remove_handler(self, handler: StreamRequestHandler):
        with self.__lock:
            array = self.__handlers.copy()
            for ref in array:
                item = ref()
                if item is None:
                    self.__handlers.remove(ref)
                elif item == handler:
                    self.__handlers.remove(ref)

    # noinspection PyMethodMayBeStatic
    def link_session(self, session: ServerSession, handler: StreamRequestHandler):
        ref = weakref.ref(session)
        setattr(handler, '_session_ref', ref)


def _get_session_id(handler) -> Optional[ID]:
    ref = getattr(handler, '_session_ref')
    if ref is None:
        return None
    session: ServerSession = ref()
    if session is None:
        return None
    else:
        return session.identifier
