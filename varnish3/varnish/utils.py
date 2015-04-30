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
import logging
__all__ = ['setup_logging', 'MultiDict']


class _NullHandler(logging.Handler):
    level = None

    def emit(self, record):
        pass

    @classmethod
    def handle(cls, record):
        pass

    def createLock(self):
        return None


def setup_logging():
    """ Setup logging adding a NullHandler, since logging configuration is
        a task done by the application itself.
        Prefer the logging.NullHandler handler if present (py>=2.7)
    """

    logger = logging.getLogger('varnish')
    logger.addHandler(_NullHandler)


class MultiDict(collections.MutableMapping):
    """
        This is a modified version of MultiDict shamelessly stolen from WebOb
        http://www.webob.org/

        An ordered dictionary that can have multiple values for each key.
        Adds the methods to the normal dictionary interface.

        (c) 2005 Ian Bicking and contributors; written for Paste
        (http://pythonpaste.org) Licensed under the MIT license:
        http://www.opensource.org/licenses/mit-license.php
    """

    def __init__(self, *args, **kw):
        if len(args) > 1:
            raise TypeError("MultiDict can only be called with one positional "
                            "argument")
        if args:
            if hasattr(args[0], 'iteritems'):
                items = list(args[0].iteritems())
            elif hasattr(args[0], 'items'):
                items = args[0].items()
            else:
                items = list(args[0])
            self._items = items
        else:
            self._items = []
        if kw:
            self._items.extend(kw.items())

    def __getitem__(self, key):
        """
        Return a list of all values matching the key (may be an empty list)
        """
        result = []
        for k, v in self._items:
            if key == k:
                result.append(v)

        if not result:
            raise KeyError(key)

        return result

    def __setitem__(self, key, value):
        """
        Add the key and value, not overwriting any previous value.
        """
        self._items.append((key, value))

    def __delitem__(self, key):
        items = self._items
        found = False
        for i in range(len(items) - 1, -1, -1):
            if items[i][0] == key:
                del items[i]
                found = True

        if not found:
            raise KeyError(key)

    def overwrite(self, key, value):
        """
        Set the value at key, discarding previous values set if any
        """
        try:
            del self[key]

        except:
            pass

        self[key] = value

    def getone(self, key):
        """
        Get one value matching the key, raising a KeyError if multiple
        values were found.
        """
        v = self[key]
        if len(v) > 1:
            raise KeyError('Multiple values match %r: %r' % (key, v))

        return v[0]

    def dict_of_lists(self):
        """
        Returns a dictionary where each key is associated with a list of values
        """
        r = {}
        for key, val in self.items():
            r.setdefault(key, []).append(val)
        return r

    def __contains__(self, key):
        for k, v in self._items:
            if k == key:
                return True
        return False

    has_key = __contains__

    def clear(self):
        del self._items[:]

    def copy(self):
        return self.__class__(self)

    def setdefault(self, key, default=None):
        for k, v in self._items:
            if key == k:
                return v
        self._items.append((key, default))
        return default

    def pop(self, key, *args):
        if len(args) > 1:
            raise TypeError("pop expected at most 2 arguments, got %s"
                             % repr(1 + len(args)))
        for i in range(len(self._items)):
            if self._items[i][0] == key:
                v = self._items[i][1]
                del self._items[i]
                return v
        if args:
            return args[0]
        else:
            raise KeyError(key)

    def popitem(self):
        return self._items.pop()

    def extend(self, other=None, **kwargs):
        if other is None:
            pass

        elif hasattr(other, 'items'):
            self._items.extend(other.items())

        elif hasattr(other, 'keys'):
            for k in other.keys():
                self._items.append((k, other[k]))

        else:
            for k, v in other:
                self._items.append((k, v))

        if kwargs:
            self.update(kwargs)

    def __repr__(self):
        items = map('(%r, %r)'.__mod__, _hide_passwd(self.items()))
        return '%s([%s])' % (self.__class__.__name__, ', '.join(items))

    def __len__(self):
        return len(self._items)

    def iterkeys(self):
        for k, v in self._items:
            yield k

    def keys(self):
        return [k for k, v in self._items]

    __iter__ = iterkeys

    def iteritems(self):
        return iter(self._items)

    def items(self):
        return self._items[:]

    def itervalues(self):
        for k, v in self._items:
            yield v

    def values(self):
        return [v for k, v in self._items]

    def trim(self, size):
        if len(self) <= size:
            return

        self._items = self._items[-size:]


def _hide_passwd(items):
    for k, v in items:
        try:
            if ('password' in k
                or 'passwd' in k
                or 'pwd' in k
            ):
                yield k, '******'

            else:
                yield k, v

        except TypeError:
            yield k, v
