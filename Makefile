
all: monotonic_time.py setup.py
.PHONY: all

include common.mk

install:
	@echo "Do 'sudo python setup.py install' to install python module."
.PHONY: install

