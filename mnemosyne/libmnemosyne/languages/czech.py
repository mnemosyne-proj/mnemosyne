#
# czech.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Czech(Language):

    name = _("Czech")
    used_for = "cs"
    feature_description = _("Google translation and text-to-speech.")
