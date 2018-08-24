#
# __init__.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class French(Language):

    name = _("French")
    used_for = "fr"
    feature_description = _("Google TTS and translation.")
