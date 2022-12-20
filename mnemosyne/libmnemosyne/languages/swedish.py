#
# swedish.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Swedish(Language):

    name = _("Swedish")
    used_for = "sv"
    feature_description = _("Google translation and text-to-speech.")
