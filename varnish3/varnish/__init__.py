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

import logging
from .utils import setup_logging
from . import api
from .stats import VarnishStats
from .logs import VarnishLogs
from .exc import VarnishUninitializedError

__version__ = (0, 0, 0, 'dev', 0)
setup_logging()
__all__ = ['Instance']
log = logging.getLogger(__name__)


def check_initialized(method):
    def wrapper(self, *args, **kwargs):
        if not self.vd:
            raise VarnishUninitializedError()

        return method(self, *args, **kwargs)

    return wrapper


class Instance(object):

    def __init__(self, name=None, log_level=None):
        self.vd = None
        self.log_level = log_level
        self._name = name
        if self.log_level:
            self.log_level = self.log_level.lower()

    def init(self):
        self.vd = api.init()
        if self.log_level:
            log_method = getattr(log, self.log_level)
            api.set_diagnostic_function(self.vd, log_method, None)

        if self._name:
            api.access_instance(self.vd, self._name)

    @check_initialized
    def close(self):
        api.close(self.vd)
        api.delete(self.vd)
        self.vd = None
        if hasattr(self, '_stats'):
            del self._stats

        if hasattr(self, '_logs'):
            del self._logs

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, type, value, tb):
        self.close()

    @check_initialized
    def open(self, verbose=False):
        api.open(self.vd, verbose)

    @check_initialized
    def reopen(self, verbose=False):
        api.reopen(self.vd, verbose)

    @property
    def name(self):
        return self._name or "<default>"

    @property
    @check_initialized
    def stats(self):
        if not hasattr(self, "_stats"):
            self._stats = VarnishStats(self)

        return self._stats

    @property
    @check_initialized
    def logs(self):
        """ Accessing logs using the same instance used to read stats will
            result in an assertion failure in varnish <= 3.0.2
        """
        if not hasattr(self, '_logs'):
            self._logs = VarnishLogs(self)

        return self._logs
