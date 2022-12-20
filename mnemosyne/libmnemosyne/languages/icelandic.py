#
# icelandic.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Icelandic(Language):

    name = _("Icelandic")
    used_for = "is"
    feature_description = _("Google translation and text-to-speech.")
