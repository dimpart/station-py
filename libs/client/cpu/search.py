# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2019 Albert Moky
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
    Command Processor for online users
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import List

from dimples import DateTime
from dimples import ID
from dimples import ReliableMessage
from dimples import Content

from dimples import BaseCommandProcessor
from dimples.common import CommonFacebook
from dimples.utils import SharedCacheManager

from ...utils import Logging
from ...common.protocol import SearchCommand
from ...database import Database
from ...database.t_active import ActiveTable


class SearchCommandProcessor(BaseCommandProcessor, Logging):

    @property
    def facebook(self) -> CommonFacebook:
        barrack = super().facebook
        assert isinstance(barrack, CommonFacebook), 'facebook error: %s' % barrack
        return barrack

    # Override
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, SearchCommand), 'search command error: %s' % content
        if content.users is not None:
            # this is a response
            return await save_response(self.facebook, station=r_msg.sender, users=content.users)
        # this is a request
        facebook = self.facebook
        keywords = content.keywords
        if keywords is None:
            text = 'Search command error.'
            return self._respond_receipt(text=text, content=content, envelope=r_msg.envelope, extra={})
        elif keywords == SearchCommand.ONLINE_USERS:
            users = await online_users(start=content.start, limit=content.limit, facebook=facebook)
            self.info('Got %d recent online user(s)' % len(users))
        else:
            db = facebook.barrack.database
            assert isinstance(db, Database), 'database error: %s' % db
            users = await search_users(keywords=keywords, start=content.start, limit=content.limit,
                                       database=db, facebook=facebook)
            self.info('Got %d account(s) matched %s' % (len(users), keywords))
        res = SearchCommand.respond(request=content, keywords=keywords, users=users)
        station = await facebook.current_user
        res.station = station.identifier
        return [res]


#
#   Caches
#
ActiveTable.CACHE_REFRESHING = 2
ActiveTable.CACHE_EXPIRES = 8

g_search_cache = None


async def online_users(start: int, limit: int, facebook: CommonFacebook) -> List[ID]:
    assert start >= 0, 'start position error: %d' % start
    if limit > 0:
        end = start + limit
    elif limit == 0:
        end = start + 100
    else:
        # this is a request from another search bot in neighbor station
        end = start + 10240
    # check all users in session center
    db = facebook.barrack.database
    assert isinstance(db, Database), 'database error: %s' % db
    active_users = await db.get_active_users()
    index = -1
    users = []
    for item in active_users:
        index += 1
        if index < start:
            # skip
            continue
        elif index >= end:
            # mission accomplished
            break
        # got it
        users.append(item)
    return users


async def search_users(keywords: str, start: int, limit: int,
                       database: Database, facebook: CommonFacebook) -> List[ID]:
    global g_search_cache
    if g_search_cache is None:
        g_search_cache = SharedCacheManager().get_pool(name='search')
    # 0. split keywords
    if keywords is None:
        kw_array = []
    else:
        kw_array = keywords.split(' ')
    assert start >= 0, 'start position error: %d' % start
    if limit > 0:
        end = start + limit
    elif limit == 0:
        end = start + 50
    else:
        # this is a request from another search bot in neighbor station
        end = start + 10240
    # 1. get from cache
    now = DateTime.now()
    value, holder = g_search_cache.fetch(key=(keywords, start, end), now=now)
    if value is not None:
        # got it
        return value
    elif holder is not None:
        # search result expired, wait to reload
        holder.renewal(duration=8, now=now)
    # 2. do searching
    index = -1
    users = []
    all_documents = await database.scan_documents()
    for doc in all_documents:
        # check duplicated
        identifier = doc.identifier
        if identifier in users:
            # already exists
            continue
        # get user info
        name = doc.name
        if name is None:
            info = str(identifier)
        else:
            info = '%s, %s' % (name, identifier)
        info = info.lower()
        # 2.1. check each keyword with user info
        match = True
        for kw in kw_array:
            if len(kw) > 0 > info.find(kw.lower()):
                match = False
                break
        if not match:
            continue
        # 2.2. check user meta
        meta = await facebook.get_meta(identifier=identifier)
        if meta is None:
            # user meta not found, skip
            continue
        # 2.3. check limit
        index += 1
        if index < start:
            # skip
            continue
        elif index >= end:
            # mission accomplished
            break
        # got it
        users.append(identifier)
    # 3. cache the search result
    g_search_cache.update(key=(keywords, start, end), value=users, life_span=600, now=now)
    return users


# noinspection PyUnusedLocal
async def save_response(facebook: CommonFacebook, station: ID, users: List[ID]) -> List[Content]:
    # TODO: Save online users in a text file
    # # store in redis server
    # for item in users:
    #     facebook.add_online_user(station=station, user=item)
    # # clear expired users
    # facebook.remove_offline_users(station=station, users=[])
    return []
