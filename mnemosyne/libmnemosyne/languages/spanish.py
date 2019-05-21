#
# spanish.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.language import Language


class Spanish(Language):

    name = _("Spanish")
    used_for = "es"
    sub_languages = {"es_ES", _("Spanish (Spain)"),
                     "es_US", _("Spanish (US)")}
    feature_description = _("Google translation.")
