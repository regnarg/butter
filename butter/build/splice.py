#!/usr/bin/env python

from cffi import FFI

ffi = FFI()
ffi.cdef("""
#define SPLICE_F_MOVE     ... /* This is a noop in modern kernels and is left here for compatibility */
#define SPLICE_F_NONBLOCK ... /* Make splice operations Non blocking (as long as the fd's are non blocking) */
#define SPLICE_F_MORE     ... /* After splice() more data will be sent, this is a hint to add TCP_CORK like buffering */
#define SPLICE_F_GIFT     ... /* unused for splice() (vmsplice compatibility) */

#define IOV_MAX ... /* Maximum ammount of vectors that can be written by vmsplice in one go */

struct iovec {
    void *iov_base; /* Starting address */
    size_t iov_len; /* Number of bytes */
};

ssize_t splice(int fd_in, signed long long *off_in, int fd_out, signed long long *off_out, size_t len, unsigned int flags);
ssize_t tee(int fd_in, int fd_out, size_t len, unsigned int flags);
""")

ffi.set_source("_splice_c", """
#include <limits.h> /* used to define IOV_MAX */
#include <fcntl.h>
#include <sys/uio.h>
""", libraries=[])

if __name__ == "__main__":
    ffi.compile()
