#
# configuration.py <Peter.Bienstman@gmail.com>
#

import os

from mnemosyne.libmnemosyne.hook import Hook


class PyQtConfiguration(Hook):

    used_for = "configuration_defaults"

    def run(self):
        for key, value in \
            list({"list_font": None,
             "last_used_card_type_id": "",
             "is_last_used_tags_per_card_type": False,
             "last_used_tags_for_card_type_id": {},
             "last_used_tags": "",
             "sort_column": None,
             "sort_order": None,
             "previous_statistics_page": 0,
             "previous_configuration_wdgt": 0,
             "previous_variant_for_statistics_page": {}, # dict[page] = variant
             "main_window_state": None,
             "add_cards_dlg_state": None,
             "preview_cards_dlg_state": None,
             "edit_card_dlg_state": None,
             "manage_card_types_dlg_state": None,
             "edit_M_sided_card_type_dlg_state": None,
             "plugins_dlg_state": None,
             "sync_dlg_state": None,
             "clone_help_shown": False,
             "browse_cards_dlg_state": None,
             "browse_cards_dlg_splitter_1_state": None,
             "browse_cards_dlg_splitter_2_state": None,
             "browse_cards_dlg_table_settings": None,
             "tag_tree_wdgt_state": None,
             "statistics_dlg_state": None,
             "configuration_dlg_state": None,
             "activate_cards_dlg_state": None,
             "activate_cards_dlg_splitter_state": None,
             "sync_help_shown": False,
             "server_for_sync_as_client": "",
             "port_for_sync_as_client": 8512,
             "username_for_sync_as_client": "",
             "password_for_sync_as_client": "",
             "remember_password_for_sync_as_client": True,
             "started_add_edit_cards_n_times": 0,
             "started_browse_cards_n_times": 0,
             "started_activate_cards_n_times": 0,
             "showed_help_on_renaming_sets": False,
             "showed_help_on_double_clicking_sets": False,
             "showed_help_on_adding_tags": False
            }.items()):
            self.config().setdefault(key, value)
