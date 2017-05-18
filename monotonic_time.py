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
    import ctypes.util
    _use = 'ctypes'
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


class _mach_timespec(ctypes.Structure):
    _fields_ = [('tv_sec', ctypes.c_uint), ('tv_nsec', ctypes.c_int)]


class _posix_timespec(ctypes.Structure):
    _fields_ = [('tv_sec', ctypes.c_long), ('tv_nsec', ctypes.c_long)]


def _timespec_to_seconds(ts):
    return float(ts.tv_sec) + float(ts.tv_nsec) * 1e-9


def _get_ctypes_mach_functions():
    libcname = ctypes.util.find_library('c')
    libc = ctypes.CDLL(libcname, use_errno=True)
    mach = _NS()
    mach.get_host = libc.mach_host_self
    mach.get_host.argtypes = []
    mach.get_host.restype = ctypes.c_uint
    mach.get_clock = libc.host_get_clock_service
    mach.get_clock.argtypes = [ctypes.c_uint,
                               ctypes.c_int,
                               ctypes.POINTER(ctypes.c_uint)
                               ]
    mach.get_time = libc.clock_get_time
    mach.get_time.argtypes = [ctypes.c_uint, ctypes.POINTER(_mach_timespec)]
    mach.get_task = libc.mach_task_self
    mach.get_task.restype = ctypes.c_uint
    mach.deallocate = libc.mach_port_deallocate
    mach.deallocate.argtypes = [ctypes.c_uint, ctypes.c_uint]
    return mach


def _get_ctypes_clock_gettime():
    clock_gettime = ctypes.CDLL('librt.so.1', use_errno=True).clock_gettime
    clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(_posix_timespec)]
    return clock_gettime


def _call_clock_gettime(clock_gettime, clock):
    t = _posix_timespec()
    if clock_gettime(clock, ctypes.pointer(t)) != 0:
        errno_ = ctypes.get_errno()
        raise OSError(errno_, os.strerror(errno_))
    return t


_py_monotonic = getattr(time, 'monotonic', None)
if _py_monotonic is not None:
    monotonic = _py_monotonic
elif sys.platform.startswith('linux'):
    _clock_gettime = _get_ctypes_clock_gettime()

    def monotonic():
        return _timespec_to_seconds(_call_clock_gettime(_clock_gettime, 1))
elif sys.platform.startswith('freebsd'):
    _clock_gettime = _get_ctypes_clock_gettime()

    def monotonic():
        return _timespec_to_seconds(_call_clock_gettime(_clock_gettime, 4))
elif sys.platform.startswith('darwin') and _machine64 == ('x86_64', True):
    if _use == 'ctypes':
        _mach = _get_ctypes_mach_functions()

        def monotonic():
            self = _mach.get_host()
            try:
                clock_ref = ctypes.c_uint(0)
                if _mach.get_clock(self, 0, ctypes.pointer(clock_ref)) != 0:
                    errno_ = ctypes.get_errno()
                    raise OSError(errno_, os.strerror(errno_))
                try:
                    timespec = _mach_timespec()
                    if _mach.get_time(clock_ref, ctypes.pointer(timespec)) != 0:
                        errno_ = ctypes.get_errno()
                        raise OSError(errno_, os.strerror(errno_))
                    return _timespec_to_seconds(timespec)
                finally:
                    if _mach.deallocate(_mach.get_task(), clock_ref) != 0:
                        errno_ = ctypes.get_errno()
                        raise OSError(errno_, os.strerror(errno_))
            finally:
                if _mach.deallocate(_mach.get_task(), self) != 0:
                    errno_ = ctypes.get_errno()
                    raise OSError(errno_, os.strerror(errno_))
    elif _use == 'cffi':
        _ffi.cdef('''
            unsigned int mach_host_self(void);
        ''')
        print('XXX', _ffi.mach_host_self())
    else:
        raise Exception('ctypes or cffi must be supported')
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
        try:
            _ffi.GetTickCount64()
            def monotonic():
                return float(_ffi.GetTickCount64()) * 1e-3
        except:
            def monotonic():
                return float(_ffi.GetTickCount()) * 1e-3
    else:
        raise Exception('ctypes or cffi must be supported')
else:
    def monotonic():
        msg = 'monotonic not supported on your platform'
        raise OSError(errno.ENOSYS, msg)


if __name__ == '__main__':
    print(monotonic())
