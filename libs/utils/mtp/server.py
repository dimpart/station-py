# -*- coding: utf-8 -*-

import json
import socket
import traceback
from typing import Optional

from startrek import Porter, PorterStatus, PorterDelegate
from startrek import Arrival, Departure

from udp.mtp import Package, DataType
from udp import SocketAddress
from udp import Channel, BaseChannel
from udp import Connection
from udp import PackageArrival, PackagePorter
from udp import ServerHub

from dimples.conn import UDPServerGate

import dmtp

from ...utils import Logging

from .manager import ContactManager, FieldValueEncoder
from .contact import ContactHub


class DmtpServerHub(ServerHub, ContactHub):

    # Override
    def _get_channel(self, remote: Optional[SocketAddress], local: Optional[SocketAddress]) -> Optional[Channel]:
        channel = super()._get_channel(remote=remote, local=local)
        if channel is None and remote is not None and local is not None:
            channel = super()._get_channel(remote=None, local=local)
        return channel

    # Override
    def _set_channel(self, channel: Channel,
                     remote: Optional[SocketAddress], local: Optional[SocketAddress]):
        super()._set_channel(channel=channel, remote=remote, local=local)

    # Override
    def _remove_channel(self, channel: Optional[Channel],
                        remote: Optional[SocketAddress], local: Optional[SocketAddress]) -> Optional[Channel]:
        return super()._remove_channel(channel=channel, remote=remote, local=local)

    # Override
    def _get_connection(self, remote: SocketAddress, local: Optional[SocketAddress]) -> Optional[Connection]:
        return super()._get_connection(remote=remote, local=None)

    # Override
    def _set_connection(self, connection: Connection,
                        remote: SocketAddress, local: Optional[SocketAddress]) -> Optional[Connection]:
        return super()._set_connection(connection=connection, remote=remote, local=None)

    # Override
    def _remove_connection(self, connection: Optional[Connection],
                           remote: SocketAddress, local: Optional[SocketAddress]) -> Optional[Connection]:
        return super()._remove_connection(connection=connection, remote=remote, local=None)


class Server(dmtp.Server, Logging, PorterDelegate):

    def __init__(self, host: str, port: int):
        super().__init__()
        self.__local_address = (host, port)
        gate = UDPServerGate(delegate=self)
        gate.hub = DmtpServerHub(delegate=gate)
        self.__gate = gate
        self.__db: Optional[ContactManager] = None

    @property
    def local_address(self) -> tuple:
        return self.__local_address

    @property
    def gate(self) -> UDPServerGate:
        return self.__gate

    @property
    def hub(self) -> DmtpServerHub:
        return self.gate.hub

    @property
    def database(self) -> ContactManager:
        return self.__db

    @database.setter
    def database(self, db: ContactManager):
        self.__db = db

    @property
    def identifier(self) -> str:
        return self.__db.identifier

    @identifier.setter
    def identifier(self, uid: str):
        self.__db.identifier = uid

    # protected
    async def bind(self, local: SocketAddress):
        channel, sock = self.hub.bind(address=local)
        if sock is not None:
            assert isinstance(channel, BaseChannel), 'channel error: %s' % channel
            # set socket for this channel
            await channel.set_socket(sock=sock)

    async def start(self):
        await self.bind(local=self.local_address)
        # self.gate.start()
        # while self.gate.running:
        #     await Runner.sleep(seconds=2.0)

    def stop(self):
        # self.gate.stop()
        pass

    # Override
    async def _connect(self, remote: tuple):
        try:
            await self.hub.connect(remote=remote, local=self.__local_address)
        except socket.error as error:
            self.error('failed to connect to %s: %s' % (remote, error))

    # Override
    async def porter_status_changed(self, previous: PorterStatus, current: PorterStatus, porter: Porter):
        remote = porter.remote_address
        local = porter.local_address
        self.info('!!! connection (%s, %s) state changed: %s -> %s' % (remote, local, previous, current))

    # Override
    async def porter_received(self, ship: Arrival, porter: Porter):
        assert isinstance(ship, PackageArrival), 'arrival ship error: %s' % ship
        pack = ship.package
        if pack is not None:
            await self._received(head=pack.head, body=pack.body, source=porter.remote_address)

    # Override
    async def porter_sent(self, ship: Departure, porter: Porter):
        pass

    # Override
    async def porter_failed(self, error: IOError, ship: Departure, porter: Porter):
        pass

    # Override
    async def porter_error(self, error: IOError, ship: Departure, porter: Porter):
        pass

    # Override
    async def _process_command(self, cmd: dmtp.Command, source: tuple) -> bool:
        self.info('received cmd: %s' % cmd)
        # noinspection PyBroadException
        try:
            return await super()._process_command(cmd=cmd, source=source)
        except Exception as error:
            self.error('failed to process command (%s): %s' % (cmd, error))
            traceback.print_exc()
            return False

    # Override
    async def _process_message(self, msg: dmtp.Message, source: tuple) -> bool:
        self.info('received msg from %s:\n\t%s' % (source, json.dumps(msg, cls=FieldValueEncoder)))
        # return await super()._process_message(msg=msg, source=source)
        return True

    # Override
    async def send_command(self, cmd: dmtp.Command, destination: tuple) -> bool:
        self.info('sending cmd to %s:\n\t%s' % (destination, cmd))
        pack = Package.new(data_type=DataType.COMMAND, body=cmd)
        return await self.send_package(pack=pack, destination=destination)

    # Override
    async def send_message(self, msg: dmtp.Message, destination: tuple) -> bool:
        self.info('sending msg to %s:\n\t%s' % (destination, json.dumps(msg, cls=FieldValueEncoder)))
        pack = Package.new(data_type=DataType.MESSAGE, body=msg)
        return await self.send_package(pack=pack, destination=destination)

    async def send_package(self, pack: Package, destination: tuple, priority: Optional[int] = 0):
        source = self.__local_address
        worker = await self.gate.fetch_porter(remote=destination, local=source)
        assert isinstance(worker, PackagePorter), 'package docker error: %s' % worker
        return await worker.send_package(pack=pack, priority=priority)

    #
    #   Server actions
    #

    # Override
    async def say_hello(self, destination: tuple) -> bool:
        if super().say_hello(destination=destination):
            return True
        cmd = dmtp.Command.hello_command(identifier=self.identifier)
        return await self.send_command(cmd=cmd, destination=destination)
