#!/usr/bin/env python
"""signalfd: Recive signals over a file descriptor"""

from .utils import UnknownError, CLOEXEC_DEFAULT
import signal
import errno

from ._signalfd_c import ffi, lib

NEW_SIGNALFD = -1 # Create a new signal rather than modify an exsisting one


def signalfd(signals, fd=NEW_SIGNALFD, flags=0, closefd=CLOEXEC_DEFAULT):
    """Create a new signalfd
    
    Arguments
    ----------
    :param sigset_t signals: raw cdata to pass to the syscall
    :param int signals: A single int representing the signal to listen for
    :param list signals: A list of signals to listen for
    :param int fd: The file descriptor to modify, if set to NEW_SIGNALFD then a new FD is returned
    :param int flags: 
    
    Flags
    ------
    SFD_CLOEXEC: Close the signalfd when executing a new program
    SFD_NONBLOCK: Open the socket in non-blocking mode
    
    Returns
    --------
    :return: The file descriptor representing the signalfd
    :rtype: int
    
    Exceptions
    -----------
    :raises ValueError: Invalid value in flags
    :raises OSError: Max per process FD limit reached
    :raises OSError: Max system FD limit reached
    :raises OSError: Could not mount (internal) anonymous inode device
    :raises MemoryError: Insufficient kernel memory
    """
    if hasattr(fd, 'fileno'):
        fd = fd.fileno()

    assert isinstance(fd, int), 'fd must be an integer'
    assert isinstance(flags, int), 'Flags must be an integer'

    if closefd:
        flags |= SFD_CLOEXEC

    if isinstance(signals, ffi.CData):
        mask = signals
    else:
        mask = ffi.new('sigset_t[1]')
        # if we have multiple signals then all is good
        try:
            signals = iter(signals)
        except TypeError:
        # if not make the value iterable
            signals = [signals]

        for signal in signals:
            lib.sigaddset(mask, signal)

    ret_fd = lib.signalfd(fd, mask, flags)
    
    if ret_fd < 0:
        err = ffi.errno
        if err == errno.EBADF:
            raise ValueError("FD is not a valid file descriptor")
        elif err == errno.EINVAL:
            if (flags & (0xffffffff ^ (SFD_CLOEXEC|SFD_NONBLOCK))):
                raise ValueError("Mask contains invalid values")
            else:
                raise ValueError("FD is not a signalfd")
        elif err == errno.EMFILE:
            raise OSError("Max system FD limit reached")
        elif err == errno.ENFILE:
            raise OSError("Max system FD limit reached")
        elif err == errno.ENODEV:
            raise OSError("Could not mount (internal) anonymous inode device")
        elif err == errno.ENOMEM:
            raise MemoryError("Insufficent kernel memory available")
        else:
            # If you are here, its a bug. send us the traceback
            raise UnknownError(err)

    return ret_fd


def pthread_sigmask(action, signals):
    """Block and Unblock signals from being delivered to an application
    
    This is required as this function/functionality does not exist in 
    python2.x
    
    Arguments
    ----------
    :param int action: The action to take on the supplied signals (bitmask)
    :param list signals: An iterable of signals
    :param int signals: A single signal
    
    Flags: action
    -----------
    SIG_BLOCK: Block the signals in sigmask from being delivered
    SIG_UNBLOCK: Unblock the signals in the supplied sigmask
    SIG_SETMASK: Set the active signals to match the supplied sigmask
    
    Returns
    --------
    :return: The old set of active signals
    :rtype: sigset
    
    Exceptions
    -----------
    :raises ValueError: Invalid value in 'action'
    :raises ValueError: sigmask is not a valid sigmask_t
    """
    assert isinstance(action, int), '"How" must be an integer'

    new_sigmask = ffi.new('sigset_t[1]')
    old_sigmask = ffi.new('sigset_t[1]')

    # if we have multiple signals then all is good
    try:
        signals = iter(signals)
    except TypeError:
    # if not make the value iterable
        signals = [signals]

    for signal in signals:
        lib.sigaddset(new_sigmask, signal)
    
    ret = lib.pthread_sigmask(action, new_sigmask, ffi.NULL)
    
    if ret < 0:
        err = ffi.errno
        if err == errno.EINVAL:
            raise ValueError("Action is an invalid value (not one of SIG_BLOCK, SIG_UNBLOCK or SIG_SETMASK)")
        elif err == errno.EFAULT:
            raise ValueError("sigmask is not a valid sigset_t")
        else:
            # If you are here, its a bug. send us the traceback
            raise UnknownError(err)


SFD_CLOEXEC = lib.SFD_CLOEXEC
SFD_NONBLOCK = lib.SFD_NONBLOCK

SIG_BLOCK = lib.SIG_BLOCK
SIG_UNBLOCK = lib.SIG_UNBLOCK
SIG_SETMASK = lib.SIG_SETMASK

signum_to_signame = {val:key for key, val in signal.__dict__.items()
                     if isinstance(val, int) and "_" not in key}


#SIGINFO_LENGTH = 128 # Bytes
SIGINFO_LENGTH = ffi.sizeof('struct signalfd_siginfo')

