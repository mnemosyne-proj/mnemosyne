#
# sinhala.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Sinhala(Language):

    name = _("Sinhala (Sinhalese)")
    used_for = "si"
    feature_description = _("Google translation and text-to-speech.")
