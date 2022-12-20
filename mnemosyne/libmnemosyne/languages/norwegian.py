#
# norwegian.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Norwegian(Language):

    name = _("Norwegian")
    used_for = "no"
    feature_description = _("Google translation and text-to-speech.")
