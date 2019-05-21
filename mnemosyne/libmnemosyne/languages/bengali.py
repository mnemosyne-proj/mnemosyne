#
# bengali.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Bengali(Language):

    name = _("Bengali")
    used_for = "bn"
    sub_languages = {"bn_BD": _("Bengali (Bangladesh"),
                     "bn_ID": _("Bengali (India)")}
    feature_description = _("Google translation.")
