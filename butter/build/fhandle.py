#!/usr/bin/env python
"""fhandle: wrappers for the name_to_handle_at and open_by_handle_at syscalls."""

from cffi import FFI

ffi = FFI()
ffi.cdef("""
#define MAX_HANDLE_SZ ...
#define AT_FDCWD ...
#define AT_EMPTY_PATH ...
#define AT_SYMLINK_FOLLOW ...
struct file_handle {
   unsigned int  handle_bytes;   /* Size of f_handle [in, out] */
   int           handle_type;    /* Handle type [out] */
   //unsigned char f_handle[0];    /* File identifier (sized by caller) [out] */
   unsigned char f_handle[];    /* File identifier (sized by caller) [out] */
};

int name_to_handle_at(int dirfd, const char *pathname,
                     struct file_handle *handle,
                     int *mount_id, int flags);

int open_by_handle_at(int mount_fd, struct file_handle *handle,
                     int flags);
""")

ffi.set_source("_fhandle_c", """
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
""", libraries=[])

if __name__ == "__main__":
    ffi.compile()
