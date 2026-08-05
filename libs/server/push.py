# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
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

"""
    Push Notification service
    ~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import time
from typing import Optional, Tuple, List

from dimples import ID, ContentType, Envelope, ReliableMessage
from dimples import MessageUtils
from dimples.server import PushService, BadgeKeeper

from ..utils import Logging, Singleton
from ..utils.localizations import Translations, Locale
from ..common import CommonFacebook
from ..common.protocol import PushCommand, PushItem

from .cpu import AnsCommandProcessor

from .filters import FilterManager
from .emitter import ServerEmitter
from .push_intl import PushTmpl


class DefaultPushService(PushService, Logging):

    MESSAGE_EXPIRES = 128

    def __init__(self, facebook: CommonFacebook, emitter: ServerEmitter):
        super().__init__()
        self.__facebook = facebook
        self.__emitter = emitter
        self.__bot: Optional[ID] = None

    @property
    def bot(self) -> Optional[ID]:
        receiver = self.__bot
        if receiver is None:
            receiver = AnsCommandProcessor.ans_id(name='announcer')
            self.__bot = receiver
        return receiver

    async def _get_image(self, identifier: ID) -> Optional[str]:
        if identifier.is_group:
            # TODO: build group image
            return None
        facebook = self.__facebook
        visa = await facebook.get_visa(user=identifier)
        if visa is None:
            return None
        avatar = visa.avatar
        if avatar is None:
            return None
        url = avatar.url
        if url is None or url.find('://') < 0:
            return None
        return url

    # Override
    async def process(self, messages: List[ReliableMessage], badge_keeper: BadgeKeeper) -> bool:
        try:
            bot = self.bot
            if bot is None:
                self.warning(msg='apns bot not set')
                return False
            facebook = self.__facebook
            current_user = await facebook.current_user
            mute_filter = FilterManager().mute_filter
            expired = time.time() - self.MESSAGE_EXPIRES
            items = []
            for msg in messages:
                if msg.time < expired:
                    env = self._origin_envelope(msg=msg)
                    self.warning(msg='drop expired message: %s -> %s (group: %s) type: %s'
                                     % (env.sender, msg.receiver, env.group, env.type))
                    continue
                if await mute_filter.is_muted(msg=msg):
                    env = self._origin_envelope(msg=msg)
                    self.info(msg='muted sender: %s -> %s (group: %s) type: %s'
                                  % (env.sender, msg.receiver, env.group, env.type))
                    continue
                # build push item for message
                pi = await self.__build_push_item(msg=msg, badge_keeper=badge_keeper)
                if pi is not None:
                    items.append(pi)
            if len(items) > 0:
                # push items to the bot
                bot = self.bot
                if bot is not None:
                    content = PushCommand(items=items)
                    if current_user is not None:
                        content['MTA'] = str(current_user.identifier)
                    emitter = self.__emitter
                    await emitter.send_content(content=content, receiver=bot)
        except Exception as error:
            self.error(msg='push %d messages error: %s' % (len(messages), error))
        return True

    async def __build_push_item(self, msg: ReliableMessage, badge_keeper: BadgeKeeper) -> Optional[PushItem]:
        # 1. check original sender, group & msg type
        env = self._origin_envelope(msg=msg)
        sender = MessageUtils.real_sender(msg=msg)
        receiver = MessageUtils.real_receiver(msg=msg)
        group = env.group
        if group is None and 'GF' in env:
            group = ID.parse(identifier='Hidden@anywhere')
        msg_type = env.type
        # 2. build title & content text
        title, text = await self._build_message(sender=sender, receiver=receiver, group=group, msg_type=msg_type)
        if text is None:
            self.info(msg='ignore msg type: %s -> %s (group: %s) type: %s' % (sender, receiver, group, msg_type))
            return None
        # 3. increase badge
        badge = badge_keeper.increase_badge(identifier=receiver)
        # 4. get avatar
        avatar = await self._get_image(identifier=sender)
        # OK
        return PushItem.create(receiver=receiver, title=title, content=text, image=avatar, badge=badge)

    # noinspection PyMethodMayBeStatic
    def _origin_envelope(self, msg: ReliableMessage) -> Envelope:
        """ get envelope of original message """
        origin = msg.get('origin')
        if origin is None:
            env = msg.envelope
        else:
            # forwarded message, separated by group assistant?
            env = Envelope.parse(envelope=origin)
            msg.pop('origin', None)
        return env

    async def _build_message(self, sender: ID, receiver: ID,
                             group: ID, msg_type: str) -> Tuple[Optional[str], Optional[str]]:
        """ build title, content for notification """
        # get title, body template
        title, body = s_push_map.get(msg_type=msg_type, group=group)
        if title is None or body is None:
            # not found
            return None, None
        # get language
        facebook = self.__facebook
        visa = await facebook.get_visa(user=receiver)
        if visa is None:
            language = 'en'
        else:
            language = Locale.from_visa(visa=visa)
            if language is None:
                language = 'en'
        translates = Translations.get(locale=language)
        if translates is None:
            assert language != 'en', 'failed to get translations for language: %s' % language
            translates = Translations.get(locale='en')
            assert translates is not None, 'default translation not set'
        # do translate
        from_name = await facebook.get_name(identifier=sender)
        to_name = await facebook.get_name(identifier=receiver)
        params = {
            'sender': from_name,
            'receiver': to_name,
        }
        if group is not None:
            params['group'] = await facebook.get_name(identifier=group)
        return title, translates.translate(text=body, params=params)


@Singleton
class _PushMap:

    def __init__(self):
        super().__init__()
        self.__title_map = {}
        self.__body_map = {}
        self.__grp_map = {}
        self.load()

    def load(self):
        self.set(ContentType.TEXT, 'text', 'Text Message', PushTmpl.recv_text, PushTmpl.grp_recv_text)
        # file
        self.set(ContentType.FILE, 'file', 'File', PushTmpl.recv_file, PushTmpl.grp_recv_file)
        self.set(ContentType.IMAGE, 'image', 'Image', PushTmpl.recv_image, PushTmpl.grp_recv_image)
        self.set(ContentType.AUDIO, 'audio', 'Voice', PushTmpl.recv_voice, PushTmpl.grp_recv_voice)
        self.set(ContentType.VIDEO, 'video', 'Video', PushTmpl.recv_video, PushTmpl.grp_recv_video)
        # web page
        self.set(ContentType.PAGE, 'page', 'Web Page', PushTmpl.recv_page, PushTmpl.grp_recv_page)
        # name card
        self.set(ContentType.NAME_CARD, 'card', 'Name Card', PushTmpl.recv_card, PushTmpl.grp_recv_card)
        # money
        self.set(ContentType.MONEY, 'money', 'Money', PushTmpl.recv_money, PushTmpl.grp_recv_money)
        self.set(ContentType.TRANSFER, 'transfer', 'Money', PushTmpl.recv_money, PushTmpl.grp_recv_money)
        # forward
        self.set(ContentType.COMBINE_FORWARD, 'combine',
                 'Chat History', PushTmpl.recv_combine, PushTmpl.grp_recv_combine)

    def set(self, msg_type: str, alias: str, title: str, body: str, grp_body: str):
        # set title
        self.__title_map[msg_type] = title
        self.__title_map[alias] = title
        # set body
        self.__body_map[msg_type] = body
        self.__body_map[alias] = body
        # set group body
        self.__grp_map[msg_type] = grp_body
        self.__grp_map[alias] = grp_body

    def get(self, msg_type, group: Optional[ID]) -> Tuple[Optional[str], Optional[str]]:
        """ get title & body for message type """
        title = self.__title_map.get(msg_type)
        if group is None:
            body = self.__body_map.get(msg_type)
        else:
            body = self.__grp_map.get(msg_type)
        # check the results
        if title is None or body is None:
            if msg_type in [ContentType.COMMAND, ContentType.HISTORY, 'command', 'history']:
                # ignore commands
                return None, None
            elif msg_type in [ContentType.ARRAY, ContentType.FORWARD, 'array', 'forward']:
                # ignore packages
                return None, None
            # any type
            title = 'Message'
            body = PushTmpl.recv_message if group is None else PushTmpl.grp_recv_message
        # OK
        return title, body


s_push_map = _PushMap()
