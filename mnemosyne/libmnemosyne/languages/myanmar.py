#
# myanmar.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Myanmar(Language):

    name = _("Myanmar (Burmese)")
    used_for = "my"
    feature_description = _("Google translation.")
