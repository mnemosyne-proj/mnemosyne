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
    fields = [("q", _("Question")),
              ("a", _("Answer"))]
    
    # Front-to-back.
    v = FactView("1", _("Front-to-back"))
    v.q_fields = ["q"]
    v.a_fields = ["a"]
    v.required_fields = ["q"]

    fact_views = [v]
    
    # The following field needs to be unique.
    unique_fields = ["q"]
