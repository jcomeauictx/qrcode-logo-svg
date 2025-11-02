SHELL := /bin/bash
PYTHON ?= $(word 1, $(shell which python3 python false))
PYLINT ?= $(word 1, $(shell which pylint3 pylint true))
SCRIPTS := $(wildcard *.py)
all: octocat-qrcode.svg
%-qrcode.svg: generate.py pyqrcode.py %.svg %.link
	$(PYTHON) $(filter-out pyqrcode.py, $+)
%.pylint: %.py
	$(PYLINT) $<
pylint: $(SCRIPTS)
	$(foreach script, $+, $(MAKE) $(script:.py=).pylint)
