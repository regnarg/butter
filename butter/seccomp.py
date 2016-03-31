#!/usr/bin/env python
"""fanotify: wrapper around the fanotify family of syscalls for watching for file modifcation"""
from __future__ import print_function

from os import O_RDONLY, O_WRONLY, O_RDWR
from os import fdopen
import errno as _errno

from warnings import warn

warn(PendingDeprecationWarning(), "The seccomp module is deprecated in favour of the official bindings, please consider upgrading")

READ_EVENTS_MAX = 10

from ._seccomp_c import ffi, lib

def condition(arg=0, comparison=lib.SCMP_CMP_EQ, arg1=ffi.NULL, arg2=ffi.NULL):
    """Initalise a new struct_arg_cmp object
    :parama arg int: Which argument to the syscall the test should be performed on
    :parama comparison: The type of comparison to make (SCMP_CMP_*)
    :parama arg1 int: argument 1 for the comaprison
    :parama arg2 int: argument 2 for the comparison (not always used)
    """
    rule = ffi.new('struct scmp_arg_cmp *')
    rule.arg = arg
    rule.op = comparison
    rule.datum_a = ffi.cast('uint64_t', arg1)
    rule.datum_b = ffi.cast('uint64_t', arg2)

    return rule
