#
# configuration.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.hook import Hook


class PyQtConfiguration(Hook):

    used_for = "configuration_defaults"

    def run(self):
        for key, value in \
            {"list_font": None,
             "last_used_card_type_id": "",
             "last_used_tags_for_card_type_id": {},
             "import_dir": self.config().data_dir,
             "import_format": None,
             "import_extra_tag_name": "",
             "export_dir": self.config().data_dir,
             "export_format": None,
             "sort_column": None,
             "sort_order": None,
             "previous_statistics_page": 0,
             "previous_configuration_wdgt": 0,
             "previous_variant_for_statistics_page": {}, # dict[page] = variant
             "main_window_state": None,
             "add_cards_dlg_state": None,
             "preview_cards_dlg_state": None,
             "edit_card_dlg_state": None,
             "plugins_dlg_state": None,
             "clone_help_shown": False,
             "browse_cards_dlg_state": None,
             "browse_cards_dlg_splitter_1_state": None,
             "browse_cards_dlg_splitter_2_state": None,
             "browse_cards_dlg_table_settings": None,   
             "statistics_dlg_state": None,
             "configuration_dlg_state": None,
             "activate_cards_dlg_state": None,
             "activate_cards_dlg_splitter_state": None,           
             "sync_help_shown": False,
             "server_for_sync_as_client": "",
             "port_for_sync_as_client": 8512,
             "username_for_sync_as_client": "",
             "password_for_sync_as_client": "",
             "port_for_sync_as_server": 8512,
             "remote_access_username": "",
             "remote_access_password": ""
            }.items():
            self.config().setdefault(key, value)
