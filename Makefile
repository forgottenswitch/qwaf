OUTDIR = gen

WGET = wget
DOWNLOADS_DIR = fetch

all: $(OUTDIR)

$(OUTDIR): conv.py compat symbols types hjkl layouts letters_latin letters_cyr \
	$(DOWNLOADS_DIR)/keysymdef.h
	 python3 conv.py -o $@ layouts

$(DOWNLOADS_DIR)/keysymdef.h:
	mkdir -p $(DOWNLOADS_DIR)
	$(WGET) -O $@ https://cgit.freedesktop.org/xorg/proto/x11proto/plain/keysymdef.h

.PHONY: clean
clean:
	@rm -r $(OUTDIR)
