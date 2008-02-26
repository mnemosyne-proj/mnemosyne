WIDGETS = activate_categories_frm.py config_frm.py change_category_frm.py \
	add_cards_frm.py import_frm.py edit_cards_frm.py \
	preview_cards_frm.py \
	export_frm.py main_frm.py edit_cards_frm.py product_tour_frm.py \
	statistics_frm.py about_frm.py tip_frm.py

WIDGETS = main_frm.py add_cards_frm.py

default: $(WIDGETS)

$(WIDGETS): %.py: %.ui
	pyuic4 $< > $@

clean:
	rm -f *~ *.pyc
	rm -f $(WIDGETS)
