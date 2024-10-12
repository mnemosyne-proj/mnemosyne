#
# hebrew.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Hebrew(Language):

    name = _("Hebrew")
    used_for = "he"
    feature_description = _("Google translation.")
