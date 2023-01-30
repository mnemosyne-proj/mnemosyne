#
# chinese.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Chinese(Language):

    name = _("Chinese")
    used_for = "zh"
    sublanguages = {"zh-CN": _("Chinese (Simplified)"),
                     "zh-TW": _("Chinese (Traditional)")}
    feature_description = _("Google translation and text-to-speech.")
