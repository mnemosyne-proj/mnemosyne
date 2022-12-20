#
# dutch.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Dutch(Language):

    name = _("Dutch")
    used_for = "nl"
    feature_description = _("Google translation and text-to-speech.")
