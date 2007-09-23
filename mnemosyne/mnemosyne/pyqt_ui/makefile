WIDGETS = activate_categories_frm.py config_frm.py change_category_frm.py \
	add_items_frm.py import_frm.py edit_items_frm.py preview_item_frm.py \
	export_frm.py main_frm.py edit_item_frm.py product_tour_frm.py \
	statistics_frm.py

default: $(WIDGETS)

$(WIDGETS): %.py: %.ui
	pyuic $< > $@
	echo "from qtextedit2 import *" > tmp
	sed 's/QTextEdit(/QTextEdit2(/' $@ >> tmp
	mv tmp $@

clean:
	rm -f *~ *.pyc
	rm -f $(WIDGETS)