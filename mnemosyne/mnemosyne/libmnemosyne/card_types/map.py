#
# map.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.fact_view import FactView


class Map(CardType, Plugin):
    
    provides = "card_type"

    def __init__(self):
        CardType.__init__(self)
        self.id = "4"
        self.name = _("Map card type")
        self.description = _("A card type for learning locations on a map")

        # List and name the keys.
        self.fields.append(("loc", _("Location")))
        self.fields.append(("blank", _("Blank map")))
        self.fields.append(("marked", _("Marked map")))
        
        # Recognition.
        v = FactView(1, _("Recognition"))
        v.q_fields = ["marked"]
        v.a_fields = ["loc"]
        v.required_fields = ["marked", "loc"]
        self.fact_views.append(v)

        # Production.
        v = FactView(2, _("Production"))
        v.q_fields = ["loc","blank"]
        v.a_fields = ["marked"]
        v.required_fields = ["loc", "blank", "marked"]
        v.a_on_top_of_q = True
        self.fact_views.append(v)
    
        # The following field needs to be unique.
        self.unique_fields = ["loc"]

   
