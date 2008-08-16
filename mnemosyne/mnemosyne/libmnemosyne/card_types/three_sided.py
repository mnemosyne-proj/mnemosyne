#
# three_sided.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView


class ThreeSided(CardType):

    def __init__(self, language_name=""):
        CardType.__init__(self)
        if not language_name:
            self.id = "3"
            self.name = _("Foreign word with pronunciation")
            self.is_language = False
        else:
            self.id = "3_" + language_name
            self.name = language_name
            self.is_language = True

        # List and name the keys.

        self.fields.append(("f", _("Foreign word")))
        self.fields.append(("p", _("Pronunciation")))
        self.fields.append(("t", _("Translation")))

        # Recognition.

        v = FactView(1, _("Recognition"))
        v.q_fields = ["f"]
        v.a_fields = ["p", "t"]
        v.required_fields = ["f"]
        self.fact_views.append(v)

        # Production.

        v = FactView(2, _("Production"))
        v.q_fields = ["t"]
        v.a_fields = ["f", "p"]
        v.required_fields = ["t"]
        self.fact_views.append(v)
