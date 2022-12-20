#
# spanish.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Spanish(Language):

    name = _("Spanish")
    used_for = "es"
    sublanguages = {"es-ES": _("Spanish (Spain)"),
                     "es-US": _("Spanish (US)")}
    feature_description = _("Google translation and text-to-speech.")
