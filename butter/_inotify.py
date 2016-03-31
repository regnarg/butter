#!/usr/bin/env python
"""inotify: Wrapper around the inotify syscalls providing both a function based and file like interface"""

from collections import namedtuple
from .utils import PermissionError, UnknownError, CLOEXEC_DEFAULT
import errno

from ._inotify_c import ffi, lib


def inotify_init(flags=0, closefd=CLOEXEC_DEFAULT):
    """Initialise an inotify instnace and return a File Descriptor to refrence is
    
    Arguments:
    -----------
    Flags:
    -------
    IN_CLOEXEC: Automatically close the inotify handle on exec()
    IN_NONBLOCK: Place the file descriptor in non blocking mode
    """
    assert isinstance(flags, int), 'Flags must be an integer'

    if closefd:
        flags |= IN_CLOEXEC

    fd = lib.inotify_init1(flags)
    
    if fd < 0:
        err = ffi.errno
        if err == errno.EINVAL:
            raise ValueError("Invalid argument or flag")
        elif err == errno.EMFILE:
            raise OSError("Maximum inotify instances reached")
        elif err == errno.ENFILE:
            raise OSError("File descriptor limit hit")
        elif err == errno.ENOMEM:
            raise MemoryError("Insufficent kernel memory avalible")
        else:
            # If you are here, its a bug. send us the traceback
            raise UnknownError(err)

    return fd
    
def inotify_add_watch(fd, path, mask):
    """Start watching a filepath for events
    
    Arguments:
    -----------
    fd:    The inotify file descriptor to attach the watch to
    path:  The path to the file/directory to be monitored for events
    mask:  The events to listen for
    
    Flags:
    -------
    IN_ACCESS:        File was accessed
    IN_MODIFY:        File was modified
    IN_ATTRIB:        Metadata changed
    IN_CLOSE_WRITE:   Writtable file was closed
    IN_CLOSE_NOWRITE: Unwrittable file closed
    IN_OPEN:          File was opened
    IN_MOVED_FROM:    File was moved from X
    IN_MOVED_TO:      File was moved to Y
    IN_CREATE:        Subfile was created
    IN_DELETE:        Subfile was deleted
    IN_DELETE_SELF:   Self was deleted
    IN_MOVE_SELF:     Self was moved

    IN_ONLYDIR:      only watch the path if it is a directory
    IN_DONT_FOLLOW:  don't follow a sym link
    IN_EXCL_UNLINK:  exclude events on unlinked objects
    IN_MASK_ADD:     add to the mask of an already existing watch
    IN_ISDIR:        event occurred against dir
    IN_ONESHOT:      only send event once
    
    Returns:
    ---------
    int: A watch descriptor that can be passed to inotify_rm_watch
    
    Exceptions:
    ------------
    ValueError:
    * No valid events in the event mask
    * fd is not an inotify file descriptor
    OSError:
    * fd is not a valid file descriptor
    * Process has no access to specified file
    * File/Folder specified does not exist
    * Maximum number of watches hit
    MemoryError:
    * Raised if the kernel cannot allocate sufficent resources to handle the watch (eg kernel memory)
    """
    if hasattr(fd, "fileno"):
        fd = fd.fileno()

    assert isinstance(fd, int), "fd must by an integer"
    assert isinstance(path, (str, bytes)), "path is not a string"
    assert len(path) > 0, "Path must be longer than 0 chars"
    assert isinstance(mask, int), "mask must be an integer"
    
    if isinstance(path, str):
        path = path.encode()
    
    wd = lib.inotify_add_watch(fd, path, mask)

    if wd < 0:
        err = ffi.errno
        if err == errno.EINVAL:
            raise ValueError("The event mask contains no valid events; or fd is not an inotify file descriptor")
        elif err == errno.EACCES:
            raise PermissionError("You do not have permission to read the specified path")
        elif err == errno.EBADF:
            raise ValueError("fd is not a valid file descriptor")
        elif err == errno.EFAULT:
            raise ValueError("path points to a file/folder outside the processes accessible address space")
        elif err == errno.ENOENT:
            raise ValueError("File/Folder pointed to by path does not exist")
        elif err == errno.ENOSPC:
            raise OSError("Maximum number of watches hit or insufficent kernel resources")
        elif err == errno.ENOMEM:
            raise MemoryError("Insufficent kernel memory avalible")
        else:
            # If you are here, its a bug. send us the traceback
            raise UnknownError(err)
            
    return wd
    
def inotify_rm_watch(fd, wd):
    """Stop watching a path for events
    
    Arguments:
    -----------
    fd: The inotify file descriptor to remove the watch from
    wd: The Watch to be removed
    
    Returns:
    ---------
    None
    
    Exceptions:
    ------------
    ValueError: Returned if supplied watch is not valid or if the file descriptor is not an inotify file descriptor
    OSError: File descriptor is invalid
    """
    if hasattr(fd, 'fileno'):
        fd = fd.fileno()
            
    assert isinstance(fd, int), "fd must by an integer"
    assert isinstance(wd, int), "wd must be an integer"

    ret = lib.inotify_rm_watch(fd, wd)

    if ret < 0:
        err = ffi.errno
        if err == errno.EINVAL:
            raise ValueError("wd is invalid or fd is not an inotify File Descriptor")
        elif err == errno.EBADF:
            raise ValueError("fd is not a valid file descriptor")
        else:
            # If you are here, its a bug. send us the traceback
            raise UnknownError(err)


def str_to_events(str):
    event_struct_size = ffi.sizeof('struct inotify_event')

    events = []

    str_buf = ffi.new('char[]', len(str))
    str_buf[0:len(str)] = str

    i = 0
    while i < len(str_buf):
        event = ffi.cast('struct inotify_event *', str_buf[i:i+event_struct_size])

        filename_start = i + event_struct_size
        filename_end = filename_start + event.len
        filename = ffi.string(str_buf[filename_start:filename_end])
        
        events.append(InotifyEvent(event.wd, event.mask, event.cookie, filename))
        
        i += event_struct_size + event.len

    return events


InotifyEvent = namedtuple("InotifyEvent", "wd mask cookie filename")
class InotifyEvent(InotifyEvent):
    __slots__ = []
    @property
    def access_event(self):
        return True if self.mask & IN_ACCESS else False

    @property
    def modify_event(self):
        return True if self.mask & IN_MODIFY else False

    @property
    def attrib_event(self):
        return True if self.mask & IN_ATTRIB else False

    @property
    def close_write_event(self):
        return True if self.mask & IN_CLOSE_WRITE else False

    @property
    def close_nowrite_event(self):
        return True if self.mask & IN_CLOSE_NOWRITE else False

    @property
    def close_event(self):
        return True if self.mask & (IN_CLOSE_NOWRITE|IN_CLOSE_WRITE) else False

    @property
    def open_event(self):
        return True if self.mask & IN_OPEN else False

    @property
    def moved_from_event(self):
        return True if self.mask & IN_MOVED_FROM else False

    @property
    def moved_to_event(self):
        return True if self.mask & IN_MOVED_TO else False

    @property
    def create_event(self):
        return True if self.mask & IN_CREATE else False

    @property
    def delete_event(self):
        return True if self.mask & IN_DELETE else False

    @property
    def delete_self_event(self):
        return True if self.mask & IN_DELETE_SELF else False

    @property
    def move_self_event(self):
        return True if self.mask & IN_MOVE_SELF else False

    @property
    def is_dir_event(self):
        return True if self.mask & IN_ISDIR else False

# update the local namespace with flags and provide
# a handy dict for reversable lookups
event_name = {}
_l = locals()
for key in dir(lib):
    if key.startswith('IN_'):
        val = getattr(lib, key)
        _l[key] = val
        event_name[key] = val
        event_name[val] = key
