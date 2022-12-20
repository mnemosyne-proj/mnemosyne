#
# turkish.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Turkish(Language):

    name = _("Turkish")
    used_for = "tr"
    feature_description = _("Google translation and text-to-speech.")
