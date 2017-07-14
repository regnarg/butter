#!/usr/bin/env python
"""filesystem: wrappers for miscallaneous filesystem-manipulation calls, especially the *at family."""

from cffi import FFI

ffi = FFI()
ffi.cdef("""
#define AT_FDCWD ...
#define RENAME_NOREPLACE 1
#define RENAME_EXCHANGE  2
#define RENAME_WHITEOUT  4

int renameat2(int olddirfd, const char *oldpath,
             int newdirfd, const char *newpath, unsigned int flags);
""")

ffi.set_source("_filesystem_c", """
#include <fcntl.h>           /* Definition of AT_* constants */
#include <stdio.h>
#include <sys/syscall.h>
#include <unistd.h>
#define RENAME_NOREPLACE 1
#define RENAME_EXCHANGE  2
#define RENAME_WHITEOUT  4

int renameat2(int olddirfd, const char *oldpath,
             int newdirfd, const char *newpath, unsigned int flags) {
    return (int)syscall(SYS_renameat2, olddirfd, oldpath, newdirfd, newpath, flags);
};
""", libraries=[])

if __name__ == "__main__":
    ffi.compile()
