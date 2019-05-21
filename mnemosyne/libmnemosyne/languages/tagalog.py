#
# tagalog.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Tagalog(Language):

    name = _("Tagalog (Filipino)")
    used_for = "tl"
    feature_description = _("Google translation.")
