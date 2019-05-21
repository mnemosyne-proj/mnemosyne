#
# hindi.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Hindi(Language):

    name = _("Hindi")
    used_for = "hi"
    feature_description = _("Google translation.")
