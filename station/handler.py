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
    Request Handler
    ~~~~~~~~~~~~~~~

    Handler for each connection
"""

from socketserver import StreamRequestHandler

from libs.utils import get_exception_traceback
from libs.utils import Logging, Runner
from libs.server import ServerSession, SessionCenter
from libs.server.cpu.text import RequestHandlerMarker

from station.shared import GlobalVariable
from station.shared import create_messenger


class RequestHandler(StreamRequestHandler, Logging):

    """
        DIM Request Handler
    """

    def __del__(self):
        self.info(msg='request removed: %s' % str(self.client_address))
        marker = RequestHandlerMarker()
        marker.remove_handler(handler=self)

    # Override
    def setup(self):
        super().setup()
        self.info(msg='request setup: %s' % str(self.client_address))
        marker = RequestHandlerMarker()
        marker.setup_handler(handler=self)

    # Override
    def finish(self):
        super().finish()
        self.info(msg='request finished: %s' % str(self.client_address))

    # Override
    def handle(self):
        super().handle()
        try:
            self.info(msg='session started: %s' % str(self.client_address))
            Runner.sync_run(main=_start_session(handler=self))
            self.info(msg='session finished: %s' % str(self.client_address))
        except Exception as error:
            self.error(msg='request handler error: %s' % error)
            # traceback.print_exc()
            tr = get_exception_traceback()
            self.error('traceback: %s', tr)


async def _start_session(handler: RequestHandler):
    client_address = handler.client_address
    request = handler.request
    shared = GlobalVariable()
    session = ServerSession(remote=client_address, sock=request, database=shared.sdb)
    marker = RequestHandlerMarker()
    marker.link_session(session=session, handler=handler)
    messenger = create_messenger(facebook=shared.facebook, database=shared.mdb, session=session)
    center = SessionCenter()
    # setup
    center.add_session(session=session)
    try:
        # handle
        await session.run()
        # await session.stop()
    finally:
        # finish
        center.remove_session(session=session)
        await Runner.sleep(seconds=2.0)
    return messenger
