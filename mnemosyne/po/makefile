PYTHON      := python
# If `python3` exists:
ifeq (1,$(shell python3 -c "print(1)" 2>&- ))
PYTHON      := python3
endif

LANGS = ../mo/cs/LC_MESSAGES/mnemosyne.mo \
	../mo/da/LC_MESSAGES/mnemosyne.mo \
	../mo/de/LC_MESSAGES/mnemosyne.mo \
	../mo/eo/LC_MESSAGES/mnemosyne.mo \
	../mo/es/LC_MESSAGES/mnemosyne.mo \
	../mo/fa/LC_MESSAGES/mnemosyne.mo \
	../mo/fr/LC_MESSAGES/mnemosyne.mo \
	../mo/he/LC_MESSAGES/mnemosyne.mo \
	../mo/hr/LC_MESSAGES/mnemosyne.mo \
	../mo/hu/LC_MESSAGES/mnemosyne.mo \
	../mo/id/LC_MESSAGES/mnemosyne.mo \
	../mo/it/LC_MESSAGES/mnemosyne.mo \
	../mo/ja/LC_MESSAGES/mnemosyne.mo \
	../mo/nb/LC_MESSAGES/mnemosyne.mo \
	../mo/nl/LC_MESSAGES/mnemosyne.mo \
	../mo/pl/LC_MESSAGES/mnemosyne.mo \
	../mo/pt_BR/LC_MESSAGES/mnemosyne.mo \
	../mo/pt/LC_MESSAGES/mnemosyne.mo \
	../mo/ru/LC_MESSAGES/mnemosyne.mo \
	../mo/tr/LC_MESSAGES/mnemosyne.mo \
	../mo/zh_CN/LC_MESSAGES/mnemosyne.mo \
	../mo/zh_HK/LC_MESSAGES/mnemosyne.mo \
	../mo/zh_TW/LC_MESSAGES/mnemosyne.mo \
	../mo/gl/LC_MESSAGES/mnemosyne.mo \
	../mo/ca/LC_MESSAGES/mnemosyne.mo \
	../mo/ca@valencia/LC_MESSAGES/mnemosyne.mo \
	../mo/uk/LC_MESSAGES/mnemosyne.mo \
	../mo/sv/LC_MESSAGES/mnemosyne.mo \
	../mo/sr/LC_MESSAGES/mnemosyne.mo

# don't copy am and vi (unless updated), en_GB, zh_SH, nb_no

default: $(LANGS)

$(LANGS): ../mo/%/LC_MESSAGES/mnemosyne.mo: %.po
	mkdir -p `dirname $@`
	$(PYTHON) ./msgfmt.py -o $@ $<

clean:
	rm -rf *~
	rm -rf ../mo

update:
	cd ../mnemosyne/pyqt_ui && make
	$(PYTHON) ./pygettext -o mnemosyne.pot ..
