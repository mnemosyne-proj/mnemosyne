#
# korean.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Korean(Language):

    name = _("Korean")
    used_for = "ko"
    feature_description = _("Google translation and text-to-speech.")
