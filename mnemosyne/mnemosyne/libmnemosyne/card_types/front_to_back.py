#
# front_to_back.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView


class FrontToBack(CardType):
    
    id = "1"
    name = _("Front-to-back only")
        
    def __init__(self):
        CardType.__init__(self)

        # List and name the keys.
        self.fields.append(("q", _("Question")))
        self.fields.append(("a", _("Answer")))

        # Front-to-back.
        v = FactView("1", _("Front-to-back"))
        v.q_fields = ["q"]
        v.a_fields = ["a"]
        v.required_fields = ["q"]
        self.fact_views.append(v)
    
        # The following field needs to be unique.
        self.unique_fields = ["q"]
 
