#
# greek.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Greek(Language):

    name = _("Greek")
    used_for = "el"
    feature_description = _("Google translation and text-to-speech.")
