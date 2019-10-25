#
# nyanja.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Nyanja(Language):

    name = _("Nyanja (Chichewa)")
    used_for = "ny"
    feature_description = _("Google translation.")
