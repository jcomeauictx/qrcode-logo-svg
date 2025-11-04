SHELL := /bin/bash
PYTHON ?= $(word 1, $(shell which python3 python false))
PYLINT ?= $(word 1, $(shell which pylint3 pylint true))
SCRIPTS := $(wildcard *.py)
LOGOS := $(filter-out sample.svg $(wildcard *-qrcode.svg), $(wildcard *.svg))
QRCODES := $(addsuffix -qrcode.svg, $(basename $(LOGOS)))
all: $(QRCODES)
	cd bikeshare && $(MAKE) all
%-qrcode.svg: generate.py pyqrcode.py %.svg %.link
	$(PYTHON) $(filter-out pyqrcode.py, $+)
%.pylint: %.py
	$(PYLINT) $<
pylint: $(SCRIPTS)
	$(foreach script, $+, $(MAKE) $(script:.py=).pylint)
push:
	$(foreach remote, $(filter-out original, $(shell git remote)), \
	  git push $(remote);)
clean:
	rm -f *-qrcode.svg */*-qrcode.svg
show:
	for file in *-qrcode.svg */*-qrcode.svg; do \
	 display $$file; \
	 read ignored; \
	done
.PHONY: all push pylint
