LANGS = de.mo

default: $(LANGS)

$(LANGS): %.mo: %.po
	./msgfmt.py $<

clean:
	rm -f *~ *.mo
