#!/usr/bin/env python
"""fanotify: wrapper around the fanotify family of syscalls for watching for file modifcation"""

from .utils import get_buffered_length as _get_buffered_length
from .utils import Eventlike as _Eventlike
from .utils import CLOEXEC_DEFAULT as _CLOEXEC_DEFAULT

from os import O_RDONLY, O_WRONLY, O_RDWR
from os import read as _read

from ._fanotify import fanotify_init, fanotify_mark, str_to_events

# Import all the constants
from ._fanotify import lib as _lib
_l = locals()
for key in dir(_lib):
    if key.startswith('FAN_'):
        _l[key] = getattr(_lib, key)
del key, _lib, _l

class Fanotify(_Eventlike):
    blocking = True
    
    def __init__(self, flags, event_flags=O_RDONLY, closefd=_CLOEXEC_DEFAULT):
        super(Fanotify, self).__init__()
        self._fd = fanotify_init(flags, event_flags, closefd=closefd)

        self._events = []

        if flags & FAN_NONBLOCK:
            self.blocking = false
        
        if event_flags & O_RDWR|O_WRONLY:
            self._mode = 'w+'
        elif event_flags & O_WRONLY:
            self._mode = 'w'
        else:
            self._mode = 'r'

    def watch(self, path, mask, flags=0, dfd=0):
        flags |= FAN_MARK_ADD
        fanotify_mark(self.fileno(), path, mask, flags, dfd)

    def del_watch(self, path, mask, flags=0, dfd=0):
        self.ignore(path, mask, flags, dfd)
        
    def ignore(self, path, mask, flags=0, dfd=0):
        flags |= FAN_MARK_REMOVE
        fanotify_mark(self.fileno(), path, mask, flags, dfd)

    def _read_events(self):
        fd = self.fileno()

        raw_events = _read(fd, _get_buffered_length(fd))

        events = str_to_events(raw_events)

        return events
