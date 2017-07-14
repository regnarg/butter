#!/usr/bin/env python
"""fhandle: wrappers for the name_to_handle_at and open_by_handle_at syscalls."""

from ._filesystem_c import ffi, lib
import sys, os, errno

AT_FDCWD = lib.AT_FDCWD
RENAME_EXCHANGE = lib.RENAME_EXCHANGE
RENAME_NOREPLACE = lib.RENAME_NOREPLACE
RENAME_WHITEOUT = lib.RENAME_WHITEOUT

def renameat2(olddirfd, oldpath, newdirfd, newpath, flags):
    ret = lib.renameat2(olddirfd, os.fsencode(oldpath), newdirfd, os.fsencode(newpath), flags)
    if ret < 0:
        raise OSError(ffi.errno, os.strerror(ffi.errno))
