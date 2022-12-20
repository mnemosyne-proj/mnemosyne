#
# japanese.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Japanese(Language):

    name = _("Japanese")
    used_for = "ja"
    feature_description = _("Google translation and text-to-speech.")
