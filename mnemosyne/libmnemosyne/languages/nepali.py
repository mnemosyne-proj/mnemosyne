#
# nepali.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Nepali(Language):

    name = _("Nepali")
    used_for = "ne"
    feature_description = _("Google translation and text-to-speech.")
