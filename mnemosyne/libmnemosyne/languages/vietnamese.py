#
# vietnamese.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Vietnamese(Language):

    name = _("Vietnamese")
    used_for = "vi"
    feature_description = _("Google translation and text-to-speech.")
