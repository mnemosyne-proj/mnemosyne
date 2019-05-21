#
# portuguese.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Portuguese(Language):

    name = _("Portuguese")
    used_for = "pt"
    sub_languages = {"pt_PT": _("Portugese (Portugal)"),
                     "pt_BR": _("Portugese (Brazilian)")}
    feature_description = _("Google translation.")
