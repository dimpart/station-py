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

from dimples import ID, ANYONE, EVERYONE, FOUNDER

from dimples.database.dos import Storage


try:
    import collections.abc as abc
    AnsMap = abc.MutableMapping[str, ID]
except TypeError:
    import typing
    AnsMap = typing.MutableMapping[str, ID]


class AddressNameStorage(Storage):
    """
        Address Name Service
        ~~~~~~~~~~~~~~~~~~~~

        file path: '.dim/protected/ans.js'
    """
    ans_path = '{PROTECTED}/ans.js'

    def show_info(self):
        path = self.protected_path(self.ans_path)
        print('!!!            ans path: %s' % path)

    def __ans_path(self) -> str:
        return self.protected_path(self.ans_path)

    async def load_records(self) -> AnsMap:
        path = self.__ans_path()
        self.info('Loading ANS records from: %s' % path)
        records = {}
        dictionary = await self.read_json(path=path)
        if dictionary is not None:
            assert isinstance(dictionary, dict), f'ANS record error: {dictionary}'
            for name, value in dictionary.items():
                # convert ID
                uid = ID.parse(identifier=value)
                if uid is None:
                    self.error(msg='invalid record: %s => %s' % (name, value))
                    continue
                records[name] = uid
        #
        #  Reserved names
        #
        records['all'] = EVERYONE
        records[EVERYONE.name] = EVERYONE
        records[ANYONE.name] = ANYONE
        records['owner'] = ANYONE
        records['founder'] = FOUNDER  # 'Albert Moky'
        return records

    async def save_records(self, records: AnsMap) -> bool:
        dictionary = {}
        # revert ID
        for name, uid in records.items():
            if uid is None:
                assert False, f'ANS record error: "{name}" => {uid}'
            else:
                dictionary[name] = str(uid)
        path = self.__ans_path()
        self.info('Saving %d ANS records into: %s' % (len(records), path))
        return await self.write_json(container=dictionary, path=path)
