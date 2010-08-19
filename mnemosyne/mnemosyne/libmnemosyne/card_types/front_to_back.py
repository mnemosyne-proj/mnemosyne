#
# front_to_back.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView


class FrontToBack(CardType):
    
    id = "1"
    name = _("Front-to-back only")
    
    # List and name the keys.
    fields = [("q", _("Question"), None),
              ("a", _("Answer"), None)]
    
    # Front-to-back.
    v = FactView(_("Front-to-back"), "1::1")
    v.q_fields = ["q"]
    v.a_fields = ["a"]

    fact_views = [v]   
    unique_fields = ["q"]
    required_fields = ["q"]
