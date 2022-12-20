#
# malayalam.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Malayalam(Language):

    name = _("Malayalam")
    used_for = "ml"
    feature_description = _("Google translation.")
