#
# prefill_tag_behaviour_plugin.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.plugin import Plugin


class PrefillTagBehaviourPlugin(Plugin):

    name = _("Prefill tag behaviour")
    description = \
_("""When creating new cards, Mnemosyne normally prefills the 'Tag(s)' field with the last value you used, regardless of card type.\n
With this plugin, Mnemosyne will for each card type remember the last tag you used, such that e.g. Chinese cards get a prefilled tag like "My Chinese textbook::Chapter 10", whereas Front-to-Back cards get "European Capitals".""")
    supported_API_level = 3

    def activate(self):
        Plugin.activate(self)
        self.config()["is_last_used_tags_per_card_type"] = True

    def deactivate(self):
        Plugin.deactivate(self)
        self.config()["is_last_used_tags_per_card_type"] = False
