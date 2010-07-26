python-monotonic-time
=====================
Gavin Beatty <gavinbeatty@gmail.com>

python-monotonic-time: a simple module to add monotonic time support to Python. Supported platforms are Linux, FreeBSD, Mac OS X\* and Windows.

\* Mac OS X requires a very small C library to function.


License
-------

python-monotonic-time Copyright 2010 Gavin Beatty <gavinbeatty@gmail.com>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You can find the GNU General Public License at:
http://www.gnu.org/licenses/


Install
-------
Note: on Mac OS X, all make commands should be `make -f Makefile.darwin`.

Build:
    make
    (cd build && python setup.py build ; )

Default prefix is `/usr/local`:
    sudo make install
    (cd build && sudo python setup.py install ; )

Select your own prefix:
    make install prefix=~/
    (cd build && python setup.py --user install ; )


