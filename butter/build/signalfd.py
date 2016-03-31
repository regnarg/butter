#!/usr/bin/env python

from cffi import FFI
import platform

ffi = FFI()
ffi.cdef("""
#define SFD_CLOEXEC ...
#define SFD_NONBLOCK ...

struct signalfd_siginfo {
    uint32_t ssi_signo; /* Signal number */
    int32_t ssi_errno; /* Error number (unused) */
    int32_t ssi_code; /* Signal code */
    uint32_t ssi_pid; /* PID of sender */
    uint32_t ssi_uid; /* Real UID of sender */
    int32_t ssi_fd; /* File descriptor (SIGIO) */
    uint32_t ssi_tid; /* Kernel timer ID (POSIX timers)
    uint32_t ssi_band; /* Band event (SIGIO) */
    uint32_t ssi_overrun; /* POSIX timer overrun count */
    uint32_t ssi_trapno; /* Trap number that caused signal */
    int32_t ssi_status; /* Exit status or signal (SIGCHLD) */
    int32_t ssi_int; /* Integer sent by sigqueue(3) */
    uint64_t ssi_ptr; /* Pointer sent by sigqueue(3) */
    uint64_t ssi_utime; /* User CPU time consumed (SIGCHLD) */
    uint64_t ssi_stime; /* System CPU time consumed (SIGCHLD) */
    uint64_t ssi_addr; /* Address that generated signal
                        (for hardware-generated signals) */
//    uint8_t pad[X]; /* Pad size to 128 bytes (allow for
//                        additional fields in the future) */
    ...;
};

//#define _SIGSET_NWORDS 32
typedef struct
{
    unsigned long int __val[%d];
} __sigset_t;

typedef __sigset_t sigset_t;

int signalfd(int fd, const sigset_t *mask, int flags);

int sigemptyset(sigset_t *set);
int sigfillset(sigset_t *set);
int sigaddset(sigset_t *set, int signum);
int sigdelset(sigset_t *set, int signum);
int sigismember(const sigset_t *set, int signum);

#define SIG_BLOCK ...
#define SIG_UNBLOCK ...
#define SIG_SETMASK ...

int pthread_sigmask(int how, const sigset_t *set, sigset_t *oldset);
""" % (16 if platform.architecture()[0] == "64bit" else 32))
# define _SIGSET_NWORDS     (1024 / (8 * sizeof (unsigned long int)))
# 32bits: 1024 / 8 / 4  = 32
# 64bits: 1024 / 8 / 4  = 16

C = ffi.set_source("_signalfd_c", """
#include <sys/signalfd.h>
#include <stdint.h> /* Definition of uint64_t */
#include <signal.h>
""", libraries=[])

if __name__ == "__main__":
    ffi.compile()
