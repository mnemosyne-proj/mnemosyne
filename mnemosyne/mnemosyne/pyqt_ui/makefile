WIDGETS = activate_categories_dlg.py config_dlg.py change_category_dlg.py \
	add_cards_dlg.py import_dlg.py edit_cards_dlg.py \
	preview_cards_dlg.py \
	export_dlg.py main_dlg.py edit_cards_dlg.py product_tour_dlg.py \
	statistics_dlg.py about_dlg.py tip_dlg.py

WIDGETS = main_dlg.py #add_cards_dlg.py card_twosided.py

default: $(WIDGETS)

$(WIDGETS): %.py: %.ui
	pyuic4 $< > $@

clean:
	rm -f *~ *.pyc
	rm -f $(WIDGETS)
