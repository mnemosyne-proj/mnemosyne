#
# romanian.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Romanian(Language):

    name = _("Romanian")
    used_for = "ro"
    feature_description = _("Google translation and text-to-speech.")
