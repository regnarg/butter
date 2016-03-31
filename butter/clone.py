#!/usr/bin/env python

from .utils import PermissionError, UnknownError
import errno

from ._clone import ffi as _ffi
from ._clone import lib as _C

CLONE_NEWNS = _C.CLONE_NEWNS
CLONE_NEWUTS = _C.CLONE_NEWUTS
CLONE_NEWIPC = _C.CLONE_NEWIPC
CLONE_NEWUSER = _C.CLONE_NEWUSER
CLONE_NEWPID = _C.CLONE_NEWPID
CLONE_NEWNET = _C.CLONE_NEWNET

def unshare(flags):
    """Unshare the current namespace and create a new one

    Arguments
    ----------
    :param int flags: The flags controlling which namespaces to unshare

    Flags
    ------
    CLONE_NEWNS: Unshare the mount namespace causing mounts in this namespace
                 to not be visible to the parent namespace
    CLONE_NEWUTS: Unshare the system hostname allowing it to be changed independently
                  to the rest of the system
    CLONE_NEWIPC: Unshare the IPC namespace 
    CLONE_NEWUSER: Unshare the UID space allowing UIDs to be remapped to the parent
    CLONE_NEWPID: Unshare the PID space allowing remapping of PIDs relative to the parent
    CLONE_NEWNET: Unshare the network namespace, creating a separate set of network
                  interfaces/firewall rules

    Exceptions
    -----------
    :raises ValueError: Invalid value in flags
    """
    fd = _C.unshare(flags)

    if fd < 0:
        err = _ffi.errno
        if err == errno.EINVAL:
            raise ValueError("Invalid value in flags")
        elif err == errno.EPERM:
            raise PermissionError("Process in chroot or has incorrect permissions")
        elif err == errno.EUSERS:
            raise PermissionError("CLONE_NEWUSER specified but max user namespace nesting has been reached")
        elif err == errno.ENOMEM:
            raise MemoryError("Insufficent kernel memory available")
        else:
            # If you are here, its a bug. send us the traceback
            raise UnknownError(err)

    return fd


### prctl

def main():
    import os, errno, sys
    
#    ret = _C.__clone(CLONE_NEWNET|CLONE_NEWUTS|CLONE_NEWIPC|CLONE_NEWNS, _ffi.NULL)
#    ret = _C.__clone(CLONE_NEWNET|CLONE_NEWUTS|CLONE_NEWIPC|CLONE_NEWNS, _ffi.NULL, _ffi.NULL, _ffi.NULL, _ffi.NULL)

    ret = _C.unshare(CLONE_NEWNET|CLONE_NEWUTS|CLONE_NEWIPC|CLONE_NEWNS)
#    ret = _C.unshare(CLONE_ALL)
    if ret >= 0:
#        with open("/proc/self/uid_map", "w") as f:
#            f.write("0 0 1\n")
        os.execl('/bin/bash', 'bash')
    else:
        print(ret, _ffi.errno, errno.errorcode[_ffi.errno])
        print("failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
