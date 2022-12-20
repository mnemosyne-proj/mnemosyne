#
# thai.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Thai(Language):

    name = _("Thai")
    used_for = "th"
    feature_description = _("Google translation and text-to-speech.")
