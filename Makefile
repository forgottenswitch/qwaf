OUTDIR = gen

WGET = wget
DOWNLOADS_DIR = fetch

all: $(OUTDIR)

$(OUTDIR): conv.py add  hjkl layouts letters_lat letters_cyr \
	$(DOWNLOADS_DIR)/keysymdef.h clean
	 python3 -B conv.py $(CONV_FLAGS) -o $@ layouts

g: CONV_FLAGS += -g
g: $(OUTDIR)

$(DOWNLOADS_DIR)/keysymdef.h:
	mkdir -p $(DOWNLOADS_DIR)
	$(WGET) -O $@ https://cgit.freedesktop.org/xorg/proto/x11proto/plain/keysymdef.h

.PHONY: clean
clean:
	@rm -r $(OUTDIR) pic 2>/dev/null || true

.PHONY: pic
pic: $(OUTDIR)
	mkdir -p $@
	convert gen/svg/layouts/qwaf.svg          pic/qwaf.png
	convert gen/svg/layouts/qwaf-lv3.svg      pic/qwaf-lv3.png
	convert gen/svg/layouts/qwaf-lv5.svg      pic/qwaf-lv5.png
	convert gen/svg/layouts/ru_intl.svg       pic/ru_intl.png
	convert gen/svg/layouts/ru_intl-lv3.svg   pic/ru_intl-lv3.png
