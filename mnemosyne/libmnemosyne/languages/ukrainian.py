#
# ukrainian.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Ukrainian(Language):

    name = _("Ukrainian")
    used_for = "uk"
    feature_description = _("Google translation and text-to-speech.")
