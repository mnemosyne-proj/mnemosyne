#
# german.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class German(Language):

    name = _("German")
    used_for = "de"
    feature_description = _("Google translation and text-to-speech.")
