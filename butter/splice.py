#!/usr/bin/env python
"""splice: wrapper around the splice() syscall"""

from .utils import UnknownError
import errno as _errno

from _splice_c import ffi as _ffi
from _splice_c import lib as _lib

NULL_TERMINATOR = 1 # length of \0 in bytes
    
def splice(fd_in, fd_out, in_offset=0, out_offset=0, len=0, flags=0):
    """Take data from fd_in and pass it to fd_out without going through userspace
    
    Arguments
    ----------
    :param file fd_in: File object or fd to splice from
    :param file fd_out: File object or fd to splice to
    :param int in_offset: Offset inside fd_in to read from
    :param int out_offset: Offset inside fd_out to write to
    :param int len: Ammount of data to transfer
    :param int flags: Flags to specify extra options
    
    Flags
    ------
    SPLICE_F_MOVE: This is a noop in modern kernels and is left here for compatibility
    SPLICE_F_NONBLOCK: Make splice operations Non blocking (as long as the fd's are non blocking)
    SPLICE_F_MORE: After splice() more data will be sent, this is a hint to add TCP_CORK like buffering
    SPLICE_F_GIFT: unused for splice() (vmsplice compatibility)
    
    Returns
    --------
    :return: Number of bytes written
    :rtype: int
    
    Exceptions
    -----------
    :raises ValueError: One of the file descriptors is unseekable
    :raises ValueError: Neither descriptor refers to a pipe
    :raises ValueError: Target filesystem does not support splicing
    :raises OSError: supplied fd does not refer to a file
    :raises OSError: Incorrect mode for file
    :raises MemoryError: Insufficient kernel memory
    :raises OSError: No writers waiting on fd_in
    :raises OSError: one or both fd's are in blocking mode and SPLICE_F_NONBLOCK specified
    """
    if hasattr(fd_in, 'fileno'):
        fd_in = fd_in.fileno()
    if hasattr(fd_out, 'fileno'):
        fd_out = fd_out.fileno()

    assert isinstance(fd_in, int), 'fd_in must be an integer'
    assert isinstance(fd_out, int), 'fd_in must be an integer'
    assert isinstance(in_offset, int), 'in_offset must be an integer'
    assert isinstance(out_offset, int), 'out_offset must be an integer'
    assert isinstance(len, int), 'len must be an integer'
    assert isinstance(flags, int), 'flags must be an integer'
    
    in_offset = _ffi.cast("long long *", in_offset)
    out_offset = _ffi.cast("long long *", out_offset)

    size = _lib.splice(fd_in, in_offset, fd_out, out_offset, len, flags)
    
    if size < 0:
        err = _ffi.errno
        if err == _errno.EINVAL:
            if in_offset or out_offset:
                raise ValueError("fds may not be seekable")
            else:
                raise ValueError("Target filesystem does not support slicing or file may be in append mode")
        elif err == _errno.EBADF:
            raise ValueError("fds are invalid or incorrect mode for file")
        elif err == _errno.EPIPE:
            raise ValueError("offset specified but one of the fds is a pipe")
        elif err == _errno.ENOMEM:
            raise MemoryError("Insufficent kernel memory available")
        elif err == _errno.EAGAIN:
            raise OSError("No writers on fd_in or a fd is open in BLOCKING mode and NON_BLOCK specified to splice()")
        else:
            # If you are here, its a bug. send us the traceback
            raise UnknownError(err)

    return size


def tee(fd_in, fd_out, len=0, flags=0):
    """Splice data like the :py:func:`.splice` but also leave a copy of the data in the original fd's buffers
    
    Arguments
    ----------
    :param file fd_in: File object or fd to splice from
    :param file fd_out: File object or fd to splice to
    :param int len: Ammount of data to transfer
    :param int flags: Flags to specify extra options
    
    Flags
    ------
    SPLICE_F_MOVE: This is a noop in modern kernels and is left here for compatibility
    SPLICE_F_NONBLOCK: Make tee operations Non blocking (as long as the fd's are non blocking)
    SPLICE_F_MORE: unused for tee()
    SPLICE_F_GIFT: unused for tee() (:py:func:`.vmsplice` compatibility)
    
    Returns
    --------
    :return: Number of bytes written
    :rtype: int
    
    Exceptions
    -----------
    :raises ValueError: One of the file descriptors is not a pipe
    :raises ValueError: Both file descriptors refer to the same pipe
    :raises MemoryError: Insufficient kernel memory
    """
    if hasattr(fd_in, 'fileno'):
        fd_in = fd_in.fileno()
    if hasattr(fd_out, 'fileno'):
        fd_out = fd_out.fileno()
    
    assert isinstance(fd_in, int), 'fd_in must be an integer'
    assert isinstance(fd_out, int), 'fd_in must be an integer'
    assert isinstance(len, int), 'len must be an integer'
    assert isinstance(flags, int), 'flags must be an integer'

    size = _lib.tee(fd_in, fd_out, len, flags)
    
    if size < 0:
        err = _ffi.errno
        if err == _errno.EINVAL:
            raise ValueError("fd_in or fd_out are not a pipe or refer to the same pipe")
        elif err == _errno.ENOMEM:
            raise MemoryError("Insufficent kernel memory available")
        else:
            # If you are here, its a bug. send us the traceback
            raise UnknownError(err)

    return size

SPLICE_F_MOVE = _lib.SPLICE_F_MOVE    
SPLICE_F_NONBLOCK = _lib.SPLICE_F_NONBLOCK
SPLICE_F_MORE = _lib.SPLICE_F_MORE    
SPLICE_F_GIFT = _lib.SPLICE_F_GIFT    

IOV_MAX = _lib.IOV_MAX
