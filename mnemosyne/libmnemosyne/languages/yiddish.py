#
# yiddish.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Yiddish(Language):

    name = _("Yiddish")
    used_for = "yi"
    feature_description = _("Google translation.")
