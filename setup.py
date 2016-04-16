#!/usr/bin/env python

# This must be at the top to force cffi to use setuptools instead od distools
from setuptools import setup

import platform

name = 'butter'
path = 'butter'

ext_modules = [
    name + "/build/clone.py:ffi",
    name + "/build/eventfd.py:ffi",
    name + "/build/fanotify.py:ffi",
    name + "/build/inotify.py:ffi",
#    name + "/build/seccomp.py:ffi",
    name + "/build/signalfd.py:ffi",
    name + "/build/splice.py:ffi",
    name + "/build/system.py:ffi",
    name + "/build/timerfd.py:ffi",
    name + "/build/utils.py:ffi",
    ]

if platform.linux_distribution()[0] == 'debian' and \
   platform.linux_distribution()[1] < '8.0':
    # no seccomp.h in debian wheezy by default
    pass
else:
    ext_modules.append(name + '/build/seccomp.py:ffi')

# work around for build failure on pypy, cannot set _GNU_SOURCE
# in ffi.set_source as stdlib being imported before it is hit
# (ie its not first line in file)
# not making this platform specific as it is not breaking cpython
# this likley breaks mucl as well but that can be fixed as required
import os
CURRENT_CFLAGS = os.environ.get('CFLAGS', '')
NEW_CFLAGS = "-D_GNU_SOURCE " + CURRENT_CFLAGS
os.environ['CFLAGS'] = NEW_CFLAGS

## Automatically determine project version ##
try:
    from hgdistver import get_version
except ImportError:
    def get_version():
        import os
        
        d = {'__name__':name}

        # handle single file modules
        if os.path.isdir(path):
            module_path = os.path.join(path, '__init__.py')
        else:
            module_path = path
                                                
        with open(module_path) as f:
            try:
                exec(f.read(), None, d)
            except:
                pass

        return d.get("__version__", 0.1)

## Use py.test for "setup.py test" command ##
from setuptools.command.test import test as TestCommand
class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        pytest.main(self.test_args)

## Try and extract a long description ##
readme = ""
for readme_name in ("README", "README.rst", "README.md",
                    "CHANGELOG", "CHANGELOG.rst", "CHANGELOG.md"):
    try:
        readme += open(readme_name).read() + "\n\n"
    except (OSError, IOError):
        continue

## Finally call setup ##
setup(
    name = name,
    version = get_version(),
    packages = [path, path + "/asyncio", path + "/build"],
    author = "Da_Blitz",
    author_email = "code@pocketnix.org",
    maintainer=None,
    maintainer_email=None,
    description = "Library to interface to low level linux features (inotify, fanotify, timerfd, signalfd, eventfd, containers) with asyncio support",
    long_description = readme,
    license = "MIT BSD",
    keywords = "linux splice tee fanotify inotify eventfd signalfd timerfd aio clone unshare asyncio container server async",
    download_url = "http://blitz.works/butter/archive/tip.tar.bz2",
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        ],
    platforms=None,
    url = "http://blitz.works/butter/file/tip",
#    entry_points = {"console_scripts":["hammerhead=hammerhead:main",
#                                       "hammerhead-enter=hammerhead:setns"],
#                   },
#    scripts = ['scripts/dosomthing'],
    zip_safe = False,
    ext_package = name,
    setup_requires = ['cffi>=1.0.0'],
    install_requires = ['cffi>=1.0.0'],
    cffi_modules = ext_modules,
    tests_require = ['tox', 'pytest', 'pytest-cov', 'pytest-mock', 'mock'],
    cmdclass = {'test': PyTest},
)

