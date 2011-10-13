LANGS = ../mo/de/LC_MESSAGES/mnemosyne.mo

default: $(LANGS)

$(LANGS): ../mo/%/LC_MESSAGES/mnemosyne.mo: %.po
	mkdir -p `dirname $@`
	./msgfmt.py -o $@ $<

clean:
	rm -rf *~
	rm -rf ../mo

update:
	cd ../mnemosyne/pyqt_ui && make
	pygettext -o mnemosyne.pot ..
