WIDGETS = ui_main_window.py \
	activate_categories_dlg.py config_dlg.py change_category_dlg.py \
	add_cards_dlg.py import_dlg.py edit_cards_dlg.py \
	preview_cards_dlg.py \
	export_dlg.py main_dlg.py edit_cards_dlg.py product_tour_dlg.py \
	statistics_dlg.py about_dlg.py tip_dlg.py

WIDGETS = ui_main_window.py ui_add_cards_dlg.py ui_review_wdgt.py \
	ui_preview_cards_dlg.py ui_edit_fact_dlg.py \
	ui_convert_card_type_fields_dlg.py ui_card_appearance_dlg.py

default: $(WIDGETS)

$(WIDGETS): ui_%.py: %.ui
	pyuic4 $< > $@

clean:
	rm -f *~ *.pyc
	rm -f $(WIDGETS)
