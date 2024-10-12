#
# french.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class French(Language):

    name = _("French")
    used_for = "fr"
    sublanguages = {"fr-FR": _("French (France)"),
                     "fr-CA": _("French (Canada)")}
    feature_description = _("Google translation and text-to-speech.")
