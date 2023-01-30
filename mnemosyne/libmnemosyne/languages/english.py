#
# english.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class English(Language):

    name = _("English")
    used_for = "en"
    sublanguages = {"en-GB": _("English (UK)"),
                     "en-US": _("English (US)"),
                     "en-IN": _("English (India)"),
                     "en-AU": _("English (Australian)")}
    feature_description = _("Google translation and text-to-speech.")
