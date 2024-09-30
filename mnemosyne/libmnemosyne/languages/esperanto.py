#
# esperanto.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Esperanto(Language):

    name = _("Esperanto")
    used_for = "eo"
    feature_description = _("Google translation.")
