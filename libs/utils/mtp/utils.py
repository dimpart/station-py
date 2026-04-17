# -*- coding: utf-8 -*-

from typing import Optional, Union

from udp.ba import ByteArray, Data, MutableData, VarIntData
from udp.mtp import DataType, TransactionID, Header, Package

from dmtp import Message
from dmtp import StringValue, BinaryValue

from dimples import base64_encode, base64_decode
from dimples import utf8_decode, utf8_encode
from dimples import json_encode, json_decode
from dimples import ReliableMessage


class MTPUtils:

    @classmethod
    def parse_head(cls, data: bytes) -> Header:
        return Header.parse(data=Data(buffer=data))

    @classmethod
    def parse_package(cls, data: bytes) -> Package:
        return Package.parse(data=Data(buffer=data))

    @classmethod
    def create_package(cls, body: Union[bytes, bytearray, ByteArray],
                       data_type: DataType, sn: Optional[TransactionID] = None) -> Package:
        if not isinstance(body, ByteArray):
            body = Data(buffer=body)
        return Package.new(data_type=data_type, sn=sn, body_length=body.size, body=body)

    @classmethod
    def serialize_message(cls, msg: ReliableMessage) -> bytes:
        info = msg.dictionary
        #
        #  body
        #
        content = info.get('data')
        if content is not None:
            assert isinstance(content, str), 'reliable message content error: %s' % content
            if content.startswith('{'):
                # JsON
                info['data'] = utf8_encode(string=content)
            else:
                # Base64
                info['data'] = base64_decode(string=content)
        signature = info.get('signature')
        if signature is not None:
            assert isinstance(signature, str), 'reliable message signature error: %s' % signature
            info['signature'] = base64_decode(string=signature)
        # symmetric key/keys
        key = info.get('key')
        if key is None:
            keys = info.get('keys')
            if keys is not None:
                assert isinstance(keys, dict), 'reliable message keys error: %s' % keys
                # DMTP store both 'keys' and 'key' in 'key'
                info['key'] = b'KEYS:' + build_keys(keys=keys)
        else:
            assert isinstance(key, str), 'reliable message key error: %s' % key
            info['key'] = base64_decode(string=key)
        #
        #  attachments
        #
        meta = info.get('meta')
        if meta is not None:
            # dict to JSON
            assert isinstance(meta, dict), 'meta error: %s' % meta
            js = json_encode(container=meta)
            js = utf8_encode(string=js)
            info['meta'] = js
        visa = info.get('visa')
        if visa is not None:
            # dict to JSON
            assert isinstance(visa, dict), 'visa error: %s' % visa
            js = json_encode(container=visa)
            js = utf8_encode(string=js)
            info['visa'] = js

        # create as message
        msg = Message.new(info=info)
        return msg.get_bytes()

    @classmethod
    def deserialize_message(cls, data: bytes) -> Optional[ReliableMessage]:
        msg = Message.parse(data=data)
        if msg is None or msg.sender is None or msg.receiver is None:
            raise ValueError('failed to deserialize data: %s' % data)
        #
        #  envelope
        #
        info = {
            'sender': msg.sender,
            'receiver': msg.receiver,
            'time': msg.time,
        }
        msg_type = msg.type
        if msg_type is not None and msg_type > 0:
            info['type'] = msg_type
        group = msg.group
        if group is not None:
            info['group'] = group
        #
        #  body
        #
        content = msg.content
        if content is not None:
            if content.startswith(b'{'):
                # JsON
                info['data'] = utf8_decode(data=content)
            else:
                # Base64
                info['data'] = base64_encode(data=content)
        signature = msg.signature
        if signature is not None:
            info['signature'] = base64_encode(data=signature)
        # symmetric key/keys
        key = msg.key
        if key is not None and len(key) > 5:
            if key[:5] == b'KEYS:':
                info['keys'] = parse_keys(data=key[5:])
            else:
                info['key'] = base64_encode(data=key)
        #
        #  attachments
        #
        meta = msg.meta
        if meta is not None and len(meta) > 0:
            # JSON to dict
            js = utf8_decode(data=meta)
            js = json_decode(string=js)
            info['meta'] = js
        visa = msg.visa
        if visa is not None and len(visa) > 0:
            # JSON to dict
            js = utf8_decode(data=visa)
            js = json_decode(string=js)
            info['visa'] = js

        # create reliable message
        return ReliableMessage.parse(msg=info)


def parse_keys(data: ByteArray) -> dict:
    keys = {}
    while data.length > 0:
        # get key length
        size = VarIntData.from_data(data=data)
        data = data.slice(start=size.size)
        # get key name
        name = StringValue.parse(data=data.slice(end=size.value))
        data = data.slice(start=size.value)
        # get value length
        size = VarIntData.from_data(data=data)
        data = data.slice(start=size.size)
        # get value
        value = BinaryValue(data=data.slice(end=size.value))
        data = data.slice(start=size.value)
        assert name.length > 0, 'key name empty'
        if value.size > 0:
            keys[name.string] = base64_encode(data=value.get_bytes())
    return keys


def build_keys(keys: dict) -> bytes:
    data = MutableData(capacity=512)
    for identifier in keys:
        id_value = StringValue.new(string=identifier)
        base64 = keys[identifier]
        if id_value.size > 0 and base64 is not None and len(base64) > 0:
            key_value = BinaryValue(data=base64_decode(string=base64))
            data.append(VarIntData.from_int(value=id_value.size))
            data.append(id_value)
            data.append(VarIntData.from_int(value=key_value.size))
            data.append(key_value)
    return data.get_bytes()
