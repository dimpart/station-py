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

from dimples import DocumentType
from dimples import ID, Document, DocumentUtils
from dimples import DocumentDBI
from dimples.utils import Config
from dimples.database import DbTask, DataCache

from .redis import DocumentCache
from .dos import DocumentStorage


class DocTask(DbTask[ID, List[Document]]):

    def __init__(self, identifier: ID,
                 redis: DocumentCache, storage: DocumentStorage,
                 mutex_lock: threading.Lock, cache_pool: CachePool):
        super().__init__(mutex_lock=mutex_lock, cache_pool=cache_pool)
        self._identifier = identifier
        self._redis = redis
        self._dos = storage

    @property  # Override
    def cache_key(self) -> ID:
        return self._identifier

    # Override
    async def _read_data(self) -> Optional[List[Document]]:
        # 1. get from redis server
        docs = await self._redis.load_documents(identifier=self._identifier)
        if docs is not None and len(docs) > 0:
            return docs
        # 2. get from local storage
        docs = await self._dos.load_documents(identifier=self._identifier)
        if docs is not None and len(docs) > 0:
            # 3. update redis server
            await self._redis.save_documents(documents=docs, identifier=self._identifier)
            return docs

    # Override
    async def _write_data(self, value: List[Document]) -> bool:
        # 1. store into redis server
        ok1 = await self._redis.save_documents(documents=value, identifier=self._identifier)
        # 2. save into local storage
        ok2 = await self._dos.save_documents(documents=value, identifier=self._identifier)
        return ok1 or ok2


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

    def _new_doc_task(self, identifier: ID) -> DocTask:
        return DocTask(identifier=identifier,
                       redis=self._redis, storage=self._dos,
                       mutex_lock=self._mutex_lock, cache_pool=self._cache_pool)

    def _new_scan_task(self) -> ScanTask:
        return ScanTask(storage=self._dos,
                        mutex_lock=self._mutex_lock, cache_pool=self._cache_pool)

    #
    #   Document DBI
    #

    # Override
    async def save_document(self, document: Document) -> bool:
        assert document.valid, 'document invalid: %s' % document
        identifier = document.identifier
        doc_type = DocumentUtils.get_document_type(document=document)
        #
        #  check old documents
        #
        my_documents = await self.get_documents(identifier=identifier)
        old = DocumentUtils.last_document(my_documents, doc_type)
        if old is None and doc_type == DocumentType.VISA:
            old = DocumentUtils.last_document(my_documents, 'profile')
        if old is not None:
            if DocumentUtils.is_expired(document, old):
                # self.warning(msg='drop expired document: %s' % identifier)
                return False
            my_documents.remove(old)
        my_documents.append(document)
        # update cache for Search Engine
        with self.lock:
            all_documents, _ = self.cache.fetch(key=ScanTask.ALL_KEY)
            if all_documents is not None:
                assert isinstance(all_documents, List), 'all_documents error: %s' % all_documents
                all_documents.append(document)
        #
        #  build task for saving
        #
        task = self._new_doc_task(identifier=identifier)
        return await task.save(value=my_documents)

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
