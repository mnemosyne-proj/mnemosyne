#
# gaelic.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Gaelic(Language):

    name = _("Scots Gaelic")
    used_for = "gd"
    feature_description = _("Google translation.")
