
VERSION := 1.0.0

CC = gcc
INSTALL = install
INSTALL_LIB = $(INSTALL) -m 0755
SED = sed
CHMOD = chmod

PREFIX = /usr/local
INSTALL_NAME_PREFIX = $(PREFIX)/lib

monotonic_time.py: monotonic_time.py.in
	@$(SED) -e 's/^@VERSION@/__version__ = '"'$(VERSION)'/" monotonic_time.py.in > monotonic_time.py
	@$(CHMOD) +x monotonic_time.py
	@echo 'GEN		monotonic_time.py'
setup.py: setup.py.in
	@$(SED) -e 's/^@VERSION@/    version='"'$(VERSION)',/" setup.py.in > setup.py
	@$(CHMOD) +x setup.py
	@echo 'GEN		setup.py'

clean:
	rm -rf build && mkdir build
	rm -f monotonic_time.py setup.py
.PHONY: clean

