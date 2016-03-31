#!/usr/bin/env python

from cffi import FFI

ffi = FFI()

ffi.cdef("""
#define EFD_CLOEXEC ...
#define EFD_NONBLOCK ...
#define EFD_SEMAPHORE ...

int eventfd(unsigned int initval, int flags);
""")

ffi.set_source("_eventfd_c", """
#include <sys/eventfd.h>
#include <stdint.h> /* Definition of uint64_t */
""", libraries=[])

if __name__ == "__main__":
    ffi.compile()
