#!/usr/bin/env python

from cffi import FFI

ffi = FFI()
ffi.cdef("""
#define FIONREAD ...
""")

ffi.set_source("_utils_c", """
#include <sys/ioctl.h>
""", libraries=[])

if __name__ == "__main__":
    ffi.compile()
