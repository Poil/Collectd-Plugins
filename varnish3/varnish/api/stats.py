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
import ctypes
import logging
from ..exc import (VarnishException,
                   VarnishUnHandledException)
from .vsm import _VSM_data


__all__ = ['open_', 'main', 'setup', 'init', 'iterate', 'filter_', 'exclude']
varnishapi = ctypes.CDLL('libvarnishapi.so.1')
log = logging.getLogger(__name__)


class _VSC_C_main(ctypes.Structure):
    pass


class _VSC_Point(ctypes.Structure):
    __slots__ = ['cls', 'ident', 'name', 'fmt', 'flag', 'desc', 'ptr']
    _fields_ = [('cls', ctypes.c_char_p),
                ('ident', ctypes.c_char_p),
                ('name', ctypes.c_char_p),
                ('fmt', ctypes.c_char_p),
                ('flag', ctypes.c_int),
                ('desc', ctypes.c_char_p),
                ('ptr', ctypes.c_void_p)]


class VarnishStatsPoint(object):
    """ Python object used to copy the _VSC_Point structure """
    __slots__ = ['cls', 'ident', 'name', 'flag', 'desc',
                'value', 'full_name']

    def __init__(self, vsc_point):
        self.cls = str(vsc_point.cls)
        self.ident = str(vsc_point.ident)
        self.name = str(vsc_point.name)
        assert vsc_point.fmt == 'uint64_t'
        self.flag = chr(vsc_point.flag)
        self.desc = str(vsc_point.desc)
        self.value = long(ctypes.cast(vsc_point.ptr,
                                      ctypes.POINTER(ctypes.c_ulong))[0])
        self.full_name = ""
        if self.cls:
            self.full_name = self.full_name + "%s." % (self.cls)

        if self.ident:
            self.full_name = self.full_name + "%s." % (self.ident)

        self.full_name = self.full_name + self.name

    def __str__(self):
        return "<%s %s = %s>" % (self.__class__.__name__, self.full_name,
                                 self.value)

    def __repr__(self):
        return "<%s %s = %s [%s]>" % (self.__class__.__name__,
                                      self.full_name,
                                      self.value,
                                      self.desc)

    def __eq__(self, other):
        return self.full_name == other.full_name


# stats
_VSC_Setup = varnishapi.VSC_Setup
_VSC_Setup.argtypes = [ctypes.POINTER(_VSM_data)]
_VSC_Setup.restype = None

_VSC_Open = varnishapi.VSC_Open
_VSC_Open.argtypes = [ctypes.POINTER(_VSM_data), ctypes.c_int]
_VSC_Open.restype = ctypes.c_int

_VSC_Arg = varnishapi.VSC_Arg
_VSC_Arg.argtypes = [ctypes.POINTER(_VSM_data), ctypes.c_int, ctypes.c_char_p]
_VSC_Arg.restype = ctypes.c_int

_VSC_Main = varnishapi.VSC_Main
_VSC_Main.argtypes = [ctypes.POINTER(_VSM_data)]
_VSC_Main.restype = ctypes.POINTER(_VSC_C_main)

_VSC_iter_f = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p,
                               ctypes.POINTER(_VSC_Point))
_VSC_Iter = varnishapi.VSC_Iter
_VSC_Iter.argtypes = [ctypes.POINTER(_VSM_data), _VSC_iter_f, ctypes.py_object]
_VSC_Iter.restype = ctypes.c_int


def setup(varnish_handle):
    """ Setup handle for use with stats functions """
    _VSC_Setup(varnish_handle)


def open_(varnish_handle, diagnostic=False):
    """ Open shared memory for stats processing """
    diag = 1 if diagnostic else 0
    if _VSC_Open(varnish_handle, diag) != 0:
        raise VarnishException('Error open shared memory for stats processing')


def main(varnish_handle):
    """ Return the main  handle """
    stats_handle = _VSC_Main(varnish_handle)
    if stats_handle is None:
        raise VarnishException('Cannot get main stats structure')

    return stats_handle


def init(varnish_handle, diagnostic=False):
    """ Shortcut function for stats processing setup """
    setup(varnish_handle)
    open_(varnish_handle, diagnostic)
    return main(varnish_handle)


def iterate(varnish_handle, callback, private_data=None):
    """ Iterate over all statistics counters calling callback for each counters
        not filtered out by pre-set filters
    """
    def _callback(priv, point):
        value = VarnishStatsPoint(point[0]) if not point is None else None
        if priv:
            priv = ctypes.cast(priv, ctypes.py_object).value

        try:
            res = callback(value, priv)

        except Exception as e:
            res = False
            _callback.exceptions = e

        else:
            res = 1 if res is False else 0

        finally:
            return res

    _callback.exception = None
    c_callback = _VSC_iter_f(_callback)

    if not private_data is None:
        private_data = ctypes.py_object(private_data)

    result = _VSC_Iter(varnish_handle, c_callback, private_data)
    if _callback.exception:
        raise _callback.exception

    return bool(result)


def filter_(varnish_handle, name, exclude=False):
    if exclude:
        name = "^%s" % (name)

    result = _VSC_Arg(varnish_handle, ord('f'), name)
    if result == -1:
        raise VarnishException('Cannot set filter %s' % (name))

    if result == 0:
        raise VarnishUnHandledException('Filter "f" unhandled: %s' % (name))


def exclude(varnish_handle, name):
    filter_(varnish_handle, name, exclude=True)
