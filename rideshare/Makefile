DIRNAME := $(notdir $(PWD))
all: pi-qrcode.svg
%-qrcode.svg: %.svg
	$(MAKE) -C .. $(DIRNAME)/$@
