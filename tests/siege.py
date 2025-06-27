#! /usr/bin/env python3
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

"""
    Stress Testing
    ~~~~~~~~~~~~~~

"""

import getopt
import multiprocessing
import sys
import time
from typing import Optional, List

from dimples import AsymmetricAlgorithms
from dimples import MetaType, DocumentType
from dimples import PrivateKey
from dimples import Meta, Document
from dimples import EntityType, ID
from dimples import Station
from dimples.common import SessionDBI

from dimples.utils import Path

path = Path.abs(path=__file__)
path = Path.dir(path=path)
path = Path.dir(path=path)
Path.add(path=path)

from libs.utils import Log, Logging
from libs.utils import Runner
from libs.utils import Config
from libs.database import Storage
from libs.client import Terminal
from libs.client import ClientFacebook
from libs.client import ClientSession, ClientMessenger, ClientProcessor, ClientPacker

from tests.shared import GlobalVariable


class Soldier(Terminal, Logging):

    ATTACK_DURATION = 32

    def __init__(self, facebook: ClientFacebook, database: SessionDBI):
        super().__init__(facebook=facebook, database=database)
        self.__user: Optional[ID] = None

    def __del__(self):
        self.warning(msg='soldier down: %s' % self.user)

    def __str__(self) -> str:
        mod = self.__module__
        cname = self.__class__.__name__
        return '<%s>%s -> %s</%s module="%s">' % (cname, self.user, self.server, cname, mod)

    def __repr__(self) -> str:
        mod = self.__module__
        cname = self.__class__.__name__
        return '<%s>%s -> %s</%s module="%s">' % (cname, self.user, self.server, cname, mod)

    @property
    def user(self) -> Optional[ID]:
        return self.__user

    @user.setter
    def user(self, identifier: ID):
        self.__user = identifier

    @property
    def server(self) -> Optional[Station]:
        session = self.session
        if session is not None:
            return session.station

    # Override
    def _create_packer(self, facebook: ClientFacebook, messenger: ClientMessenger) -> ClientPacker:
        return ClientPacker(facebook=facebook, messenger=messenger)

    # Override
    def _create_processor(self, facebook: ClientFacebook, messenger: ClientMessenger) -> ClientProcessor:
        return ClientProcessor(facebook=facebook, messenger=messenger)

    # Override
    def _create_messenger(self, facebook: ClientFacebook, session: ClientSession) -> ClientMessenger:
        shared = GlobalVariable()
        messenger = ClientMessenger(session=session, facebook=facebook, database=shared.mdb)
        shared.messenger = messenger
        return messenger

    async def attack(self, host: str, port: int):
        user = self.user
        shared = GlobalVariable()
        await shared.login(current_user=user)
        #
        #  connect
        #
        await self.connect(host=host, port=port)
        #
        #  login
        #
        session = self.session
        if session is None:
            assert False, 'session not found'
        else:
            self.info(msg='setting session ID: %s' % user)
            session.set_identifier(identifier=user)
        #
        #  waiting to retreat
        #
        time_to_retreat = time.time() + self.ATTACK_DURATION
        Runner.async_task(coro=self.run())
        while True:
            await Runner.sleep(seconds=1.0)
            if not self.running:
                break
            elif time.time() > time_to_retreat:
                break
        # done
        await self.stop()


class Sergeant(Logging):

    LANDING_POINT = 'normandy'

    HOST = '127.0.0.1'
    PORT = 9394

    UNITS = 10  # threads count

    def __init__(self, client_id: ID, offset: int):
        super().__init__()
        self.__cid = client_id
        self.__offset = offset

    def run(self):
        cid = self.__cid
        shared = GlobalVariable()
        threads = []
        for i in range(self.UNITS):
            self.warning(msg='**** thread starts (%d + %d): %s' % (self.__offset, i, cid))
            soldier = Soldier(facebook=shared.facebook, database=shared.sdb)
            soldier.user = cid
            thr = Runner.async_thread(coro=soldier.attack(host=self.HOST, port=self.PORT))
            thr.start()
            threads.append(thr)
            self.__offset += self.UNITS
        for thr in threads:
            try:
                thr.join()
            except KeyboardInterrupt as error:
                self.error(msg='thread error: %s, %s' % (cid, error))
            self.warning(msg='**** thread stopped: %s' % thr)

    def attack(self) -> multiprocessing.Process:
        proc = multiprocessing.Process(target=self.run)
        proc.daemon = True
        proc.start()
        return proc

    @classmethod
    async def training(cls, sn: int) -> ID:
        """ create new bot """
        seed = 'soldier%03d' % sn
        # 1. generate private key
        pri_key = PrivateKey.generate(algorithm=AsymmetricAlgorithms.RSA)
        # 2. generate meta
        meta = Meta.generate(version=MetaType.MKM, private_key=pri_key, seed=seed)
        # 3. generate ID
        identifier = ID.generate(meta=meta, network=EntityType.BOT)
        Log.info(msg='NewID: %s\n' % identifier)
        # 4. save private key & meta
        shared = GlobalVariable()
        database = shared.adb
        facebook = shared.facebook
        await database.save_private_key(key=pri_key, user=identifier)
        await facebook.save_meta(meta=meta, identifier=identifier)
        # 5. create visa
        visa = Document.create(doc_type=DocumentType.VISA, identifier=identifier)
        visa.name = 'Soldier %03d @%s' % (sn, cls.LANDING_POINT)
        # 6. sign and save visa
        visa.sign(private_key=pri_key)
        await facebook.save_document(document=visa)
        return identifier


class Colonel(Runner, Logging):

    TROOPS = 16  # progresses count

    def __init__(self):
        super().__init__(interval=1.0)
        self.__soldiers: List[ID] = []
        self.__offset = 0

    # Override
    async def setup(self):
        await super().setup()
        # load soldiers
        text = await Storage.read_text(path=soldiers_path)
        if text is not None:
            array = text.splitlines()
            for item in array:
                if len(item) < 45 or len(item) > 55:
                    self.error(msg='*** ID error: %s' % item)
                    continue
                cid = ID.parse(identifier=item)
                if cid is not None:
                    self.__soldiers.append(cid)
        # count
        count = len(self.__soldiers)
        if count < self.TROOPS:
            # more soldiers
            for i in range(count, self.TROOPS):
                cid = await Sergeant.training(sn=i)
                assert cid is not None, 'failed to train new soldier'
                self.__soldiers.append(cid)
                # save to '.dim/soldiers.txt'
                line = '%s\n' % cid
                await Storage.append_text(text=line, path=soldiers_path)

    # Override
    async def process(self) -> bool:
        processes = []
        for i in range(self.TROOPS):
            soldier = self.__soldiers[i]
            self.warning(msg='**** process starts [%d]: %s' % (i, soldier))
            sergeant = Sergeant(client_id=soldier, offset=self.__offset)
            proc = sergeant.attack()
            processes.append(proc)
            time.sleep(1)
            self.__offset += Sergeant.UNITS
        for proc in processes:
            try:
                proc.join()
            except KeyboardInterrupt as error:
                self.error(msg='process error: %s' % error)
            self.warning(msg='**** process stopped: %s' % proc)
        # return False to have a rest
        return False

    # Override
    async def _idle(self):
        print('====================================================')
        print('== All soldiers retreated, retry after 16 seconds...')
        print('====================================================')
        print('sleeping ...')
        for z in range(16):
            print('%d ..zzZZ' % z)
            await Runner.sleep(seconds=1.0)
        print('wake up.')
        print('====================================================')
        print('== Attack !!!')
        print('====================================================')


def show_help(app_name: str, default_config: str):
    cmd = sys.argv[0]
    print('')
    print('    %s' % app_name)
    print('')
    print('usages:')
    print('    %s [--config=<FILE>]' % cmd)
    print('    %s [-h|--help]' % cmd)
    print('')
    print('optional arguments:')
    print('    --config        config file path (default: "%s")' % default_config)
    print('    --help, -h      show this help message and exit')
    print('')


async def create_config(app_name: str, default_config: str) -> Config:
    """ load config """
    try:
        opts, args = getopt.getopt(args=sys.argv[1:],
                                   shortopts='hf:',
                                   longopts=['help', 'config='])
    except getopt.GetoptError:
        show_help(app_name=app_name, default_config=default_config)
        sys.exit(1)
    # check options
    ini_file = None
    for opt, arg in opts:
        if opt == '--config':
            ini_file = arg
        else:
            show_help(app_name=app_name, default_config=default_config)
            sys.exit(0)
    # check config filepath
    if ini_file is None:
        ini_file = default_config
    if not await Path.exists(path=ini_file):
        show_help(app_name=app_name, default_config=default_config)
        print('')
        print('!!! config file not exists: %s' % ini_file)
        print('')
        sys.exit(0)
    # load config from file
    config = Config()
    await config.load(path=ini_file)
    print('>>> config loaded: %s => %s' % (ini_file, config))
    return config


#
# show logs
#
Log.LEVEL = Log.DEVELOP
Log.LEVEL = Log.RELEASE


DEFAULT_CONFIG = '/etc/dim/config.ini'

soldiers_path = '/tmp/soldiers.txt'


Sergeant.LANDING_POINT = 'normandy'
Sergeant.UNITS = 10
Colonel.TROOPS = 10

# candidates
all_stations = [
    ('127.0.0.1', 'gsp-s001@x5Zh9ixt8ECr59XLye1y5WWfaX4fcoaaSC'),
    ('106.52.25.169', 'gsp-s002@wpjUWg1oYDnkHh74tHQFPxii6q9j3ymnyW'),
    ('147.139.30.182', 'gsp-india@x15NniVboopEtD3d81cbUibftcewMxzZLw'),
    ('47.254.237.224', 'gsp-jlp@x8Eudmgq4rHvTm2ongrwk6BVdS1wuE7ctE'),
    ('149.129.234.145', 'gsp-yjd@wjPLYSyaZ7fe4aNL8DJAvHBNnFcgK76eYq'),
    ('', ''),
    ('', ''),
    ('', ''),
]
test_station = all_stations[4]

Sergeant.HOST = test_station[0]
Sergeant.PORT = 9394


async def async_main():
    # create global variable
    shared = GlobalVariable()
    config = await create_config(app_name='Siege', default_config=DEFAULT_CONFIG)
    await shared.prepare(config=config)
    #
    #  Update config
    #
    station = config.get_section(section='station')
    Log.info(msg='**** Start testing %s ...' % station)
    client = Colonel()
    await client.run()
    Log.warning(msg='Mission accomplished')


def main():
    Runner.sync_run(main=async_main())


if __name__ == '__main__':
    main()
