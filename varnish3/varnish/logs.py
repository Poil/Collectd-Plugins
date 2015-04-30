#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2012 Giacomo Bagnoli <g.bagnoli@asidev.com>

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from datetime import datetime
import inspect
import logging
import functools
from .api import logs
from .utils import MultiDict
log = logging.getLogger(__name__)


class VarnishLogs(object):
    default_settings = {
           'process_old_entries': False,
           'process_backend_requests': False,
           'process_client_requests': False,
           'include_tag': None,
           'include_tag_regex': None,
           'exclude_tag': None,
           'exclude_tag_regex': None,
           'stop_after': None,
           'skip_first': None,
           'read_entries_from_file': None,
           'filter_transactions_by_tag_regex': None,
           'ignore_case_in_regex': False
        }

    def __init__(self, varnish, **settings):
        self.settings = dict(self.default_settings)
        self.settings.update(settings)
        self.varnish = varnish
        self.vd = varnish.vd
        logs.init(self.vd, True)
        for st, value in self.settings.items():
            if value and self.default_settings[st] is None:
                getattr(logs, st)(self.vd, value)

            elif value and self.default_settings[st] is False:
                getattr(logs, st)(self.vd)

            if value and st == "filter_transactions_by_tag_regex":
                getattr(logs, st)(self.vd, value[0], value[1])

    def __getattr__(self, attr):
        if attr in self.default_settings:
            return functools.partial(getattr(logs, attr), self.vd)

        raise AttributeError(attr)

    def dispatch_chunks(self, callback, source=None):
        """ Read logs from varnish shared memory logs, then call callback
            for every chunk as returned from the low level api
            `callback` must be a callable that accepts 0 or 1 positional
            parameter (an instance of the varnish.api.logs.LogChunk class)
        """
        if callback:
            args = len(inspect.getargspec(callback).args)

        def wrapper(chunk, priv):
            res = False

            if callback and args == 0:
                res = callback()

            elif callback:
                res = callback(chunk)

            return res

        if source:
            self.read_entries_from_file(source)

        logs.dispatch(self.vd, wrapper)

    def dispatch_requests(self, callback, aggregate=1000, source=None):
        """ Read logs from Varnish shared memory Logs, then call callback
            when a RequestLog is complete (all its chunks have been read).
            `callback` must be a callable that accepts 1 positional parameter
            (an instance of ClientRequestLog or BackendRequestLog, subclasses
             of RequestLog)
            if `aggregate` is true, try to relate backend requests to the
            client request that generated it
        """
        if aggregate:
            # use a multidict because it is ordered
            backend_requests = MultiDict()

        def cb(chunk):
            ev = RequestLog(chunk)
            # discard invalid, incomplete and empty logs
            res = True
            if not ev or not ev.complete or (ev.backend and not ev.chunks):
                return res

            if not aggregate:
                res = callback(ev)

            elif ev.backend:
                id_ = ev.txheaders.getone('x-varnish')
                log.debug("Adding %s to backend_requests", ev)
                backend_requests.overwrite(id_, ev)

            elif ev.client and ev.id in backend_requests:
                ev.backend_request = backend_requests.getone(ev.id)
                res = callback(ev)

            else:
                # backend request was not read, leaving to None
                res = callback(ev)

            if aggregate and len(backend_requests) > aggregate:
                backend_requests.trim(aggregate)

            return res

        self.dispatch_chunks(callback=cb)

    def __str__(self):
        return "<%s [instance: %s]>" % (self.__class__.__name__,
                                        self.varnish.name)

    def __repr__(self):
        return str(self)


class RequestLog(object):
    """ This class is a factory for its subclasses. It keeps returning the
        same objects as long as the chunk belongs to an existing instance.
        It returns None if the chunk belongs to neither a client of backend
        request
    """
    _lines = {}

    def __new__(cls, chunk, active=False):
        if chunk.fd in cls._lines:
            obj = cls._lines[chunk.fd]

        else:
            if chunk.client:
                obj = super(RequestLog, cls).__new__(ClientRequestLog)

            elif chunk.backend:
                obj = super(RequestLog, cls).__new__(BackendRequestLog)

            else:
                return None

            obj.init(chunk, active)
            cls._lines[chunk.fd] = obj

        obj.add_chunk(chunk)
        return obj

    def init(self, chunk, active=False):
        if hasattr(self, "fd"):
            return

        self.fd = chunk.fd
        self.chunks = []
        self.active = active
        self.complete = False
        self.rxheaders = MultiDict()
        self.txheaders = MultiDict()
        self.rxprotocol = None
        self.txprotocol = None
        self.method = None
        self.url = None
        self.status = None
        self.response = None
        self.length = None

    def add_chunk(self, chunk):
        if self.fd == 0:
            return False

        if not self.active and \
            ((chunk.client and chunk.tag.name == 'reqstart') or
             (chunk.backend and chunk.tag.name == 'backendopen')):
            self.active = True

        elif not self.active:
            return False

        if (chunk.client and chunk.tag.name == 'reqend') or \
           (chunk.backend and (chunk.tag.name == 'backendclose' or
                               chunk.tag.name == 'backendreuse')):
            self.complete = True
            self.active = False
            del self.__class__._lines[self.fd]
            if chunk.tag.name == 'backendreuse':
                # backend reuse need a special case to get the next backend
                # request as no backendopen will arrive
                # then we create a new empry object that we now is active
                next_backend = super(RequestLog, self.__class__)\
                                        .__new__(BackendRequestLog)
                next_backend.init(chunk, active=True)
                self.__class__._lines[chunk.fd] = next_backend
                next_backend.on_append_chunk(chunk)

        self.on_append_chunk(chunk)
        return self.complete

    def on_append_chunk(self, chunk):
        self.client = chunk.client
        self.backend = chunk.backend
        self.chunks.append(chunk)
        name = chunk.tag.name
        if name == 'rxheader':
            key, value = chunk.data.split(":", 1)
            self.rxheaders[key.strip().lower()] = value.strip()

        elif name == 'txheader':
            key, value = chunk.data.split(":", 1)
            self.txheaders[key.strip().lower()] = value.strip()

        elif name == 'rxprotocol':
            self.rxprotocol = chunk.data

        elif name == 'txprotocol':
            self.txprotocol = chunk.data

        elif name == 'length':
            self.length = int(chunk.data)

    def __repr__(self):
        res = "<%s %s" % (self.__class__.__name__, self.id)
        for c in self.chunks:
            res += "\n\t%s" % (c)
        res += ">"
        return res


class ClientRequestLog(RequestLog):
    """ Aggragates chunks for a client request """

    def init(self, chunk, active=False):
        super(ClientRequestLog, self).init(chunk, active)
        self.id = None
        self.vcl_calls = MultiDict()
        self.hash_data = []
        self.client_ip = None
        self.client_port = None
        self.started_at = None
        self.completed_at = None
        self.req_start_delay = None
        self.processing_time = None
        self.deliver_time = None
        self.backend_request = None

    def on_append_chunk(self, chunk):
        super(ClientRequestLog, self).on_append_chunk(chunk)
        name = chunk.tag.name

        if name == 'vcl_call':
            self._last_vcl = chunk.data

        elif name == 'vcl_return':
            self.vcl_calls[self._last_vcl] = chunk.data
            del self._last_vcl

        elif name == 'hash':
            self.hash_data.append(chunk.data)

        elif name == 'length':
            self.length = int(chunk.data)

        elif name == 'rxrequest':
            self.method = chunk.data

        elif name == 'rxurl':
            self.url = chunk.data

        elif name == 'reqstart':
            self.client_ip, self.client_port, self.id = \
                chunk.data.split(" ")

        elif name == 'txstatus':
            self.status = int(chunk.data)

        elif name == 'txresponse':
            self.response = chunk.data

        elif name == 'reqend':
            xid, started_at, completed_at, \
                req_start_delay, processing_time, \
                deliver_time = chunk.data.split(" ")
            self.started_at = datetime.fromtimestamp(float(started_at))
            self.completed_at = datetime.fromtimestamp(float(completed_at))
            self.req_start_delay = float(req_start_delay)
            self.processing_time = float(processing_time)
            self.deliver_time = float(deliver_time)

    @property
    def hit(self):
        return "hit" in self.vcl_calls

    @property
    def miss(self):
        return "miss" in self.vcl_calls

    def __repr__(self):
        res = """
<{self.__class__.__name__} XID: {self.id}
    Client: {self.client_ip}:{self.client_port}

    Timing:
        started   : {self.started_at}
        completed : {self.completed_at}
        delay     : {self.req_start_delay} [s]
        processing: {self.processing_time} [s]
        deliver   : {self.deliver_time} [s]

    Request: {self.rxprotocol} {self.method} {self.url}
        headers   : {self.rxheaders}

    Hash: {self.hash_data}
    VCL Calls: {self.vcl_calls}

    Response: {self.txprotocol} {self.status} {self.response} [{self.length}B]
        headers   : {self.txheaders}
>""".format(self=self)
        return res

    def __str__(self):
        return "<{self.__class__.__name__} XID: {self.id}>".format(self=self)


class BackendRequestLog(RequestLog):
    """ Aggragates chunks for a backend request """

    def init(self, chunk, active=False):
        super(BackendRequestLog, self).init(chunk, active)
        self.backend_name = None

    def on_append_chunk(self, chunk):
        super(BackendRequestLog, self).on_append_chunk(chunk)
        name = chunk.tag.name
        if name == 'txrequest':
            self.method = chunk.data

        elif name == 'txurl':
            self.url = chunk.data

        elif name == 'rxstatus':
            self.status = int(chunk.data)

        elif name == 'rxresponse':
            self.response = chunk.data

        elif name in ('backendopen', 'backendreuse'):
            self.backend_name = chunk.data.split(" ")[0]

    def __repr__(self):
        return """
<{self.__class__.__name__} [backend: {self.backend_name}]
    Request: {self.rxprotocol} {self.method} {self.url}
        headers   : {self.rxheaders}

    Response: {self.txprotocol} {self.status} {self.response} [{self.length}B]
        headers   : {self.txheaders}
>""".format(self=self)

    def __str__(self):
        return "<{self.__class__.__name__} ({self.backend_name})>"\
                .format(self=self)
