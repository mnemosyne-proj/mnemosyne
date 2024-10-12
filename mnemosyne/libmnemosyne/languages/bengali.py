#
# bengali.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Bengali(Language):

    name = _("Bengali")
    used_for = "bn"
    sublanguages = {"bn-BD": _("Bengali (Bangladesh"),
                     "bn-ID": _("Bengali (India)")}
    feature_description = _("Google translation and text-to-speech.")
