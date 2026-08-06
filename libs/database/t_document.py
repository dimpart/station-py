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

import threading
from typing import Optional, List

from aiou.mem import CachePool

from dimples import ID
from dimples import Document
from dimples import DocumentUtils
from dimples import DocumentDBI
from dimples.utils import Config
from dimples.database import DbTask, DataCache
from dimples.database.t_document import DocTask

from .redis import DocumentCache
from .dos import DocumentStorage


class ScanTask(DbTask[ID, List[Document]]):

    ALL_KEY = 'all_documents'

    MEM_CACHE_EXPIRES = 3600  # seconds
    MEM_CACHE_REFRESH = 600   # seconds

    def __init__(self, storage: DocumentStorage,
                 mutex_lock: threading.Lock, cache_pool: CachePool):
        super().__init__(mutex_lock=mutex_lock, cache_pool=cache_pool,
                         cache_expires=self.MEM_CACHE_EXPIRES,
                         cache_refresh=self.MEM_CACHE_REFRESH)
        self._dos = storage

    @property  # Override
    def cache_key(self) -> str:
        return self.ALL_KEY

    # Override
    async def _read_data(self) -> Optional[List[Document]]:
        return await self._dos.scan_documents()

    # Override
    async def _write_data(self, value: List[Document]) -> bool:
        pass


class DocumentTable(DataCache, DocumentDBI):
    """ Implementations of DocumentDBI """

    def __init__(self, config: Config):
        super().__init__(pool_name='documents')  # ID => List[Document]
        self._redis = DocumentCache(config=config)
        self._dos = DocumentStorage(config=config)

    def show_info(self):
        self._dos.show_info()

    def _new_doc_task(self, identifier: ID, new_document: Document = None) -> DocTask:
        assert identifier.terminal is None, f'not a naked id: {identifier}'
        # create task with naked id
        return DocTask(identifier=identifier, new_document=new_document,
                       redis=self._redis, storage=self._dos,
                       mutex_lock=self._mutex_lock, cache_pool=self._cache_pool)

    def _new_scan_task(self) -> ScanTask:
        return ScanTask(storage=self._dos,
                        mutex_lock=self._mutex_lock, cache_pool=self._cache_pool)

    #
    #   Document DBI
    #

    # Override
    async def save_document(self, document: Document, identifier: ID) -> bool:
        #
        #   0. check valid
        #
        did = DocumentUtils.get_document_id(document=document)
        if not identifier.is_same_as(other=did):
            self.error('document id not matched: %s, %s', did, identifier)
            return False
        elif not document.is_valid:
            self.error('document not valid: %s', identifier)
            return False
        #
        #   1. load old records
        #
        task = self._new_doc_task(identifier=identifier)
        docs = await task.load()
        if docs is None:
            docs = []
        #
        #   2. save new record
        #
        task = self._new_doc_task(identifier=identifier, new_document=document)
        return await task.save(docs)

    # Override
    async def get_documents(self, identifier: ID) -> List[Document]:
        #
        #  build task for loading
        #
        task = self._new_doc_task(identifier=identifier)
        docs = await task.load()
        return [] if docs is None else docs

    async def scan_documents(self) -> List[Document]:
        """ Scan all documents from data directory """
        task = self._new_scan_task()
        docs = await task.load()
        return [] if docs is None else docs
