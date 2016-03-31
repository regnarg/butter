#!/usr/bin/env python

from cffi import FFI

ffi = FFI()
ffi.cdef("""
# define MS_BIND ...
# define MS_DIRSYNC ...
# define MS_MANDLOCK ...
# define MS_MOVE ...
# define MS_NOATIME ...
# define MS_NODEV ...
# define MS_NODIRATIME ...
# define MS_NOEXEC ...
# define MS_NOSUID ...
# define MS_RDONLY ...
# define MS_RELATIME ...
# define MS_REMOUNT ...
# define MS_SILENT ...
# define MS_STRICTATIME ...
# define MS_SYNCHRONOUS ...

# define MNT_FORCE ...
# define MNT_DETACH ...
# define MNT_EXPIRE ...
# define UMOUNT_NOFOLLOW ...

# define HOST_NAME_MAX ...

int mount(const char *source, const char *target,
          const char *filesystemtype, unsigned long mountflags,
          const void *data);
int umount2(const char *target, int flags);
int pivot_root(const char * new_root, const char * put_old);

int gethostname(char *name, size_t len);
int sethostname(const char *name, size_t len);

// Muck with the types so cffi understands it
// normmaly pid_t (defined as int32_t in
// /usr/include/arm-linux-gnueabihf/bits/typesizes.h
int32_t getpid(void);
int32_t getppid(void);
""")

ffi.set_source("_system_c", """  
//#include <sched.h>
#include <sys/mount.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>
#include <sys/mount.h>

// from the `man 2 syscall` manpage
// For example, on the ARM architecture Embedded ABI (EABI), a 64-bit value 
// (e.g., long long) must be aligned to an even register pair.
//
// OK well that sucks, ... but wait! these are always arch sized pointers!
// that means registers on 64bit will be 64bit and 32 bit will be 32bit
// meaining i dont have to align by hand!
// /me laughs manically and strokes a white cat
int pivot_root(const char * new_root, const char * put_old){
    return syscall(SYS_pivot_root, new_root, put_old);
};

int32_t getpid(void){
    return syscall(SYS_getpid);
};

int32_t getppid(void){
    return syscall(SYS_getppid);
};
""", libraries=[])

if __name__ == "__main__":
    ffi.compile()
