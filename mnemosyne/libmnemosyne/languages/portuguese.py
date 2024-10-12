#
# portuguese.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Portuguese(Language):

    name = _("Portuguese")
    used_for = "pt"
    sublanguages = {"pt-PT": _("Portugese (Portugal)"),
                     "pt-BR": _("Portugese (Brazilian)")}
    feature_description = _("Google translation and text-to-speech.")
