#
# __init__.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class English(Language):

    name = _("English")
    used_for = "en"
    feature_description = _("Google TTS and translation.")
