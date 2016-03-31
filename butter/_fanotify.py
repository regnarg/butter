#!/usr/bin/env python
"""fanotify: wrapper around the fanotify family of syscalls for watching for file modifcation"""

from .utils import PermissionError, UnknownError, CLOEXEC_DEFAULT
from collections import namedtuple
from os import O_RDONLY, O_WRONLY, O_RDWR
from os import getpid, readlink
from os import close
from os.path import join
import errno

READ_EVENTS_MAX = 10

from ._fanotify_c import ffi, lib

def fanotify_init(flags=0, event_flags=O_RDONLY, closefd=CLOEXEC_DEFAULT):
    """Create a fanotify handle
    """
    assert isinstance(flags, int), 'Flags must be an integer'
    assert isinstance(event_flags, int), 'Event flags must be an integer'

    if closefd:
        flags |= FAN_CLOEXEC

    fd = lib.fanotify_init(flags, event_flags)

    if fd < 0:
        err = ffi.errno
        if err == errno.EINVAL:
            raise ValueError("Invalid argument or flag")
        elif err == errno.EMFILE:
            raise OSError("Maximum fanotify instances reached or cant Queue/Mark limits")
        elif err == errno.ENOMEM:
            raise MemoryError("Insufficent kernel memory avalible")
        elif err == errno.EPERM:
            raise PermissionError("Operation not permitted")
        else:
            # If you are here, its a bug. send us the traceback
            raise UnknownError(err)
                                            
    return fd

def fanotify_mark(fd, path, mask, flags, dfd=0):
    """Add a file to a fanotify context"""
    """
    EINVAL: an invalid flag or mask was passed in
    EBADF: an invalid fd was passed in
    ENOENT: directory is invalid or directory/mount not marked
    ENOMEM: no mem avalible
    ENOSPC: Too many marks
    """
    if hasattr(fd, 'fileno'):
        fd = fd.fileno()

    assert isinstance(fd, int), 'FD must be an integer'
    assert isinstance(dfd, int), 'DFD must be an integer'
    assert isinstance(flags, int), 'Flags must be an integer'
    assert isinstance(mask, int), 'Mask must be an integer'
    assert isinstance(path, (str, bytes)), 'Path must be a string'
    assert len(path) > 0, 'Path cannot be 0 chars'
    
    if isinstance(path, str):
        path = path.encode()

    ret = lib.fanotify_mark(fd, flags, mask, dfd, path)
    if ret < 0:
        err = ffi.errno
        if err == errno.EINVAL:
            raise ValueError("Invalid flag or mask")
        elif err == errno.EBADF:
            raise ValueError("fd does not exist or was of the incorrect type")
        elif err == errno.ENOENT:
            raise ValueError("File pointed to by path and dfd does not exist")
        elif err == errno.ENOMEM:
            raise MemoryError("Insufficent kernel memory avalible")
        elif err == errno.ENOSPC:
            raise OSError("Too many marks")
        else:
            # If you are here, its a bug. send us the traceback
            raise UnknownError(err)

class FanotifyEvent(object):
    __slots__ = ['_filename', 'version', 'mask', 'fd', 'pid']
    def __init__(self, version, mask, fd, pid):
        self.version = version
        self.mask = mask
        self.fd = fd
        self.pid = pid

        self._filename = None
                
    @property
    def filename(self):
        if not self._filename:
            try:
                name = readlink(join('/proc', str(getpid()), 'fd', str(self.fd)))
                self._filename = name
            except OSError:
                self._filename = "<Unknown>"
    
        return self._filename
        
    def close(self):
        close(self.fd)
        self.fd = None

    def __repr__(self):
        return "<FanotifyEvent filename={}, version={}, mask=0x{:X}, fd={}, pid={}>".format(
                self.filename, self.version, self.mask, self.fd, self.pid)

    @property
    def access_event(self):
        return True if self.mask & FAN_ACCESS else False

    @property
    def access_perm_event(self):
        return True if self.mask & FAN_ACCESS_PERM else False

    @property
    def modify_event(self):
        return True if self.mask & FAN_MODIFY else False

    @property
    def close_event(self):
        return True if self.mask & FAN_CLOSE else False

    @property
    def close_write_event(self):
        return True if self.mask & FAN_CLOSE_WRITE else False

    @property
    def close_nowrite_event(self):
        return True if self.mask & FAN_CLOSE_NOWRITE else False

    @property
    def open_event(self):
        return True if self.mask & FAN_OPEN else False

    @property
    def open_perm_event(self):
        return True if self.mask & FAN_OPEN_PERM else False

    @property
    def queue_overflow_event(self):
        return True if self.mask & FAN_Q_OVERFLOW else False

    @property
    def on_dir_event(self):
        return True if self.mask & FAN_ONDIR else False

    @property
    def on_child_event(self):
        return True if self.mask & FAN_EVENT_ON_CHILD else False


def str_to_events(str):
    event_struct_size = ffi.sizeof('struct fanotify_event_metadata')

    events = []

    str_buf = ffi.new('char[]', len(str))
    str_buf[0:len(str)] = str

    i = 0
    while i < len(str_buf):
        event = ffi.cast('struct fanotify_event_metadata *', str_buf[i:i+event_struct_size])
        events.append(FanotifyEvent(event.vers, event.mask, event.fd, event.pid))

        i += event.event_len

    return events
