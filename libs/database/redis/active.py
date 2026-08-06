# -*- coding: utf-8 -*-
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

from typing import Optional, Set, Tuple

from dimples import ID
from dimples import RedisCache

from ...utils import json_encode, json_decode, utf8_encode, utf8_decode


class ActiveCache(RedisCache):

    @property  # Override
    def db_name(self) -> Optional[str]:
        return 'mkm'

    @property  # Override
    def tbl_name(self) -> str:
        return 'user'

    """
        Session Online
        ~~~~~~~~~~~~~~

        redis key: 'mkm.user.active_sockets'
    """
    def __active_sockets_cache_name(self) -> str:
        return '%s.%s.active_sockets' % (self.db_name, self.tbl_name)

    async def clear_socket_addresses(self) -> bool:
        """ clear before station start """
        name = self.__active_sockets_cache_name()
        all_keys = await self.hkeys(name=name)
        for key in all_keys:
            await self.hdel(name=name, key=key)
        return await self.delete(name)

    async def save_socket_addresses(self, user: ID, addresses: Set[Tuple[str, int]]) -> bool:
        name = self.__active_sockets_cache_name()
        value = serialize_socket_addresses(addresses=addresses)
        if value is None:
            return await self.hdel(name=name, key=str(user))
        else:
            return await self.hset(name=name, key=str(user), value=value)

    # async def load_socket_addresses(self, user: ID) -> Set[Tuple[str, int]]:
    #     name = self.__active_sockets_cache_name()
    #     value = await self.hget(name=name, key=str(user))
    #     if is_empty(value=value):
    #         return set()
    #     return deserialize_socket_addresses(value=value)
    #
    # async def all_users(self) -> Set[ID]:
    #     name = self.__active_sockets_cache_name()
    #     all_keys = await self.hkeys(name=name)
    #     users = set()
    #     for key in all_keys:
    #         did = ID.parse(identifier=key)
    #         if did is not None:
    #             did = did.without_terminal()
    #             users.add(did)
    #     return users

    async def load_active_users(self) -> Set[ID]:
        name = self.__active_sockets_cache_name()
        records = await self.hgetall(name=name)  # ID => Set[socket_address]
        if records is None:
            return set()
        users = set()
        for key, value in records.items():
            if is_empty(value=value):
                # user logout
                continue
            string = utf8_decode(data=key)
            did = ID.parse(identifier=string)
            if did is not None:
                did = did.without_terminal()
                users.add(did)
        return users


"""
    JsON format: [
        [host, port],
        [host, port],
        [host, port]
    ]
"""


def serialize_socket_addresses(addresses: Set[Tuple[str, int]]) -> Optional[bytes]:
    if addresses is None or len(addresses) == 0:
        return None
    array = []
    for add in addresses:
        # item = [add[0], add[1]]
        item = list(add)
        array.append(item)
    js = json_encode(container=array)
    return utf8_encode(string=js)


def deserialize_socket_addresses(value: bytes) -> Set[Tuple[str, int]]:
    js = utf8_decode(data=value)
    array = json_decode(string=js)
    all_addresses = set()
    for item in array:
        # address = (item[0], item[1])
        address = tuple(item)
        all_addresses.add(address)
    return all_addresses


min_len = len('[["8.8.8.8",8]]')


def is_empty(value: bytes) -> bool:
    return value is None or len(value) <= 2  # < min_len
