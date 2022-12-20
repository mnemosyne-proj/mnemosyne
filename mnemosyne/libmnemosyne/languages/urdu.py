#
# urdu.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Urdu(Language):

    name = _("Urdu")
    used_for = "ur"
    feature_description = _("Google translation.")
