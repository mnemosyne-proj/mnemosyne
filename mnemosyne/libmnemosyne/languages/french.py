#
# french.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class French(Language):

    name = _("French")
    used_for = "fr"
    sub_languages = {"fr_FR": _("French (France)"),
                     "fr_CA": _("French (Canada)")}
    feature_description = _("Google translation.")
