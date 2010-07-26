
VERSION := 1.0.0

CC = gcc
INSTALL = install
INSTALL_LIB = $(INSTALL) -m 0755
SED = sed
CHMOD = chmod

PREFIX = /usr/local
INSTALL_NAME_PREFIX = $(PREFIX)/lib

build/monotonic_time.py: monotonic_time.py.in
	@$(SED) -e 's/^@VERSION@/__version__ = '"'$(VERSION)'/" monotonic_time.py.in > build/monotonic_time.py
	@$(CHMOD) +x build/monotonic_time.py
	@echo 'GEN		build/monotonic_time.py'
build/setup.py: setup.py.in
	@$(SED) -e 's/^@VERSION@/    version='"'$(VERSION)',/" setup.py.in > build/setup.py
	@$(CHMOD) +x build/setup.py
	@echo 'GEN		build/setup.py'

clean:
	rm -rf build && mkdir build && touch build/.file
.PHONY: clean

