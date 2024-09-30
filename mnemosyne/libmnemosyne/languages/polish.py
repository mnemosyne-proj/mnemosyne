#
# polish.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Polish(Language):

    name = _("Polish")
    used_for = "pl"
    feature_description = _("Google translation and text-to-speech.")
