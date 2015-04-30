'''Wrapper for varnishapi.h

Generated with:
/home/g.bagnoli/.virtualenvs/varnish/bin/ctypesgen.py -llibvarnishapi.so -o _libvarnish.py /usr/include/varnish/varnishapi.h

Do not modify this file.
'''

__docformat__ =  'restructuredtext'

# Begin preamble

import ctypes, os, sys
from ctypes import *

_int_types = (c_int16, c_int32)
if hasattr(ctypes, 'c_int64'):
    # Some builds of ctypes apparently do not have c_int64
    # defined; it's a pretty good bet that these builds do not
    # have 64-bit pointers.
    _int_types += (c_int64,)
for t in _int_types:
    if sizeof(t) == sizeof(c_size_t):
        c_ptrdiff_t = t
del t
del _int_types

class c_void(Structure):
    # c_void_p is a buggy return type, converting to int, so
    # POINTER(None) == c_void_p is actually written as
    # POINTER(c_void), so it can be treated as a real pointer.
    _fields_ = [('dummy', c_int)]

def POINTER(obj):
    p = ctypes.POINTER(obj)

    # Convert None to a real NULL pointer to work around bugs
    # in how ctypes handles None on 64-bit platforms
    if not isinstance(p.from_param, classmethod):
        def from_param(cls, x):
            if x is None:
                return cls()
            else:
                return x
        p.from_param = classmethod(from_param)

    return p

class UserString:
    def __init__(self, seq):
        if isinstance(seq, basestring):
            self.data = seq
        elif isinstance(seq, UserString):
            self.data = seq.data[:]
        else:
            self.data = str(seq)
    def __str__(self): return str(self.data)
    def __repr__(self): return repr(self.data)
    def __int__(self): return int(self.data)
    def __long__(self): return long(self.data)
    def __float__(self): return float(self.data)
    def __complex__(self): return complex(self.data)
    def __hash__(self): return hash(self.data)

    def __cmp__(self, string):
        if isinstance(string, UserString):
            return cmp(self.data, string.data)
        else:
            return cmp(self.data, string)
    def __contains__(self, char):
        return char in self.data

    def __len__(self): return len(self.data)
    def __getitem__(self, index): return self.__class__(self.data[index])
    def __getslice__(self, start, end):
        start = max(start, 0); end = max(end, 0)
        return self.__class__(self.data[start:end])

    def __add__(self, other):
        if isinstance(other, UserString):
            return self.__class__(self.data + other.data)
        elif isinstance(other, basestring):
            return self.__class__(self.data + other)
        else:
            return self.__class__(self.data + str(other))
    def __radd__(self, other):
        if isinstance(other, basestring):
            return self.__class__(other + self.data)
        else:
            return self.__class__(str(other) + self.data)
    def __mul__(self, n):
        return self.__class__(self.data*n)
    __rmul__ = __mul__
    def __mod__(self, args):
        return self.__class__(self.data % args)

    # the following methods are defined in alphabetical order:
    def capitalize(self): return self.__class__(self.data.capitalize())
    def center(self, width, *args):
        return self.__class__(self.data.center(width, *args))
    def count(self, sub, start=0, end=sys.maxint):
        return self.data.count(sub, start, end)
    def decode(self, encoding=None, errors=None): # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.decode(encoding, errors))
            else:
                return self.__class__(self.data.decode(encoding))
        else:
            return self.__class__(self.data.decode())
    def encode(self, encoding=None, errors=None): # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.encode(encoding, errors))
            else:
                return self.__class__(self.data.encode(encoding))
        else:
            return self.__class__(self.data.encode())
    def endswith(self, suffix, start=0, end=sys.maxint):
        return self.data.endswith(suffix, start, end)
    def expandtabs(self, tabsize=8):
        return self.__class__(self.data.expandtabs(tabsize))
    def find(self, sub, start=0, end=sys.maxint):
        return self.data.find(sub, start, end)
    def index(self, sub, start=0, end=sys.maxint):
        return self.data.index(sub, start, end)
    def isalpha(self): return self.data.isalpha()
    def isalnum(self): return self.data.isalnum()
    def isdecimal(self): return self.data.isdecimal()
    def isdigit(self): return self.data.isdigit()
    def islower(self): return self.data.islower()
    def isnumeric(self): return self.data.isnumeric()
    def isspace(self): return self.data.isspace()
    def istitle(self): return self.data.istitle()
    def isupper(self): return self.data.isupper()
    def join(self, seq): return self.data.join(seq)
    def ljust(self, width, *args):
        return self.__class__(self.data.ljust(width, *args))
    def lower(self): return self.__class__(self.data.lower())
    def lstrip(self, chars=None): return self.__class__(self.data.lstrip(chars))
    def partition(self, sep):
        return self.data.partition(sep)
    def replace(self, old, new, maxsplit=-1):
        return self.__class__(self.data.replace(old, new, maxsplit))
    def rfind(self, sub, start=0, end=sys.maxint):
        return self.data.rfind(sub, start, end)
    def rindex(self, sub, start=0, end=sys.maxint):
        return self.data.rindex(sub, start, end)
    def rjust(self, width, *args):
        return self.__class__(self.data.rjust(width, *args))
    def rpartition(self, sep):
        return self.data.rpartition(sep)
    def rstrip(self, chars=None): return self.__class__(self.data.rstrip(chars))
    def split(self, sep=None, maxsplit=-1):
        return self.data.split(sep, maxsplit)
    def rsplit(self, sep=None, maxsplit=-1):
        return self.data.rsplit(sep, maxsplit)
    def splitlines(self, keepends=0): return self.data.splitlines(keepends)
    def startswith(self, prefix, start=0, end=sys.maxint):
        return self.data.startswith(prefix, start, end)
    def strip(self, chars=None): return self.__class__(self.data.strip(chars))
    def swapcase(self): return self.__class__(self.data.swapcase())
    def title(self): return self.__class__(self.data.title())
    def translate(self, *args):
        return self.__class__(self.data.translate(*args))
    def upper(self): return self.__class__(self.data.upper())
    def zfill(self, width): return self.__class__(self.data.zfill(width))

class MutableString(UserString):
    """mutable string objects

    Python strings are immutable objects.  This has the advantage, that
    strings may be used as dictionary keys.  If this property isn't needed
    and you insist on changing string values in place instead, you may cheat
    and use MutableString.

    But the purpose of this class is an educational one: to prevent
    people from inventing their own mutable string class derived
    from UserString and than forget thereby to remove (override) the
    __hash__ method inherited from UserString.  This would lead to
    errors that would be very hard to track down.

    A faster and better solution is to rewrite your program using lists."""
    def __init__(self, string=""):
        self.data = string
    def __hash__(self):
        raise TypeError("unhashable type (it is mutable)")
    def __setitem__(self, index, sub):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data): raise IndexError
        self.data = self.data[:index] + sub + self.data[index+1:]
    def __delitem__(self, index):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data): raise IndexError
        self.data = self.data[:index] + self.data[index+1:]
    def __setslice__(self, start, end, sub):
        start = max(start, 0); end = max(end, 0)
        if isinstance(sub, UserString):
            self.data = self.data[:start]+sub.data+self.data[end:]
        elif isinstance(sub, basestring):
            self.data = self.data[:start]+sub+self.data[end:]
        else:
            self.data =  self.data[:start]+str(sub)+self.data[end:]
    def __delslice__(self, start, end):
        start = max(start, 0); end = max(end, 0)
        self.data = self.data[:start] + self.data[end:]
    def immutable(self):
        return UserString(self.data)
    def __iadd__(self, other):
        if isinstance(other, UserString):
            self.data += other.data
        elif isinstance(other, basestring):
            self.data += other
        else:
            self.data += str(other)
        return self
    def __imul__(self, n):
        self.data *= n
        return self

class String(MutableString, Union):

    _fields_ = [('raw', POINTER(c_char)),
                ('data', c_char_p)]

    def __init__(self, obj=""):
        if isinstance(obj, (str, unicode, UserString)):
            self.data = str(obj)
        else:
            self.raw = obj

    def __len__(self):
        return self.data and len(self.data) or 0

    def from_param(cls, obj):
        # Convert None or 0
        if obj is None or obj == 0:
            return cls(POINTER(c_char)())

        # Convert from String
        elif isinstance(obj, String):
            return obj

        # Convert from str
        elif isinstance(obj, str):
            return cls(obj)

        # Convert from c_char_p
        elif isinstance(obj, c_char_p):
            return obj

        # Convert from POINTER(c_char)
        elif isinstance(obj, POINTER(c_char)):
            return obj

        # Convert from raw pointer
        elif isinstance(obj, int):
            return cls(cast(obj, POINTER(c_char)))

        # Convert from object
        else:
            return String.from_param(obj._as_parameter_)
    from_param = classmethod(from_param)

def ReturnString(obj, func=None, arguments=None):
    return String.from_param(obj)

# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to c_void_p.
def UNCHECKED(type):
    if (hasattr(type, "_type_") and isinstance(type._type_, str)
        and type._type_ != "P"):
        return type
    else:
        return c_void_p

# ctypes doesn't have direct support for variadic functions, so we have to write
# our own wrapper class
class _variadic_function(object):
    def __init__(self,func,restype,argtypes):
        self.func=func
        self.func.restype=restype
        self.argtypes=argtypes
    def _as_parameter_(self):
        # So we can pass this variadic function as a function pointer
        return self.func
    def __call__(self,*args):
        fixed_args=[]
        i=0
        for argtype in self.argtypes:
            # Typecheck what we can
            fixed_args.append(argtype.from_param(args[i]))
            i+=1
        return self.func(*fixed_args+list(args[i:]))

# End preamble

_libs = {}
_libdirs = []

# Begin loader

# ----------------------------------------------------------------------------
# Copyright (c) 2008 David James
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

import os.path, re, sys, glob
import ctypes
import ctypes.util

def _environ_path(name):
    if name in os.environ:
        return os.environ[name].split(":")
    else:
        return []

class LibraryLoader(object):
    def __init__(self):
        self.other_dirs=[]

    def load_library(self,libname):
        """Given the name of a library, load it."""
        paths = self.getpaths(libname)

        for path in paths:
            if os.path.exists(path):
                return self.load(path)

        raise ImportError("%s not found." % libname)

    def load(self,path):
        """Given a path to a library, load it."""
        try:
            # Darwin requires dlopen to be called with mode RTLD_GLOBAL instead
            # of the default RTLD_LOCAL.  Without this, you end up with
            # libraries not being loadable, resulting in "Symbol not found"
            # errors
            if sys.platform == 'darwin':
                return ctypes.CDLL(path, ctypes.RTLD_GLOBAL)
            else:
                return ctypes.cdll.LoadLibrary(path)
        except OSError,e:
            raise ImportError(e)

    def getpaths(self,libname):
        """Return a list of paths where the library might be found."""
        if os.path.isabs(libname):
            yield libname

        else:
            for path in self.getplatformpaths(libname):
                yield path

            path = ctypes.util.find_library(libname)
            if path: yield path

    def getplatformpaths(self, libname):
        return []

# Darwin (Mac OS X)

class DarwinLibraryLoader(LibraryLoader):
    name_formats = ["lib%s.dylib", "lib%s.so", "lib%s.bundle", "%s.dylib",
                "%s.so", "%s.bundle", "%s"]

    def getplatformpaths(self,libname):
        if os.path.pathsep in libname:
            names = [libname]
        else:
            names = [format % libname for format in self.name_formats]

        for dir in self.getdirs(libname):
            for name in names:
                yield os.path.join(dir,name)

    def getdirs(self,libname):
        '''Implements the dylib search as specified in Apple documentation:

        http://developer.apple.com/documentation/DeveloperTools/Conceptual/
            DynamicLibraries/Articles/DynamicLibraryUsageGuidelines.html

        Before commencing the standard search, the method first checks
        the bundle's ``Frameworks`` directory if the application is running
        within a bundle (OS X .app).
        '''

        dyld_fallback_library_path = _environ_path("DYLD_FALLBACK_LIBRARY_PATH")
        if not dyld_fallback_library_path:
            dyld_fallback_library_path = [os.path.expanduser('~/lib'),
                                          '/usr/local/lib', '/usr/lib']

        dirs = []

        if '/' in libname:
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
        else:
            dirs.extend(_environ_path("LD_LIBRARY_PATH"))
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))

        dirs.extend(self.other_dirs)
        dirs.append(".")

        if hasattr(sys, 'frozen') and sys.frozen == 'macosx_app':
            dirs.append(os.path.join(
                os.environ['RESOURCEPATH'],
                '..',
                'Frameworks'))

        dirs.extend(dyld_fallback_library_path)

        return dirs

# Posix

class PosixLibraryLoader(LibraryLoader):
    _ld_so_cache = None

    def _create_ld_so_cache(self):
        # Recreate search path followed by ld.so.  This is going to be
        # slow to build, and incorrect (ld.so uses ld.so.cache, which may
        # not be up-to-date).  Used only as fallback for distros without
        # /sbin/ldconfig.
        #
        # We assume the DT_RPATH and DT_RUNPATH binary sections are omitted.

        directories = []
        for name in ("LD_LIBRARY_PATH",
                     "SHLIB_PATH", # HPUX
                     "LIBPATH", # OS/2, AIX
                     "LIBRARY_PATH", # BE/OS
                    ):
            if name in os.environ:
                directories.extend(os.environ[name].split(os.pathsep))
        directories.extend(self.other_dirs)
        directories.append(".")

        try: directories.extend([dir.strip() for dir in open('/etc/ld.so.conf')])
        except IOError: pass

        directories.extend(['/lib', '/usr/lib', '/lib64', '/usr/lib64'])

        cache = {}
        lib_re = re.compile(r'lib(.*)\.s[ol]')
        ext_re = re.compile(r'\.s[ol]$')
        for dir in directories:
            try:
                for path in glob.glob("%s/*.s[ol]*" % dir):
                    file = os.path.basename(path)

                    # Index by filename
                    if file not in cache:
                        cache[file] = path

                    # Index by library name
                    match = lib_re.match(file)
                    if match:
                        library = match.group(1)
                        if library not in cache:
                            cache[library] = path
            except OSError:
                pass

        self._ld_so_cache = cache

    def getplatformpaths(self, libname):
        if self._ld_so_cache is None:
            self._create_ld_so_cache()

        result = self._ld_so_cache.get(libname)
        if result: yield result

        path = ctypes.util.find_library(libname)
        if path: yield os.path.join("/lib",path)

# Windows

class _WindowsLibrary(object):
    def __init__(self, path):
        self.cdll = ctypes.cdll.LoadLibrary(path)
        self.windll = ctypes.windll.LoadLibrary(path)

    def __getattr__(self, name):
        try: return getattr(self.cdll,name)
        except AttributeError:
            try: return getattr(self.windll,name)
            except AttributeError:
                raise

class WindowsLibraryLoader(LibraryLoader):
    name_formats = ["%s.dll", "lib%s.dll", "%slib.dll"]

    def load_library(self, libname):
        try:
            result = LibraryLoader.load_library(self, libname)
        except ImportError:
            result = None
            if os.path.sep not in libname:
                for name in self.name_formats:
                    try:
                        result = getattr(ctypes.cdll, name % libname)
                        if result:
                            break
                    except WindowsError:
                        result = None
            if result is None:
                try:
                    result = getattr(ctypes.cdll, libname)
                except WindowsError:
                    result = None
            if result is None:
                raise ImportError("%s not found." % libname)
        return result

    def load(self, path):
        return _WindowsLibrary(path)

    def getplatformpaths(self, libname):
        if os.path.sep not in libname:
            for name in self.name_formats:
                dll_in_current_dir = os.path.abspath(name % libname)
                if os.path.exists(dll_in_current_dir):
                    yield dll_in_current_dir
                path = ctypes.util.find_library(name % libname)
                if path:
                    yield path

# Platform switching

# If your value of sys.platform does not appear in this dict, please contact
# the Ctypesgen maintainers.

loaderclass = {
    "darwin":   DarwinLibraryLoader,
    "cygwin":   WindowsLibraryLoader,
    "win32":    WindowsLibraryLoader
}

loader = loaderclass.get(sys.platform, PosixLibraryLoader)()

def add_library_search_dirs(other_dirs):
    loader.other_dirs = other_dirs

load_library = loader.load_library

del loaderclass

# End loader

add_library_search_dirs([])

# Begin libraries

_libs["libvarnishapi.so"] = load_library("libvarnishapi.so")

# 1 libraries
# End libraries

# No modules

enum_VSL_tag_e = c_int # /usr/include/varnish/vsl.h: 68

# /usr/include/varnish/varnishapi.h: 49
class struct_VSM_data(Structure):
    pass

# /usr/include/varnish/varnishapi.h: 49
if hasattr(_libs['libvarnishapi.so'], 'VSM_New'):
    VSM_New = _libs['libvarnishapi.so'].VSM_New
    VSM_New.argtypes = []
    VSM_New.restype = POINTER(struct_VSM_data)

VSM_diag_f = CFUNCTYPE(UNCHECKED(None), POINTER(None), String) # /usr/include/varnish/varnishapi.h: 59

# /usr/include/varnish/varnishapi.h: 61
if hasattr(_libs['libvarnishapi.so'], 'VSM_Diag'):
    VSM_Diag = _libs['libvarnishapi.so'].VSM_Diag
    VSM_Diag.argtypes = [POINTER(struct_VSM_data), POINTER(VSM_diag_f), POINTER(None)]
    VSM_Diag.restype = None

# /usr/include/varnish/varnishapi.h: 70
if hasattr(_libs['libvarnishapi.so'], 'VSM_n_Arg'):
    VSM_n_Arg = _libs['libvarnishapi.so'].VSM_n_Arg
    VSM_n_Arg.argtypes = [POINTER(struct_VSM_data), String]
    VSM_n_Arg.restype = c_int

# /usr/include/varnish/varnishapi.h: 80
if hasattr(_libs['libvarnishapi.so'], 'VSM_Name'):
    VSM_Name = _libs['libvarnishapi.so'].VSM_Name
    VSM_Name.argtypes = [POINTER(struct_VSM_data)]
    if sizeof(c_int) == sizeof(c_void_p):
        VSM_Name.restype = ReturnString
    else:
        VSM_Name.restype = String
        VSM_Name.errcheck = ReturnString

# /usr/include/varnish/varnishapi.h: 85
if hasattr(_libs['libvarnishapi.so'], 'VSM_Delete'):
    VSM_Delete = _libs['libvarnishapi.so'].VSM_Delete
    VSM_Delete.argtypes = [POINTER(struct_VSM_data)]
    VSM_Delete.restype = None

# /usr/include/varnish/varnishapi.h: 92
if hasattr(_libs['libvarnishapi.so'], 'VSM_Open'):
    VSM_Open = _libs['libvarnishapi.so'].VSM_Open
    VSM_Open.argtypes = [POINTER(struct_VSM_data), c_int]
    VSM_Open.restype = c_int

# /usr/include/varnish/varnishapi.h: 101
if hasattr(_libs['libvarnishapi.so'], 'VSM_ReOpen'):
    VSM_ReOpen = _libs['libvarnishapi.so'].VSM_ReOpen
    VSM_ReOpen.argtypes = [POINTER(struct_VSM_data), c_int]
    VSM_ReOpen.restype = c_int

# /usr/include/varnish/varnishapi.h: 112
if hasattr(_libs['libvarnishapi.so'], 'VSM_Seq'):
    VSM_Seq = _libs['libvarnishapi.so'].VSM_Seq
    VSM_Seq.argtypes = [POINTER(struct_VSM_data)]
    VSM_Seq.restype = c_uint

# /usr/include/varnish/varnishapi.h: 117
class struct_VSM_head(Structure):
    pass

# /usr/include/varnish/varnishapi.h: 117
if hasattr(_libs['libvarnishapi.so'], 'VSM_Head'):
    VSM_Head = _libs['libvarnishapi.so'].VSM_Head
    VSM_Head.argtypes = [POINTER(struct_VSM_data)]
    VSM_Head.restype = POINTER(struct_VSM_head)

# /usr/include/varnish/varnishapi.h: 122
if hasattr(_libs['libvarnishapi.so'], 'VSM_Find_Chunk'):
    VSM_Find_Chunk = _libs['libvarnishapi.so'].VSM_Find_Chunk
    VSM_Find_Chunk.argtypes = [POINTER(struct_VSM_data), String, String, String, POINTER(c_uint)]
    VSM_Find_Chunk.restype = POINTER(None)

# /usr/include/varnish/varnishapi.h: 130
if hasattr(_libs['libvarnishapi.so'], 'VSM_Close'):
    VSM_Close = _libs['libvarnishapi.so'].VSM_Close
    VSM_Close.argtypes = [POINTER(struct_VSM_data)]
    VSM_Close.restype = None

# /usr/include/varnish/varnishapi.h: 136
class struct_VSM_chunk(Structure):
    pass

# /usr/include/varnish/varnishapi.h: 136
if hasattr(_libs['libvarnishapi.so'], 'VSM_iter0'):
    VSM_iter0 = _libs['libvarnishapi.so'].VSM_iter0
    VSM_iter0.argtypes = [POINTER(struct_VSM_data)]
    VSM_iter0.restype = POINTER(struct_VSM_chunk)

# /usr/include/varnish/varnishapi.h: 137
for _lib in _libs.itervalues():
    if not hasattr(_lib, 'VSM_itern'):
        continue
    VSM_itern = _lib.VSM_itern
    VSM_itern.argtypes = [POINTER(struct_VSM_data), POINTER(POINTER(struct_VSM_chunk))]
    VSM_itern.restype = None
    break

# /usr/include/varnish/varnishapi.h: 152
if hasattr(_libs['libvarnishapi.so'], 'VSC_Setup'):
    VSC_Setup = _libs['libvarnishapi.so'].VSC_Setup
    VSC_Setup.argtypes = [POINTER(struct_VSM_data)]
    VSC_Setup.restype = None

# /usr/include/varnish/varnishapi.h: 161
if hasattr(_libs['libvarnishapi.so'], 'VSC_Arg'):
    VSC_Arg = _libs['libvarnishapi.so'].VSC_Arg
    VSC_Arg.argtypes = [POINTER(struct_VSM_data), c_int, String]
    VSC_Arg.restype = c_int

# /usr/include/varnish/varnishapi.h: 170
if hasattr(_libs['libvarnishapi.so'], 'VSC_Open'):
    VSC_Open = _libs['libvarnishapi.so'].VSC_Open
    VSC_Open.argtypes = [POINTER(struct_VSM_data), c_int]
    VSC_Open.restype = c_int

# /usr/include/varnish/varnishapi.h: 176
class struct_VSC_C_main(Structure):
    pass

# /usr/include/varnish/varnishapi.h: 176
if hasattr(_libs['libvarnishapi.so'], 'VSC_Main'):
    VSC_Main = _libs['libvarnishapi.so'].VSC_Main
    VSC_Main.argtypes = [POINTER(struct_VSM_data)]
    VSC_Main.restype = POINTER(struct_VSC_C_main)

# /usr/include/varnish/varnishapi.h: 181
class struct_VSC_point(Structure):
    pass

struct_VSC_point.__slots__ = [
    '_class',
    'ident',
    'name',
    'fmt',
    'flag',
    'desc',
    'ptr',
]
struct_VSC_point._fields_ = [
    ('_class', String),
    ('ident', String),
    ('name', String),
    ('fmt', String),
    ('flag', c_int),
    ('desc', String),
    ('ptr', POINTER(None)),
]

VSC_iter_f = CFUNCTYPE(UNCHECKED(c_int), POINTER(None), POINTER(struct_VSC_point)) # /usr/include/varnish/varnishapi.h: 191

# /usr/include/varnish/varnishapi.h: 193
if hasattr(_libs['libvarnishapi.so'], 'VSC_Iter'):
    VSC_Iter = _libs['libvarnishapi.so'].VSC_Iter
    VSC_Iter.argtypes = [POINTER(struct_VSM_data), POINTER(VSC_iter_f), POINTER(None)]
    VSC_Iter.restype = c_int

# /usr/include/varnish/varnishapi.h: 203
if hasattr(_libs['libvarnishapi.so'], 'VSL_Setup'):
    VSL_Setup = _libs['libvarnishapi.so'].VSL_Setup
    VSL_Setup.argtypes = [POINTER(struct_VSM_data)]
    VSL_Setup.restype = None

# /usr/include/varnish/varnishapi.h: 208
if hasattr(_libs['libvarnishapi.so'], 'VSL_Open'):
    VSL_Open = _libs['libvarnishapi.so'].VSL_Open
    VSL_Open.argtypes = [POINTER(struct_VSM_data), c_int]
    VSL_Open.restype = c_int

# /usr/include/varnish/varnishapi.h: 242
if hasattr(_libs['libvarnishapi.so'], 'VSL_Arg'):
    VSL_Arg = _libs['libvarnishapi.so'].VSL_Arg
    VSL_Arg.argtypes = [POINTER(struct_VSM_data), c_int, String]
    VSL_Arg.restype = c_int

VSL_handler_f = CFUNCTYPE(UNCHECKED(c_int), POINTER(None), enum_VSL_tag_e, c_uint, c_uint, c_uint, String, c_uint64) # /usr/include/varnish/varnishapi.h: 251

# /usr/include/varnish/varnishapi.h: 256
try:
    VSL_H_Print = (VSL_handler_f).in_dll(_libs['libvarnishapi.so'], 'VSL_H_Print')
except:
    pass

# /usr/include/varnish/varnishapi.h: 258
if hasattr(_libs['libvarnishapi.so'], 'VSL_Select'):
    VSL_Select = _libs['libvarnishapi.so'].VSL_Select
    VSL_Select.argtypes = [POINTER(struct_VSM_data), c_uint]
    VSL_Select.restype = None

# /usr/include/varnish/varnishapi.h: 259
if hasattr(_libs['libvarnishapi.so'], 'VSL_NonBlocking'):
    VSL_NonBlocking = _libs['libvarnishapi.so'].VSL_NonBlocking
    VSL_NonBlocking.argtypes = [POINTER(struct_VSM_data), c_int]
    VSL_NonBlocking.restype = None

# /usr/include/varnish/varnishapi.h: 260
if hasattr(_libs['libvarnishapi.so'], 'VSL_Dispatch'):
    VSL_Dispatch = _libs['libvarnishapi.so'].VSL_Dispatch
    VSL_Dispatch.argtypes = [POINTER(struct_VSM_data), POINTER(VSL_handler_f), POINTER(None)]
    VSL_Dispatch.restype = c_int

# /usr/include/varnish/varnishapi.h: 261
if hasattr(_libs['libvarnishapi.so'], 'VSL_NextLog'):
    VSL_NextLog = _libs['libvarnishapi.so'].VSL_NextLog
    VSL_NextLog.argtypes = [POINTER(struct_VSM_data), POINTER(POINTER(c_uint32)), POINTER(c_uint64)]
    VSL_NextLog.restype = c_int

# /usr/include/varnish/varnishapi.h: 262
if hasattr(_libs['libvarnishapi.so'], 'VSL_Matched'):
    VSL_Matched = _libs['libvarnishapi.so'].VSL_Matched
    VSL_Matched.argtypes = [POINTER(struct_VSM_data), c_uint64]
    VSL_Matched.restype = c_int

# /usr/include/varnish/varnishapi.h: 263
for _lib in _libs.itervalues():
    if not hasattr(_lib, 'VSL_Name2Tag'):
        continue
    VSL_Name2Tag = _lib.VSL_Name2Tag
    VSL_Name2Tag.argtypes = [String, c_int]
    VSL_Name2Tag.restype = c_int
    break

# /usr/include/varnish/varnishapi.h: 264
try:
    VSL_tags = (POINTER(c_char) * 256).in_dll(_libs['libvarnishapi.so'], 'VSL_tags')
except:
    pass

# /usr/include/varnish/varnishapi.h: 68
try:
    VSM_n_USAGE = '[-n varnish_name]'
except:
    pass

# /usr/include/varnish/varnishapi.h: 157
try:
    VSC_ARGS = 'f:n:'
except:
    pass

# /usr/include/varnish/varnishapi.h: 158
try:
    VSC_n_USAGE = VSM_n_USAGE
except:
    pass

# /usr/include/varnish/varnishapi.h: 217
try:
    VSL_ARGS = 'bCcdI:i:k:n:r:s:X:x:m:'
except:
    pass

# /usr/include/varnish/varnishapi.h: 218
try:
    VSL_b_USAGE = '[-b]'
except:
    pass

# /usr/include/varnish/varnishapi.h: 219
try:
    VSL_c_USAGE = '[-c]'
except:
    pass

# /usr/include/varnish/varnishapi.h: 220
try:
    VSL_C_USAGE = '[-C]'
except:
    pass

# /usr/include/varnish/varnishapi.h: 221
try:
    VSL_d_USAGE = '[-d]'
except:
    pass

# /usr/include/varnish/varnishapi.h: 222
try:
    VSL_i_USAGE = '[-i tag]'
except:
    pass

# /usr/include/varnish/varnishapi.h: 223
try:
    VSL_I_USAGE = '[-I regexp]'
except:
    pass

# /usr/include/varnish/varnishapi.h: 224
try:
    VSL_k_USAGE = '[-k keep]'
except:
    pass

# /usr/include/varnish/varnishapi.h: 225
try:
    VSL_m_USAGE = '[-m tag:regex]'
except:
    pass

# /usr/include/varnish/varnishapi.h: 226
try:
    VSL_n_USAGE = VSM_n_USAGE
except:
    pass

# /usr/include/varnish/varnishapi.h: 227
try:
    VSL_r_USAGE = '[-r file]'
except:
    pass

# /usr/include/varnish/varnishapi.h: 228
try:
    VSL_s_USAGE = '[-s skip]'
except:
    pass

# /usr/include/varnish/varnishapi.h: 229
try:
    VSL_x_USAGE = '[-x tag]'
except:
    pass

# /usr/include/varnish/varnishapi.h: 230
try:
    VSL_X_USAGE = '[-X regexp]'
except:
    pass

# /usr/include/varnish/varnishapi.h: 254
try:
    VSL_S_CLIENT = (1 << 0)
except:
    pass

# /usr/include/varnish/varnishapi.h: 255
try:
    VSL_S_BACKEND = (1 << 1)
except:
    pass

VSM_data = struct_VSM_data # /usr/include/varnish/varnishapi.h: 49

VSM_head = struct_VSM_head # /usr/include/varnish/varnishapi.h: 117

VSM_chunk = struct_VSM_chunk # /usr/include/varnish/varnishapi.h: 136

VSC_C_main = struct_VSC_C_main # /usr/include/varnish/varnishapi.h: 176

VSC_point = struct_VSC_point # /usr/include/varnish/varnishapi.h: 181

# No inserted files

