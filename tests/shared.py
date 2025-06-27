# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2022 Albert Moky
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

from typing import Optional

from dimples import ID
from dimples import Document
from dimples import Station
from dimples.common import AccountDBI, MessageDBI, SessionDBI
from dimples.group import SharedGroupManager
from dimples.client import ClientChecker

from libs.utils import Singleton, Log
from libs.utils import Config
from libs.common import ExtensionLoader
from libs.common import CommonFacebook
from libs.database import Database
from libs.client import ClientArchivist, ClientFacebook
from libs.client import ClientSession, ClientMessenger, ClientProcessor, ClientPacker


@Singleton
class GlobalVariable:

    def __init__(self):
        super().__init__()
        self.__config: Optional[Config] = None
        self.__adb: Optional[AccountDBI] = None
        self.__mdb: Optional[MessageDBI] = None
        self.__sdb: Optional[SessionDBI] = None
        self.__database: Optional[Database] = None
        self.__facebook: Optional[ClientFacebook] = None
        self.__messenger: Optional[ClientMessenger] = None
        # load extensions
        ExtensionLoader().run()

    @property
    def config(self) -> Config:
        return self.__config

    @property
    def adb(self) -> AccountDBI:
        return self.__adb

    @property
    def mdb(self) -> MessageDBI:
        return self.__mdb

    @property
    def sdb(self) -> SessionDBI:
        return self.__sdb

    @property
    def database(self) -> Database:
        return self.__database

    @property
    def facebook(self) -> ClientFacebook:
        return self.__facebook

    @property
    def messenger(self) -> ClientMessenger:
        return self.__messenger

    @messenger.setter
    def messenger(self, transceiver: ClientMessenger):
        self.__messenger = transceiver
        # set for group manager
        man = SharedGroupManager()
        man.messenger = transceiver
        # set for entity checker
        checker = self.facebook.checker
        assert isinstance(checker, ClientChecker), 'entity checker error: %s' % checker
        checker.messenger = transceiver

    async def prepare(self, config: Config):
        self.__config = config
        #
        #  Step 1: create database
        #
        database = await create_database(config=config)
        self.__adb = database
        self.__mdb = database
        self.__sdb = database
        self.__database = database
        #
        #  Step 2: create facebook
        #
        facebook = await create_facebook(database=database)
        self.__facebook = facebook

    async def login(self, current_user: ID):
        facebook = self.facebook
        # make sure private keys exists
        sign_key = await facebook.private_key_for_visa_signature(identifier=current_user)
        msg_keys = await facebook.private_keys_for_decryption(identifier=current_user)
        assert sign_key is not None, 'failed to get sign key for current user: %s' % current_user
        assert len(msg_keys) > 0, 'failed to get msg keys: %s' % current_user
        Log.info(msg='set current user: %s' % current_user)
        user = await facebook.get_user(identifier=current_user)
        assert user is not None, 'failed to get current user: %s' % current_user
        visa = await user.visa
        if visa is not None:
            # refresh visa
            visa = Document.parse(document=visa.copy_dictionary())
            visa.sign(private_key=sign_key)
            await facebook.save_document(document=visa)
        await facebook.set_current_user(user=user)


async def create_database(config: Config) -> Database:
    """ create database with directories """
    db = Database(config=config)
    db.show_info()
    return db


async def create_facebook(database: AccountDBI) -> ClientFacebook:
    """ create facebook """
    facebook = ClientFacebook(database=database)
    facebook.barrack = ClientArchivist(facebook=facebook, database=database)
    facebook.checker = ClientChecker(facebook=facebook, database=database)
    # set for group manager
    man = SharedGroupManager()
    man.facebook = facebook
    return facebook


async def create_messenger(shared: GlobalVariable, facebook: CommonFacebook) -> ClientMessenger:
    """ create messenger and connect to station (host:port) """
    config = shared.config
    host = config.station_host
    port = config.station_port
    user = await facebook.current_user
    # 1. create station with remote host & port
    station = Station(host=host, port=port)
    station.data_source = facebook
    # 2. create session with SessionDB
    session = ClientSession(station=station, database=shared.sdb)
    session.set_identifier(identifier=user.identifier)
    # 3. create messenger with session and MessageDB
    messenger = ClientMessenger(session=session, facebook=facebook, database=shared.mdb)
    # 4. create packer, processor for messenger
    #    they have weak references to facebook & messenger
    messenger.packer = ClientPacker(facebook=facebook, messenger=messenger)
    messenger.processor = ClientProcessor(facebook=facebook, messenger=messenger)
    # 5. set weak reference to messenger
    session.messenger = messenger
    return messenger
