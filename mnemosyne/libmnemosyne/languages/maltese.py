#
# maltese.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Maltese(Language):

    name = _("Maltese")
    used_for = "mt"
    feature_description = _("Google translation.")
