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
import ctypes
import logging
from .vsm import _VSM_data
from ..exc import (VarnishException,
                   VarnishUnHandledException)


__all__ = ['setup', 'init', 'open_', 'name_to_tag', 'dispatch', 'next',
           'process_old_entries', 'process_backend_requests',
           'process_client_requests', 'include_tag', 'include_tag_regex',
           'exclude_tag',  'exclude_tag_regex', 'stop_after', 'skip_first',
           'read_entries_from_file', 'filter_transactions_by_tag_regex',
           'ignore_case_in_regex']
varnishapi = ctypes.CDLL('libvarnishapi.so.1')
log = logging.getLogger(__name__)


LogTag = collections.namedtuple('LogTag', ['code', 'name'])


class LogTags(collections.Mapping):

    def __new__(cls):
        if '_inst' not in vars(cls):
            cls._inst = super(LogTags, cls).__new__(cls)
            cls._inst._tags_by_code = dict()
            cls._inst._tags_by_name = dict()
            for code in xrange(_VSL_tags_len):
                name = _VSL_tags[code]
                if not name is None:
                    name = name.lower()
                    tag = LogTag(code=code, name=name)
                    cls._inst._tags_by_code[code] = tag
                    cls._inst._tags_by_name[name] = tag

        return cls._inst

    def _to_code(self, key):
        if isinstance(key, basestring):
            if _VSL_Name2Tag:
                res = _VSL_Name2Tag(key, -1)
                if res == -1:
                    return KeyError('No tag %s' % key)

                if res == -2:
                    raise KeyError("Multiple code for %s" % key)

                return res
            else:
                key = key.lower()
                return self._tags_by_name[key].code

        else:
            return key

    def __getitem__(self, key):
        key = self._to_code(key)
        return self._tags_by_code[key]

    def __iter__(self):
        return iter(self._tags_by_name)

    def __contains__(self, key):
        key = self._to_code(key)
        return key in self._tags_by_code

    def __len__(self):
        return len(self._tags_by_code)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return repr(self._tags_by_name)


class LogChunk(object):
    """ Python object that represent a log entry """
    tags = None

    def __init__(self, tag, fd, len_, spec, ptr, bitmap):
        if not self.__class__.tags:
            self.__class__.tags = LogTags()
        self.tag = self.tags[tag]
        self.fd = int(fd)  # file descriptor associated with this record
        self.client = spec == _VSL_S_CLIENT
        self.backend = spec == _VSL_S_BACKEND
        self.data = str(ptr)[0:len_]
        self.bitmap = int(bitmap)

    def __str__(self):
        type_ = "client" if self.client else "backend"
        return "<LogChunk [%s] [%s] [%s]: %s>" % (self.fd, type_,
                                                  self.tag.name,
                                                  self.data.strip())

    def __repr__(self):
        return str(self)


# logs
_VSL_S_CLIENT = (1 << 0)
_VSL_S_BACKEND = (1 << 1)
_VSL_tags_len = 256
_VSL_tags = (ctypes.c_char_p * _VSL_tags_len).in_dll(varnishapi, 'VSL_tags')

try:
    _VSL_Name2Tag = varnishapi.VSL_Name2Tag
    _VSL_Name2Tag.argtypes = [ctypes.c_char_p, ctypes.c_int]
    _VSL_Name2Tag.restype = ctypes.c_int

except AttributeError:
    _VSL_Name2Tag = None

_VSL_Setup = varnishapi.VSL_Setup
_VSL_Setup.argtypes = [ctypes.POINTER(_VSM_data)]
_VSL_Setup.restype = None

_VSL_Open = varnishapi.VSL_Open
_VSL_Open.argtypes = [ctypes.POINTER(_VSM_data), ctypes.c_int]
_VSL_Open.restype = ctypes.c_int

_VSL_Arg = varnishapi.VSL_Arg
_VSL_Arg.argtypes = [ctypes.POINTER(_VSM_data), ctypes.c_int, ctypes.c_char_p]
_VSL_Arg.restype = ctypes.c_int


                                # return,       priv,
                                # tag,          fd,
                                # len,          spec,
                                # ptr,          bitmap
_VSL_handler_f = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p,
                                  ctypes.c_int, ctypes.c_uint,
                                  ctypes.c_uint, ctypes.c_uint,
                                  ctypes.c_char_p, ctypes.c_uint64)
_VSL_Dispatch = varnishapi.VSL_Dispatch
_VSL_Dispatch.argtypes = [ctypes.POINTER(_VSM_data),
                          _VSL_handler_f, ctypes.py_object]
_VSL_Dispatch.restype = ctypes.c_int

_VSL_NextLog = varnishapi.VSL_NextLog
_VSL_NextLog.argtypes = [ctypes.POINTER(_VSM_data),
                         ctypes.POINTER(ctypes.POINTER(ctypes.c_uint32)),
                         ctypes.POINTER(ctypes.c_uint64)]
_VSL_NextLog.restype = ctypes.c_int


def setup(varnish_handle):
    """ Setup handle for use with logs functions """
    log.debug("Setting up handle at %s for use with log functions",
              varnish_handle)
    _VSL_Setup(varnish_handle)


def open_(varnish_handle, diagnostic=False):
    """ Attempt to open and map the shared memory file. """
    log.debug("Opening and mapping handle at %s for use with log functions",
              varnish_handle)
    diag = 1 if diagnostic else 0
    if _VSL_Open(varnish_handle, diag) != 0:
        raise VarnishException('Error open shared memory for logs processing')


def init(varnish_handle, diagnostic=False):
    """ Shortcut function for logs processing setup """
    setup(varnish_handle)
    open_(varnish_handle, diagnostic)


def name_to_tag(name, match_length=-1):
    """ Converts a name to a log tag code.
        match_length == -1 means len(name)
        Returns -1 if no tag matches
                -2 if multiple matches are found
                >= 0 tag code
    """
    try:
        tagcode = LogTags()[name]

    except KeyError:
        return -1

    else:
        return tagcode


def dispatch(varnish_handle, callback, private_data=None):
    def _callback(priv, tag, fd, len_, spec, ptr, bitmap):
        if priv:
            priv = ctypes.cast(priv, ctypes.py_object).value

        res = True
        try:
            lchunk = LogChunk(tag, fd, len_, spec, ptr, bitmap)

        except:
            return res
        try:
            res = callback(lchunk, priv)

        except Exception as e:
            res = False
            _callback.exception = e

        finally:
            res = 1 if res is False else 0
            return res

    # add an exception attr to callback, used to collect and re-raise eventual
    # exceptions raised in user callback
    _callback.exception = None

    c_callback = _VSL_handler_f(_callback)
    if not private_data is None:
        private_data = ctypes.py_object(private_data)

    log.debug("Calling dispatch with callback at %s", callback)
    result = _VSL_Dispatch(varnish_handle, c_callback, private_data)

    if _callback.exception:
        raise _callback.exception

    return bool(result)


def arg_(varnish_handle, flag, option=None):
    result = _VSL_Arg(varnish_handle, ord(flag), option)
    if result == -1:
        raise VarnishException('Cannot set filter %s = %s' % (flag, option))

    if result == 0:
        raise VarnishUnHandledException('Filter "%s" unhandled: %s' % (flag,
                                                                      option))


def process_old_entries(varnish_handle):
    arg_(varnish_handle, 'd')


def process_client_requests(varnish_handle):
    arg_(varnish_handle, 'c')


def process_backend_requests(varnish_handle):
    arg_(varnish_handle, 'b')


def include_tag(varnish_handle, tag):
    arg_(varnish_handle, 'i', tag)


def include_tag_regex(varnish_handle, tag_regex):
    arg_(varnish_handle, 'I', tag_regex)


def stop_after(varnish_handle, num):
    arg_(varnish_handle, 'k', str(num))


def read_entries_from_file(varnish_handle, filename):
    arg_(varnish_handle, 'r', filename)


def skip_first(varnish_handle, num):
    arg_(varnish_handle, 's', str(num))


def exclude_tag(varnish_handle, tag):
    arg_(varnish_handle, 'x', tag)


def exclude_tag_regex(varnish_handle, tag_regex):
    arg_(varnish_handle, 'X', tag_regex)


def filter_transactions_by_tag_regex(varnish_handle, tag, regex):
    arg_(varnish_handle, 'm', "{0}:{1}".format(tag, regex))


def ignore_case_in_regex(varnish_handle):
    arg_(varnish_handle, 'C')


def next(varnish_handle):

    raise NotImplementedError()
    # raw_log = ctypes.POINTER(ctypes.c_uint32)()
    # bitmap = ctypes.c_uint64(0)
    # result = _VSL_NextLog(varnish_handle,
    #                       ctypes.byref(raw_log),
    #                       ctypes.byref(bitmap))
    # print result
    # if result != 1:
    #     return None

    # tag = raw_log[0] >> 24
    # fd = raw_log[1]
    # len_ = raw_log[0] & 0xffff
    # # FIXME
    # data = ctypes.cast(raw_log, ctypes.c_void_p)
    # data.value += 2
    # data = ctypes.cast(data, ctypes.c_char_p)

    # spec = 0  # fixme
    # return LogChunk(tag, fd, len_, spec, data.value, bitmap.value)
