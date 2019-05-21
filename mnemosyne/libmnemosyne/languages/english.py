#
# english.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class English(Language):

    name = _("English")
    used_for = "en"
    sub_languages = {"en_GB": _("English (UK)"),
                     "en_US": _("English (US)"),
                     "en_IN": _("English (India)"),
                     "en_AU", _("English (Australian)")}
    feature_description = _("Google translation.")
