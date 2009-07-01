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
             "last_variant_for_statistics_page": {} # dict[page] = variant
            }.items():
            self.config().setdefault(key, value)
