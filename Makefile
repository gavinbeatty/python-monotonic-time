
all: build/monotonic_time.py build/setup.py
.PHONY: all

include common.mk

install:
	@echo "Do '(cd build && sudo python setup.py install ; )' to install python module."
.PHONY: install

