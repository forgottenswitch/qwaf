OUTDIR = gen

all: $(OUTDIR)

$(OUTDIR): conv.py compat symbols types hjkl layouts letters_latin letters_cyr
	 python3 conv.py -o $@ layouts

.PHONY: clean
clean:
	@rm -r $(OUTDIR)
