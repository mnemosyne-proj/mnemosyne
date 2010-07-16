#
# configuration.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.hook import Hook
from mnemosyne.libmnemosyne.translator import _


class PyQtConfiguration(Hook):

    used_for = "configuration_defaults"

    def run(self):
        for key, value in \
            {"list_font": None,
             "card_type_name_of_last_added": "",
             "tags_of_last_added": _("<default>"),
             "sort_column": None,
             "sort_order": None,
             "last_statistics_page": 0,
             "last_configuration_wdgt": 0,
             "last_variant_for_statistics_page": {}, # dict[page] = variant
             "main_window_size": (0, 0),
             "add_widget_size": (0, 0),
             "edit_widget_size": (0, 0),
             "plugins_dlg_size": (0, 0),
             "statistics_dlg_size": (0, 0),
             "configuration_dlg_size": (0, 0),
             "activate_cards_dlg_size": (0, 0),
             "activate_cards_dlg_splitter": None,
             "sync_help_shown": False,
             "sync_as_client_server": "",
             "sync_as_client_port": 8512,
             "sync_as_client_username": "",
             "sync_as_client_password": ""
            }.items():
            self.config().setdefault(key, value)
