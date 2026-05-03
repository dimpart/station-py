# -*- coding: utf-8 -*-
#
#   DMTP: Direct Message Transfer Protocol
#
#                                Written in 2020 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2020 Albert Moky
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

import json
import threading
import time
from typing import Optional, Union
from weakref import WeakValueDictionary

from dimples import base64_encode

from udp.ba import IntegerData
from udp import SocketAddress
from udp import Hub

from dmtp import LocationValue, StringValue, BinaryValue
from dmtp import LocationDelegate

from .contact import Contact


class FieldValueEncoder(json.JSONEncoder):

    def default(self, value):
        if isinstance(value, IntegerData):
            return value.value
        elif isinstance(value, StringValue):
            return value.string
        elif isinstance(value, BinaryValue):
            return base64_encode(data=value.get_bytes())
        else:
            return super().default(value)


class Session:

    def __init__(self, location: LocationValue, address: SocketAddress):
        super().__init__()
        self.__location = location
        self.__address = address

    def __str__(self) -> str:
        return '%s@%s' % (self.__location.identifier, self.__address)

    def __repr__(self) -> str:
        return '%s@%s' % (self.__location.identifier, self.__address)

    @property
    def location(self) -> LocationValue:
        return self.__location

    @property
    def address(self) -> SocketAddress:
        return self.__address


class ContactManager(LocationDelegate):

    def __init__(self, hub: Hub, local: SocketAddress):
        super().__init__()
        self.identifier: str = ''
        self.nat: str = 'Unknown'
        self.__source_address = local
        self.__hub = hub
        # contacts
        self.__contacts = {}  # str(ID) -> Contact
        self.__contacts_lock = threading.Lock()
        # locations
        self.__locations = WeakValueDictionary()  # (IP, port) -> LocationValue

    # noinspection PyMethodMayBeStatic
    def _create_contact(self, identifier: str) -> Contact:
        return Contact(identifier=identifier)

    def __get_contact(self, identifier: Union[str, StringValue]) -> Contact:
        if isinstance(identifier, StringValue):
            identifier = identifier.string
        with self.__contacts_lock:
            contact = self.__contacts.get(identifier)
            if contact is None:
                contact = self._create_contact(identifier=identifier)
                self.__contacts[identifier] = contact
            return contact

    #
    #   LocationDelegate
    #

    def store_location(self, location: LocationValue) -> bool:
        identifier = location.identifier
        if identifier is None:
            # location ID not found
            return False
        # store by contact
        contact = self.__get_contact(identifier=identifier)
        if not contact.store_location(location=location):
            # location error
            return False
        # update the map
        source_address = location.source_address
        if source_address is not None:
            self.__locations[source_address] = location
        mapped_address = location.mapped_address
        if mapped_address is not None:
            self.__locations[mapped_address] = location
        return True

    def clear_location(self, location: LocationValue) -> bool:
        identifier = location.identifier
        if identifier is None:
            # location ID not found
            return False
        # store by contact
        contact = self.__get_contact(identifier=identifier)
        if not contact.clear_location(location=location):
            # location error
            return False
        # update the map
        source_address = location.source_address
        if source_address is not None:
            self.__locations.pop(source_address)
        mapped_address = location.mapped_address
        if mapped_address is not None:
            self.__locations.pop(mapped_address)
        return True

    def current_location(self) -> Optional[LocationValue]:
        if self.identifier is None:
            return None
        contact = self.__get_contact(identifier=self.identifier)
        # contact.purge(peer=self.__peer)
        return contact.get_location(address=self.__source_address)

    def get_location(self, address: SocketAddress) -> Optional[LocationValue]:
        location = self.__locations.get(address)
        if location is None:
            return None
        if Contact.is_location_expired(location=location, hub=self.__hub):
            return None
        return location

    def get_locations(self, identifier: str) -> list:
        contact = self.__get_contact(identifier=identifier)
        contact.purge(hub=self.__hub)
        return contact.locations

    def sign_location(self, location: LocationValue) -> Optional[LocationValue]:
        if self.identifier != location.identifier:
            # ID not match
            return None
        # timestamp
        now = int(time.time())
        # location value to be signed
        value = LocationValue.new(identifier=location.identifier,
                                  source_address=self.__source_address,
                                  mapped_address=location.mapped_address,
                                  relayed_address=location.relayed_address,
                                  timestamp=now, nat=self.nat)
        contact = self.__get_contact(identifier=self.identifier)
        return contact.sign_location(location=value)
