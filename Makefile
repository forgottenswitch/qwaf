all: gen

gen: conv.py compat symbols types hjkl layouts letters_latin letters_cyr
	 python3 conv.py -o gen layouts

.PHONY: clean
clean:
	@rm -r gen
