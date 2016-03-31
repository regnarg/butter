#!/usr/bin/env python

from cffi import FFI

ffi = FFI()
ffi.cdef("""
#define TFD_CLOEXEC ...
#define TFD_NONBLOCK ...

#define TFD_TIMER_ABSTIME ...

#define CLOCK_REALTIME                  ...
#define CLOCK_MONOTONIC                 ...
#define CLOCK_PROCESS_CPUTIME_ID        ...
#define CLOCK_THREAD_CPUTIME_ID         ...
#define CLOCK_MONOTONIC_RAW             ...
#define CLOCK_REALTIME_COARSE           ...
#define CLOCK_MONOTONIC_COARSE          ...
#define CLOCK_BOOTTIME                  ...
#define CLOCK_REALTIME_ALARM            ...
#define CLOCK_BOOTTIME_ALARM            ...
//#define CLOCK_SGI_CYCLE                 ...
//#define CLOCK_TAI                       ...

typedef long int time_t;

struct timespec {
    time_t tv_sec; /* Seconds */
    long tv_nsec; /* Nanoseconds */
};

struct itimerspec {
    struct timespec it_interval; /* Interval for periodic timer */
    struct timespec it_value; /* Initial expiration */
};

int timerfd_create(int clockid, int flags);

int timerfd_settime(int fd, int flags,
                    const struct itimerspec *new_value,
                    struct itimerspec *old_value);

int timerfd_gettime(int fd, struct itimerspec *curr_value);
""")

ffi.set_source("_timerfd_c", """
#include <sys/timerfd.h>
#include <stdint.h> /* Definition of uint64_t */
#include <time.h>
""", libraries=[])

if __name__ == "__main__":
    ffi.compile()
