#
# front_to_back.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView


class FrontToBack(CardType):

    def __init__(self):
        CardType.__init__(self)
        self.id = "1"
        self.name = _("Front-to-back only")

        # List and name the keys.

        self.fields.append(("q", _("Question")))
        self.fields.append(("a", _("Answer")))

        # Front-to-back.

        v = FactView(_("Front-to-back"))
        v.q_fields = ["q"]
        v.a_fields = ["a"]
        v.required_fields = ["q"]
        self.fact_views.append(v)
