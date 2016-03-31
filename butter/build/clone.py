#!/usr/bin/env python

from cffi import FFI

ffi = FFI()

ffi.cdef("""

#define CLONE_FS      ...
#define CLONE_NEWNS   ...
#define CLONE_NEWUTS  ...
#define CLONE_NEWIPC  ...
#define CLONE_NEWUSER ...
#define CLONE_NEWPID  ...
#define CLONE_NEWNET  ...

//#long __clone(unsigned long flags, void *child_stack, ...);
long __clone(unsigned long flags, void *child_stack,
             void *ptid, void *ctid, void *regs);

int unshare(int flags);
#pragma weak setns
int setns(int fd, int nstype);
""")

ffi.set_source("_clone", """
#include <linux/sched.h>
#include <unistd.h>
#include <sys/types.h>

// man page
//long __clone(unsigned long flags, void *child_stack, ...);
long __clone(unsigned long flags, void *child_stack,
             void *ptid, void *ctid,
             void *regs);

int unshare(int flags);

int setns(int fd, int nstype) {
    return -1;
};
""", libraries=[])

if __name__ == "__main__":
    ffi.compile()
