WIDGETS = ui_main_wdgt.py ui_add_cards_dlg.py \
	ui_edit_card_dlg.py \
	ui_convert_card_type_keys_dlg.py ui_about_dlg.py \
	ui_manage_plugins_dlg.py ui_manage_card_types_dlg.py \
	ui_clone_card_type_dlg.py ui_configuration_wdgt_main.py \
	ui_configuration_wdgt_card_appearance.py \
	ui_activate_cards_dlg.py ui_card_set_name_dlg.py \
	ui_configuration_dlg.py ui_criterion_wdgt_default.py \
	ui_statistics_dlg.py ui_sync_dlg.py ui_configuration_wdgt_sync_server.py \
	ui_browse_cards_dlg.py ui_rename_tag_dlg.py ui_change_card_type_dlg.py \
	ui_add_tags_dlg.py ui_remove_tags_dlg.py ui_getting_started_dlg.py \
	ui_tip_dlg.py ui_import_dlg.py ui_compact_database_dlg.py \
	ui_delete_unused_media_files_dlg.py ui_rename_card_type_dlg.py \
	ui_export_dlg.py ui_export_metadata_dlg.py

default: $(WIDGETS) ui_review_wdgt.py ui_preview_cards_dlg.py
	pyrcc4 mnemosyne.qrc -o mnemosyne_rc.py

ui_review_wdgt.py: review_wdgt.ui
	$(PYTHON) ./pyuic4 $< > tmp
	sed -f fix_review_widget_ui.sed <  tmp > $@

ui_preview_cards_dlg.py: preview_cards_dlg.ui
	$(PYTHON) ./pyuic4 $< > tmp
	sed -f fix_review_widget_ui.sed <  tmp > $@

$(WIDGETS): ui_%.py: %.ui
	$(PYTHON) ./pyuic4 $< > $@

clean:
	rm -f *~ *.pyc
	rm -f $(WIDGETS) ui_review_wdgt.py ui_preview_cards_dlg.py
	rm -f mnemosyne_rc.py