#
# russian.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Russian(Language):

    name = _("Russian")
    used_for = "ru"
    feature_description = _("Google translation and text-to-speech.")
