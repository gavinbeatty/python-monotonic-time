# vi: set ft=Makefile noexpandtab shiftwidth=4 tabstop=4:
all::

.SUFFIXES:
SHELL = /bin/sh

SRCDIR = .
ifeq ($(SRCDIR),)
	SRCDIR = .
endif
ifndef SHELL_PATH
	SHELL_PATH = /bin/sh
endif

CC = gcc
AR = ar
RM = rm -f
FIND = find
INSTALL = install
INSTALL_LIB = $(INSTALL) -m 0755
INSTALL_DIR = $(INSTALL) -d -m 0755
SED = sed
CHMOD = chmod

build/VERSION-FILE: FORCE
	@$(INSTALL_DIR) $(@D)
	@$(SHELL_PATH) $(SRCDIR)/VERSION-GEN $@
-include build/VERSION-FILE

uname_S = $(shell sh -c 'uname -s 2>/dev/null || echo not')

PREFIX = /usr/local
LIBDIR = $(PREFIX)/lib

TARGETS = build/monotonic_time.py build/setup.py
ifeq ($(uname_S),Darwin)
	TARGETS += build/libmonotonic_time.dylib
	TARGETS_INSTALL += darwin_install
endif

# default target
all:: $(TARGETS)

build/monotonic_time.py: $(SRCDIR)/monotonic_time.py.in
	@$(INSTALL_DIR) $(@D)
	@$(SED) 's/^@VERSION@/__version__ = "$(VERSION)"/' $^ > $@
	@$(CHMOD) +x $@
	@echo "GEN		$@"
build/setup.py: $(SRCDIR)/setup.py.in
	@$(INSTALL_DIR) $(@D)
	@$(SED) 's/^@VERSION@/    version="$(VERSION)",/' $^ > $@
	@$(CHMOD) +x $@
	@echo "GEN		$@"

MACOSX_VERSION_MIN = 10.0
ARCH_ARGS = -arch i386 -arch x86_64

build/darwin.c.o: $(SRCDIR)/darwin.c
	@$(INSTALL_DIR) $(@D)
	$(CC) $(ARCH_ARGS) -mmacosx-version-min=$(MACOSX_VERSION_MIN) -fPIC -o $@ -c $^

build/libmonotonic_time.dylib: build/darwin.c.o
	@$(INSTALL_DIR) $(@D)
	$(CC) $(ARCH_ARGS) -mmacosx-version-min=$(MACOSX_VERSION_MIN) -dynamiclib -headerpad_max_install_names -o $@ -install_name $(LIBDIR)/$(@F) $^

darwin_install: build/libmonotonic_time.dylib
	@$(INSTALL_DIR) $(LIBDIR)
	$(INSTALL_LIB) $^ $(LIBDIR)

clean:
	$(RM) -r build

install: $(TARGETS_INSTALL)
	@echo "Do '(cd build && sudo python setup.py install)' to install python module."
.PHONY: all install darwin_install clean FORCE VERSION-FILE
