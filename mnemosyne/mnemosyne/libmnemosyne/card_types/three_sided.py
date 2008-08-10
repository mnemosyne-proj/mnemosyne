#
# three_sided.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView


class ThreeSided(CardType):

    def __init__(self):
        CardType.__init__(self)
        self.id = 3
        self.name = _("Foreign word with pronunciation")

        # Name the keys.

        self.fields["f"] = _("Foreign word")
        self.fields["p"] = _("Pronunciation")
        self.fields["t"] = _("Translation")

        # Recognition.

        v = FactView(_("Recognition"))
        v.q_fields = ["f"]
        v.a_fields = ["p", "t"]
        v.required_fields = ["f"]
        self.fact_views.append(v)

        # Production.

        v = FactView(_("Production"))
        v.q_fields = ["t"]
        v.a_fields = ["f", "p"]
        v.required_fields = ["t"]
        self.fact_views.append(v)
