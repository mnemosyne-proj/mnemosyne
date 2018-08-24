#
# __init__.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Arabic(Language):

    name = _("Arabic")
    used_for = "ar"
    feature_description = _("Google TTS and translation.")
