#! /usr/bin/env python3
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
    DIM Station
    ~~~~~~~~~~~

    DIM network server node
"""

import sys
from socketserver import ThreadingTCPServer

from dimples.utils import SysArgvParser
from dimples.utils import init_logger
from dimples.utils import Log, LogLevel
from dimples.utils import Runner
from dimples.utils import Path

path = Path.abs(path=__file__)
path = Path.dir(path=path)
path = Path.dir(path=path)
Path.add(path=path)

from libs.utils.mtp import Server as UDPServer

from station.shared import GlobalVariable
from station.shared import create_config
from station.handler import RequestHandler


#
#  show logs
#
LOG_LEVEL = LogLevel.DEVELOP
LOGGER_NAME = 'dims'

APP_NAME = 'DIM Network Station'

DEFAULT_CONFIG = '/etc/dim/station.ini'


def show_help():
    cmd = sys.argv[0]
    print('')
    print('    %s' % APP_NAME)
    print('')
    print('usages:')
    print('    %s [--config=<FILE>]' % cmd)
    print('    %s [-h|--help]' % cmd)
    print('')
    print('optional arguments:')
    print('    --config        config file path (default: "%s")' % DEFAULT_CONFIG)
    print('    --help, -h      show this help message and exit')
    print('')


async def async_main():
    #
    #  parse cmd parameters
    #
    sys_argv = SysArgvParser.parse(shortopts='hf:ld:',
                                   longopts=['help', 'config=', 'log-location', 'log-dir='])
    if sys_argv is None:
        show_help()
        sys.exit(1)
    #
    #  init logger
    #
    show_location = sys_argv.has_opt(opt='log-location')
    log_directory = sys_argv.get_opt(opt='log-dir')
    init_logger(name=LOGGER_NAME, level=LOG_LEVEL, show_location=show_location, directory=log_directory)
    #
    #  create config
    #
    config = await create_config(sys_argv=sys_argv, default_config=DEFAULT_CONFIG)
    if config is None:
        show_help()
        sys.exit(1)
    #
    #  login
    #
    sid = config.station_id
    shared = GlobalVariable()
    await shared.login(current_user=sid)
    #
    #  Station host & port
    #
    host = config.station_host
    port = config.station_port
    assert host is not None and port > 0, 'station config error: %s' % config
    host = '0.0.0.0'
    server_address = (host, port)
    #
    #  Start UDP Server
    #
    Log.info('>>> UDP server %s starting ...', server_address)
    g_udp_server = UDPServer(host=server_address[0], port=server_address[1])
    await g_udp_server.start()
    #
    #  Start TCP server
    #
    try:
        # ThreadingTCPServer.allow_reuse_address = True
        server = ThreadingTCPServer(server_address=server_address,
                                    RequestHandlerClass=RequestHandler,
                                    bind_and_activate=False)
        Log.info('>>> TCP server %s starting...', server_address)
        server.allow_reuse_address = True
        server.server_bind()
        server.server_activate()
        server.serve_forever()
    except KeyboardInterrupt as ex:
        Log.info('~~~~~~~~ %s', ex)
    finally:
        g_udp_server.stop()
        Log.info('======== station shutdown!')


def main():
    Runner.sync_run(main=async_main())


if __name__ == '__main__':
    main()
