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
    fields = [("f", _("Front"), None),
              ("b", _("Back"), None)]
    
    # Front-to-back.
    v = FactView(_("Front-to-back"), "1::1")
    v.q_fields = ["f"]
    v.a_fields = ["b"]

    fact_views = [v]   
    unique_fields = ["f"]
    required_fields = ["f"]
