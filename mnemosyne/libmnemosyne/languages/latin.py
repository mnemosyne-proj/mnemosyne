#
# latin.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Latin(Language):

    name = _("Latin")
    used_for = "la"
    feature_description = _("Google translation.")
