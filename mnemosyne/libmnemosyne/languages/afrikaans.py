#
# afrikaans.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Afrikaans(Language):

    name = _("Afrikaans")
    used_for = "af"
    feature_description = _("Google translation.")
