WIDGETS = ui_main_window.py ui_add_cards_dlg.py ui_review_wdgt.py \
	ui_preview_cards_dlg.py ui_edit_fact_dlg.py \
	ui_convert_card_type_fields_dlg.py ui_card_appearance_dlg.py \
	ui_activate_plugins_dlg.py ui_cloned_card_types_list_dlg.py \
	ui_clone_card_type_dlg.py

default: $(WIDGETS)
	pyrcc4 mnemosyne.qrc

$(WIDGETS): ui_%.py: %.ui
	pyuic4 $< > $@

clean:
	rm -f *~ *.pyc
	rm -f $(WIDGETS)
