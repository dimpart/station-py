# -*- coding: utf-8 -*-
#
#   DIMP : Decentralized Instant Messaging Protocol
#
#                                Written in 2023 by Moky <albert.moky@gmail.com>
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
    APNs Protocol
    ~~~~~~~~~~~~~

    Application (Apple/Android) Push Notification service

    Push Item: {

        "receiver" : "{ID}",

        "aps"      : {
            "title"    : "{TITLE}",   // alert.title (OPTIONAL)
            "content"  : "{CONTENT},  // alert.body  (OPTIONAL)
            "sound"    : "{URL}",
            "badge"    : 0,
            "category" : "{CATEGORY}",
            "alert"    : {
                "title"    : "{TITLE}",
                "subtitle" : "{SUBTITLE}",
                "body"     : "{CONTENT}",
                "image"    : "{URL}"
            }
        }
    }
"""

from typing import Optional, Any, List, Dict

from dimples import Dictionary
from dimples import ID, BaseCommand


class PushAlert(Dictionary):
    """
        Alert
        ~~~~~

        "alert" : {
            "title"    : "{TITLE}",
            "subtitle" : "{SUBTITLE}",
            "body"     : "{CONTENT}",
            "image"    : "{URL}"
        }
    """

    @property
    def title(self) -> Optional[str]:
        return self.get_str(key='title', default=None)

    @property
    def subtitle(self) -> Optional[str]:
        return self.get_str(key='subtitle', default=None)

    @property
    def body(self) -> str:
        return self.get_str(key='body', default='')

    @property
    def image(self) -> Optional[str]:
        return self.get_str(key='image', default=None)

    #
    #   Factory methods
    #

    @classmethod
    def create(cls, body: str, title: str = None, subtitle: str = None, image: str = None):  # -> PushAlert:
        alert = {
            'body': body,
        }
        if title is not None:
            alert['title'] = title
        if subtitle is not None:
            alert['subtitle'] = subtitle
        if image is not None:
            alert['image'] = image
        return cls(dictionary=alert)

    @classmethod
    def parse(cls, alert: Any):  # -> Optional[PushAlert]:
        if alert is None:
            return None
        elif isinstance(alert, PushAlert):
            return alert
        assert isinstance(alert, Dict), 'push alert error: %s' % alert
        body = alert.get('body')
        if isinstance(body, str):
            return cls(dictionary=alert)


class PushInfo(Dictionary):
    """
        Push Info
        ~~~~~~~~~

        "aps" : {
            "alert"    : {
                // ...
            },
            "title"    : "{TITLE}",   // alert.title
            "content"  : "{CONTENT},  // alert.body
            "sound"    : "{URL}",
            "badge"    : 0,
            "category" : "{CATEGORY}"
        }
    """

    def __init__(self, dictionary: Dict):
        super().__init__(dictionary=dictionary)
        self.__alert: Optional[PushAlert] = None

    @property
    def alert(self) -> Optional[PushAlert]:
        pa = self.__alert
        if pa is None:
            pa = PushAlert.parse(alert=self.get('alert'))
            self.__alert = pa
        return pa

    @property
    def title(self) -> Optional[str]:
        alert = self.alert
        if alert is not None:
            text = alert.title
            if text is not None:
                return text
        return self.get_str(key='title', default=None)

    @property
    def content(self) -> str:
        alert = self.alert
        if alert is not None:
            return alert.body
        return self.get_str(key='content', default='')

    @property
    def image(self) -> Optional[str]:
        alert = self.alert
        if alert is not None:
            return alert.image

    @property
    def sound(self) -> Optional[str]:
        return self.get_str(key='sound', default=None)

    @property
    def badge(self) -> int:
        return self.get_int(key='badge', default=0)

    @property
    def category(self) -> Optional[str]:
        return self.get_str(key='category', default=None)

    #
    #   Factory methods
    #

    @classmethod
    def create(cls, alert: PushAlert, sound: str = None, badge: int = 0, category: str = None):  # -> PushInfo:
        info = {
            'alert': alert.dictionary,
        }
        if sound is not None:
            info['sound'] = sound
        if badge is not None:
            info['badge'] = badge
        if category is not None:
            info['category'] = category
        return cls(dictionary=info)

    @classmethod
    def parse(cls, info: Any):  # -> Optional[PushInfo]:
        if info is None:
            return None
        elif isinstance(info, PushInfo):
            return info
        assert isinstance(info, Dict), 'push info error: %s' % info
        alert = info.get('alert')
        if isinstance(alert, Dict):
            return cls(dictionary=info)
        content = info.get('content')
        if isinstance(content, str):
            return cls(dictionary=info)


class PushItem(Dictionary):
    """
        Push Item
        ~~~~~~~~~

        item: {
            "receiver" : "{ID}",
            "aps" : {
                // ...
            }
        }
    """

    def __init__(self, dictionary: Dict, receiver: ID = None, aps: PushInfo = None):
        super().__init__(dictionary=dictionary)
        self.__receiver = receiver
        self.__aps = aps

    @property
    def receiver(self) -> ID:
        identifier = self.__receiver
        if identifier is None:
            string = self.get(key='receiver')
            identifier = ID.parse(identifier=string)
            assert identifier is not None, 'receiver error: %s' % string
            self.__receiver = identifier
        return identifier

    @property
    def info(self) -> PushInfo:
        aps = self.__aps
        if aps is None:
            dictionary = self.get(key='aps')
            if dictionary is None:
                dictionary = self.dictionary
            aps = PushInfo.parse(info=dictionary)
            assert aps is not None, 'push info error: %s' % dictionary
            self.__aps = aps
        return aps

    #
    #   Factory methods
    #

    @classmethod
    def create(cls, receiver: ID, title: Optional[str], content: str,
               image: str = None, sound: str = None, badge: int = 0):  # -> PushItem:
        alert = PushAlert.create(title=title, body=content, image=image)
        aps = PushInfo.create(alert=alert, sound=sound, badge=badge)
        item = {
            'receiver': str(receiver),
            'aps': aps.dictionary,
        }
        return cls(dictionary=item, receiver=receiver, aps=aps)

    @classmethod
    def parse(cls, item: Any):  # -> Optional[PushItem]:
        if item is None:
            return None
        elif isinstance(item, PushItem):
            return item
        assert isinstance(item, Dict), 'push item error: %s' % item
        receiver = ID.parse(identifier=item.get('receiver'))
        info = item.get('aps')
        if info is None:
            info = item
        aps = PushInfo.parse(info=info)
        if receiver is not None and aps is not None:
            return cls(dictionary=item, receiver=receiver, aps=aps)

    @classmethod
    def convert(cls, array: List[Dict]):  # -> List[PushItem]:
        items = []
        for item in array:
            pi = cls.parse(item=item)
            if pi is not None:
                items.append(pi)
        return items

    @classmethod
    def revert(cls, items: List):  # -> List[Dict]:
        array = []
        for item in items:
            assert isinstance(item, PushItem), 'push item error: %s' % item
            array.append(item.dictionary)
        return array


class PushCommand(BaseCommand):
    """
        Push Notification Command
        ~~~~~~~~~~~~~~~~~~~~~~~~~

        data format: {
            type : 0x88,
            sn   : 123,

            cmd   : "push",
            //-------- Notification Info --------
            items : [
                {Push Item},
                ...
            ]
        }
    """

    PUSH = 'push'

    def __init__(self, content: Dict[str, Any] = None, items: List[PushItem] = None):
        if content is None:
            # create with names
            super().__init__(cmd=PushCommand.PUSH)
            if items is not None:
                self['items'] = PushItem.revert(items=items)
        else:
            # create with command content
            super().__init__(content=content)
        # push items
        self.__items = items

    @property
    def items(self) -> List[PushItem]:
        array = self.__items
        if array is None:
            array = self.get('items')
            if array is None:
                # check for single push item
                single = PushItem.parse(item=self.dictionary)
                if single is not None:
                    array = [single]
            else:
                # convert push items
                array = PushItem.convert(array=array)
            if array is None:
                array = []  # placeholder
            self.__items = array
        return array

    #
    #   Factory methods
    #

    @classmethod
    def create(cls, receiver: ID, title: Optional[str], content: str,
               image: str = None, sound: str = None, badge: int = 0):  # -> PushCommand:
        item = PushItem.create(receiver=receiver, title=title, content=content, image=image, sound=sound, badge=badge)
        return cls(items=[item])
