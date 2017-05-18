# vi: set ft=python sw=4 ts=4 et:

'''monotonic time for Python 2 and 3, on Linux, FreeBSD, Mac OS X, and Windows.

Copyright 2010, 2011, 2017 Gavin Beatty <gavinbeatty@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Gavin Beatty <gavinbeatty@gmail.com>'
__version__ = '2.0.2.dev0'
__date__ = '2017-05-15'
__all__ = ['monotonic']

try:
    import ctypes
    _use = 'ctypes'

    class _mach_timespec(ctypes.Structure):
        _fields_ = [('tv_sec', ctypes.c_uint), ('tv_nsec', ctypes.c_int)]

    class _posix_timespec(ctypes.Structure):
        _fields_ = [('tv_sec', ctypes.c_long), ('tv_nsec', ctypes.c_long)]
except ImportError:
    import cffi
    _ffi = cffi.FFI()
    _use = 'cffi'
import errno
import os
import platform
import sys
import time


_machine64 = (platform.machine(), sys.maxsize > 2**32)


class _NS():
    pass


def _timespec_to_seconds(ts):
    return float(ts.tv_sec) + float(ts.tv_nsec) * 1e-9


def _get_ctypes_macho_functions():
    libmacho = ctypes.CDLL('/usr/lib/system/libmacho.dylib', use_errno=True)
    macho = _NS()
    macho.get_host = libmacho.mach_host_self
    macho.get_host.argtypes = []
    macho.get_host.restype = ctypes.c_uint
    macho.get_clock = libmacho.host_get_clock_service
    macho.get_clock.argtypes = [ctypes.c_uint,
                                ctypes.c_int,
                                ctypes.POINTER(ctypes.c_uint)
                                ]
    macho.get_time = libmacho.clock_get_time
    macho.get_time.argtypes = [ctypes.c_uint, ctypes.POINTER(_mach_timespec)]
    macho.get_task = libmacho.mach_task_self
    macho.get_task.restype = ctypes.c_uint
    macho.deallocate = libmacho.mach_port_deallocate
    macho.deallocate.argtypes = [ctypes.c_uint, ctypes.c_uint]
    return macho


def _get_ctypes_clock_gettime(library):
    clock_gettime = ctypes.CDLL(library, use_errno=True).clock_gettime
    clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(_posix_timespec)]
    return clock_gettime


def _call_ctypes_clock_gettime(clock_gettime, clockid):
    timespec = _posix_timespec()
    ret = clock_gettime(clockid, ctypes.pointer(timespec))
    if int(ret) != 0:
        errno_ = ctypes.get_errno()
        raise OSError(errno_, os.strerror(errno_))
    return timespec


def _call_cffi_clock_gettime(ffi, clock_gettime, clockid):
    timespecptr = ffi.new('struct posix_timespec *')
    ret = clock_gettime(clockid, timespecptr)
    if int(ret) != 0:
        errno_ = int(ffi.errno)
        raise OSError(errno_, os.strerror(errno_))
    return timespecptr


_py_monotonic = getattr(time, 'monotonic', None)
if _py_monotonic is not None:
    monotonic = _py_monotonic
elif sys.platform.startswith('linux'):
    if _use == 'ctypes':
        _clock_gettime = _get_ctypes_clock_gettime('librt.so.1')

        def monotonic():
            clockid = ctypes.c_int(1)
            timespec = _call_ctypes_clock_gettime(_clock_gettime, clockid)
            return _timespec_to_seconds(timespec)
    elif _use == 'cffi':
        _ffi.cdef('''
            struct posix_timespec { long tv_sec; long tv_nsec; };
            int clock_gettime(int, struct posix_timespec *);
        ''')
        _rt = _ffi.dlopen('librt.so.1')

        def monotonic():
            clockid = _ffi.cast('int', 4)
            clock_gettime = _rt.clock_gettime
            timespec = _call_cffi_clock_gettime(_ffi, clock_gettime, clockid)
            return _timespec_to_seconds(timespec)
    else:
        raise RuntimeError('ctypes or cffi must be supported')
elif sys.platform.startswith('freebsd'):
    if _use == 'ctypes':
        _clock_gettime = _get_ctypes_clock_gettime('libc.so')

        def monotonic():
            clockid = ctypes.c_int(4)
            timespec = _call_ctypes_clock_gettime(_clock_gettime, clockid)
            return _timespec_to_seconds(timespec)
    elif _use == 'cffi':
        _ffi.cdef('''
            struct posix_timespec { long tv_sec; long tv_nsec; };
            int clock_gettime(int, struct posix_timespec *);
        ''')
        _rt = _ffi.dlopen('libc.so')

        def monotonic():
            clockid = _ffi.cast('int', 4)
            clock_gettime = _rt.clock_gettime
            timespec = _call_cffi_clock_gettime(_ffi, clock_gettime, clockid)
            return _timespec_to_seconds(timespec)
    else:
        raise RuntimeError('ctypes or cffi must be supported')
elif sys.platform.startswith('darwin') and _machine64 == ('x86_64', True):
    if _use == 'ctypes':
        _macho = _get_ctypes_macho_functions()

        def monotonic():
            self = _macho.get_host()
            try:
                clock = ctypes.c_uint(0)
                clockid = ctypes.c_int(0)
                ret = _macho.get_clock(self, clockid, ctypes.pointer(clock))
                if int(ret) != 0:
                    errno_ = ctypes.get_errno()
                    raise OSError(errno_, os.strerror(errno_))
                try:
                    timespec = _mach_timespec()
                    ret = _macho.get_time(clock, ctypes.pointer(timespec))
                    if int(ret) != 0:
                        errno_ = ctypes.get_errno()
                        raise OSError(errno_, os.strerror(errno_))
                    return _timespec_to_seconds(timespec)
                finally:
                    ret = _macho.deallocate(_macho.get_task(), clock)
                    if int(ret) != 0:
                        errno_ = ctypes.get_errno()
                        raise OSError(errno_, os.strerror(errno_))
            finally:
                ret = _macho.deallocate(_macho.get_task(), self)
                if int(ret) != 0:
                    errno_ = ctypes.get_errno()
                    raise OSError(errno_, os.strerror(errno_))
    elif _use == 'cffi':
        _ffi.cdef('''
            struct mach_timespec { unsigned tv_sec; int tv_nsec; };
            extern unsigned mach_task_self_;
            unsigned int mach_host_self(void);
            int host_get_clock_service(unsigned, int, unsigned *);
            int clock_get_time(unsigned, struct mach_timespec *);
            int mach_port_deallocate(unsigned, unsigned);
        ''')
        _macho = _ffi.dlopen('/usr/lib/system/libmacho.dylib')

        def monotonic():
            taskptr = _ffi.addressof(_macho, 'mach_task_self_')
            host = _macho.mach_host_self()
            try:
                clockptr = _ffi.new('unsigned *')
                clockid = _ffi.cast('int', 0)
                ret = _macho.host_get_clock_service(host, clockid, clockptr)
                if int(ret) != 0:
                    errno_ = int(_ffi.errno)
                    raise OSError(errno_, os.strerror(errno_))
                try:
                    timespecptr = _ffi.new('struct mach_timespec *')
                    ret = _macho.clock_get_time(clockptr[0], timespecptr)
                    if int(ret) != 0:
                        errno_ = int(_ffi.errno)
                        raise OSError(errno_, os.strerror(errno_))
                    return _timespec_to_seconds(timespecptr)
                finally:
                    ret = _macho.mach_port_deallocate(taskptr[0], clockptr[0])
                    if int(ret) != 0:
                        errno_ = int(_ffi.errno)
                        raise OSError(errno_, os.strerror(errno_))
            finally:
                ret = _macho.mach_port_deallocate(taskptr[0], host)
                if int(ret) != 0:
                    errno_ = int(_ffi.errno)
                    raise OSError(errno_, os.strerror(errno_))
    else:
        raise RuntimeError('ctypes or cffi must be supported')
elif sys.platform.startswith('win32'):
    if _use == 'ctypes':
        _GetTickCount = getattr(ctypes.windll.kernel32, 'GetTickCount64', None)

        if _GetTickCount is not None:
            _GetTickCount.restype = ctypes.c_uint64
        else:
            _GetTickCount = ctypes.windll.kernel32.GetTickCount
            _GetTickCount.restype = ctypes.c_uint32

        def monotonic():
            return float(_GetTickCount()) * 1e-3
    elif _use == 'cffi':
        _ffi.cdef('''
            unsigned long long WINAPI GetTickCount64(void);
            unsigned long WINAPI GetTickCount(void);
        ''')
        _kernel32 = _ffi.dlopen('kernel32.dll')
        try:
            _kernel32.GetTickCount64()

            def monotonic():
                return float(_kernel32.GetTickCount64()) * 1e-3
        except:
            def monotonic():
                return float(_kernel32.GetTickCount()) * 1e-3
    else:
        raise RuntimeError('ctypes or cffi must be supported')
else:
    def monotonic():
        msg = 'monotonic not supported on your platform'
        raise OSError(errno.ENOSYS, msg)


if __name__ == '__main__':
    print(monotonic())
