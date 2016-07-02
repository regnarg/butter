#!/usr/bin/env python
"""fhandle: wrappers for the name_to_handle_at and open_by_handle_at syscalls."""

from ._fhandle_c import ffi, lib
import os, errno
from collections import namedtuple

AT_FDCWD = lib.AT_FDCWD
AT_EMPTY_PATH = lib.AT_EMPTY_PATH
AT_SYMLINK_FOLLOW = lib.AT_SYMLINK_FOLLOW

FileHandle = namedtuple('FileHandle', 'type handle')

class StaleHandle(OSError):
    def __init__(self):
        OSError.__init__(self, errno.ESTALE, os.strerror(errno.ESTALE))

def name_to_handle_at(dirfd, pathname, flags=0):
    c_handle = ffi.new('struct file_handle *', {'handle_bytes': lib.MAX_HANDLE_SZ, 'f_handle': lib.MAX_HANDLE_SZ})
    mount_id = ffi.new('int *')
    ret = lib.name_to_handle_at(dirfd, pathname, c_handle, mount_id, flags)
    if ret != 0:
        raise OSError(ffi.errno, os.strerror(ffi.errno))
    data = bytes(ffi.buffer(ffi.cast('char[%d]' % c_handle.handle_bytes, c_handle.f_handle)))
    handle = FileHandle(c_handle.handle_type, data)
    return handle, mount_id[0]

def open_by_handle_at(mount_fd, handle, flags=0):
    handle_type, handle_data = handle
    c_handle = ffi.new('struct file_handle *', {'handle_bytes': len(handle_data),
                            'handle_type': handle_type, 'f_handle': handle_data})
    fd = lib.open_by_handle_at(mount_fd, c_handle, flags)
    if fd < 0:
        if ffi.errno == errno.ESTALE:
            raise StaleHandle()
        else:
            raise OSError(ffi.errno, os.strerror(ffi.errno))
    return fd


__all__ = ['FileHandle', 'StaleHandle', 'AT_FDCWD', 'AT_EMPTY_PATH', 'AT_SYMLINK_FOLLOW', 'name_to_handle_at', 'open_by_handle_at']
