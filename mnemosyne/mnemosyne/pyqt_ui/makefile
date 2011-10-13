WIDGETS = ui_main_wdgt.py ui_add_cards_dlg.py \
	ui_preview_cards_dlg.py ui_edit_card_dlg.py \
	ui_convert_card_type_keys_dlg.py ui_card_appearance_dlg.py \
	ui_activate_plugins_dlg.py ui_cloned_card_types_list_dlg.py \
	ui_clone_card_type_dlg.py ui_configuration_wdgt_main.py \
	ui_activate_cards_dlg.py ui_card_set_name_dlg.py \
	ui_configuration_dlg.py ui_criterion_wdgt_default.py \
	ui_statistics_dlg.py ui_sync_dlg.py ui_configuration_wdgt_sync_server.py \
	ui_browse_cards_dlg.py ui_rename_tag_dlg.py ui_change_card_type_dlg.py \
	ui_add_tags_dlg.py ui_remove_tags_dlg.py ui_getting_started_dlg.py \
	ui_tip_dlg.py ui_import_dlg.py

default: $(WIDGETS) ui_review_wdgt.py 
	pyrcc4 mnemosyne.qrc -o mnemosyne_rc.py

ui_review_wdgt.py: review_wdgt.ui
	./pyuic4 $< > $@
	sed -i -e '11ifrom qpushbutton2 import *'\
		-e '11ifrom qwebview2 import *'\
		-e 's/QtGui.QPushButton(/QPushButton2(/'\
		-e 's/QtWebKit.QWebView(/QWebView2(/'\
		$@

$(WIDGETS): ui_%.py: %.ui
	./pyuic4 $< > $@

clean:
	rm -f *~ *.pyc
	rm -f $(WIDGETS) ui_review_wdgt.py
	rm -f mnemosyne_rc.py
