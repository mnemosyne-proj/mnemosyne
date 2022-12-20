#
# indonesian.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Indonesian(Language):

    name = _("Indonesian")
    used_for = "id"
    feature_description = _("Google translation and text-to-speech.")
