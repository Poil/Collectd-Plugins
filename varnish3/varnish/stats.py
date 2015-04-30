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

import collections
import datetime
import inspect
from .api import stats


class VarnishStats(object):

    def __init__(self, varnish):
        self.varnish = varnish
        self.vd = varnish.vd
        stats.init(self.vd)

    def read(self, callback=None):
        if callback:
            args = len(inspect.getargspec(callback).args)

        def wrapper(point, data):
            data.append(point)
            if callback and args == 0:
                if callback:
                    callback()

            elif callback:
                callback(point)

        stats_list = list()
        stats.iterate(self.vd, wrapper, stats_list)
        return VarnishStatsReading(stats_list)

    def filter(self, filter_, exclude=False):
        """ Set filters for next read() calls. Return self, so calls are
            chainable """
        stats.filter_(self.vd, filter_, exclude)
        return self

    def exclude(self, filter_):
        return self.filter(filter_, exclude=True)

    def include(self, filter_):
        return self.filter(filter_, exclude=False)

    def __iter__(self):
        return self

    def next(self):
        return self.read()

    def __str__(self):
        return "<%s [instance: %s]>" % (self.__class__.__name__,
                                        self.varnish.name)

    def __repr__(self):
        return str(self)


class VarnishStatsReading(collections.Mapping):
    def __init__(self, points):
        object.__setattr__(self, "timestamp", datetime.datetime.utcnow())
        object.__setattr__(self, "_points", {})
        for point in points:
            self._points[point.full_name] = point

    def iter_by_class(self, class_):
        return (p for p in self.itervalues() if p.cls == class_)

    def get_in_class(self, class_):
        return list(self.iter_by_class(class_))

    def __getitem__(self, key):
        return self._points[key]

    def __iter__(self):
        return iter(self._points)

    def __len__(self):
        return len(self._points)

    def __contains__(self, obj):
        return obj in self._points

    def __str__(self):
        return "<%s[%s] - %s elements>" % (self.__class__.__name__,
                                           self.timestamp, len(self))

    def __repr__(self):
        return "<%s[%s] - %s>" % (self.__class__.__name__,
                                 self.timestamp, self._points)

    def __getattr__(self, attr):
        try:
            return self[attr].value

        except KeyError:
            raise AttributeError(attr)

        raise AttributeError(attr)

    def __setattr__(self, attr, value):
        raise TypeError("'%s' object does not support "
                        "attribute assignment" % (self.__class__.__name__))
