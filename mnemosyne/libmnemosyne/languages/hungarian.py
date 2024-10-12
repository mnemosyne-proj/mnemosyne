#
# hungarian.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Hungarian(Language):

    name = _("Hungarian")
    used_for = "hu"
    feature_description = _("Google translation and text-to-speech.")
