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
from ..exc import VarnishException


log = logging.getLogger(__name__)
__all__ = ['init', 'open', 'reopen', 'close', 'delete',
           'clear_diagnostic_function', 'set_diagnostic_function',
           'access_instance']
varnishapi = ctypes.CDLL('libvarnishapi.so.1')


# STRUCTURES
class _VSM_data(ctypes.Structure):
    pass


_VSM_New = varnishapi.VSM_New
_VSM_New.argtypes = []
_VSM_New.restype = ctypes.POINTER(_VSM_data)

_VSM_Open = varnishapi.VSM_Open
_VSM_Open.argtypes = [ctypes.POINTER(_VSM_data), ctypes.c_int]
_VSM_Open.restype = ctypes.c_int

_VSM_ReOpen = varnishapi.VSM_ReOpen
_VSM_ReOpen.argtypes = [ctypes.POINTER(_VSM_data), ctypes.c_int]
_VSM_ReOpen.restype = ctypes.c_int

_VSM_diag_f = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
_VSM_Diag = varnishapi.VSM_Diag
_VSM_Diag.argtypes = [ctypes.POINTER(_VSM_data), _VSM_diag_f, ctypes.py_object]
_VSM_Diag.restype = None

_VSM_n_Arg = varnishapi.VSM_n_Arg
_VSM_n_Arg.argtypes = [ctypes.POINTER(_VSM_data), ctypes.c_char_p]
_VSM_n_Arg.restype = ctypes.c_int

_VSM_Close = varnishapi.VSM_Close
_VSM_Close.argtypes = [ctypes.POINTER(_VSM_data)]
_VSM_Close.restype = None

_VSM_Delete = varnishapi.VSM_Close
_VSM_Delete.argtypes = [ctypes.POINTER(_VSM_data)]
_VSM_Delete.restype = None


def init():
    """ Allocate and initialize the handle used in the C API.
        This is the first thing you have to do.
        You can have multiple active handles at the same time referencing the
        same or different shared memory files
    """
    handle = _VSM_New()
    if not handle:
        raise VarnishException('Cannot initialize varnish C API')

    log.debug("Initialized varnish C API (handle at %s)", handle)
    return handle


def open(varnish_handle, diagnostic=False):
    diag = 1 if diagnostic else 0
    res = _VSM_Open(varnish_handle, diag)
    if res != 0:
        raise VarnishException('Failed to open and map shared memory file')


def reopen(varnish_handle, diagnostic=False):
    diag = 1 if diagnostic else 0
    res = _VSM_ReOpen(varnish_handle, diag)
    if res < 0:
        raise VarnishException('Failed to reopen and remap shared memory file')


def close(varnish_handle):
    _VSM_Close(varnish_handle)


def delete(varnish_handle):
    _VSM_Delete(varnish_handle)


def set_diagnostic_function(varnish_handle, function, private_data):
    """ Set the diagnostic reporting function """

    def _function(priv, fmt, *args):
        if priv:
            priv = ctypes.cast(priv, ctypes.py_object).value
        function(priv, fmt, *args)

    c_function = _VSM_diag_f(_function)
    if not private_data is None:
        private_data = ctypes.py_object(private_data)

    _VSM_Diag(varnish_handle, c_function, private_data)


def clear_diagnostic_function(varnish_handle):
    """ Remove a previously set diagnostic reporting function """
    _VSM_Diag(varnish_handle, None, None)


def access_instance(varnish_handle, instance_name):
    """ Configure which varnish instance to access """
    if _VSM_n_Arg(varnish_handle, instance_name) != 1:
        raise VarnishException('Cannot access instance %s', instance_name)
