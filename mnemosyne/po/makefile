LANGS = ../mo/de/LC_MESSAGES/mnemosyne.mo

default: $(LANGS)

$(LANGS): ../mo/%/LC_MESSAGES/mnemosyne.mo: %.po
	mkdir -p `dirname $@`
	./msgfmt.py -o $@ $<

clean:
	rm -rf ../mo
