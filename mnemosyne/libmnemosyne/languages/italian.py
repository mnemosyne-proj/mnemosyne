#
# italian.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Italian(Language):

    name = _("Italian")
    used_for = "it"
    feature_description = _("Google translation and text-to-speech.")
