#
# mongolian.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Mongolian(Language):

    name = _("Mongolian")
    used_for = "mn"
    feature_description = _("Google translation.")
