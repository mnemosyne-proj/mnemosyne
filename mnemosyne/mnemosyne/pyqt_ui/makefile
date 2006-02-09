WIDGETS = activate_categories_frm.py config_frm.py \
	add_items_frm.py import_frm.py edit_items_frm.py  \
	export_frm.py main_frm.py edit_item_frm.py product_tour_frm.py

default: $(WIDGETS)

$(WIDGETS): %.py: %.ui
	pyuic $< > $@

clean:
	rm -f *~ *.pyc
	rm -f $(WIDGETS)