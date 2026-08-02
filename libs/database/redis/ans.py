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

from typing import Optional, Set

from dimples import utf8_encode, utf8_decode
from dimples import ID
from dimples.database.redis import RedisCache

from ...utils import BytesPairing


class AddressNameCache(RedisCache):

    @property  # Override
    def db_name(self) -> Optional[str]:
        return 'dim'

    @property  # Override
    def tbl_name(self) -> str:
        return 'ans'

    """
        Address Name Service
        ~~~~~~~~~~~~~~~~~~~~

        redis key: 'dim.ans'
    """
    def __cache_name(self) -> str:
        return '%s.%s' % (self.db_name, self.tbl_name)

    async def save_record(self, name: str, identifier: ID):
        value = utf8_encode(string=str(identifier))
        return await self.hset(name=self.__cache_name(), key=name, value=value)

    async def get_record(self, name: str) -> Optional[ID]:
        value = await self.hget(name=self.__cache_name(), key=name)
        if value is not None:
            identifier = utf8_decode(data=value)
            return ID.parse(identifier=identifier)

    async def get_names(self, identifier: ID) -> Set[str]:
        records = await self.hgetall(name=self.__cache_name())
        if records is None:
            return set()
        else:
            return get_names(records=records, identifier=identifier)


def get_names(records: BytesPairing, identifier: ID) -> Set[str]:
    strings = set()
    for key, value in records.items():
        text = utf8_decode(data=value)
        did = ID.parse(identifier=text)
        if did is None:
            assert False, f'ANS ID error: {text}'
        elif did.is_same_as(other=identifier):
            name = utf8_decode(data=key)
            strings.add(name)
    return strings
