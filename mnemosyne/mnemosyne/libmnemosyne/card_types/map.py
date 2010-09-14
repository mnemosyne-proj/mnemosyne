#
# map.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.fact_view import FactView


class Map(CardType):

    id = "4"
    name = _("Map")

    # List and name the keys.
    fields = [("loc", _("Location"), None),
              ("blank", _("Blank map"), None),
              ("marked", _("Marked map"), None)]

    # Recognition.
    v1 = FactView(_("Recognition"), "4::1")
    v1.q_fields = ["marked"]
    v1.a_fields = ["loc", "marked",]
    v1.a_on_top_of_q = True
    
    # Production.
    v2 = FactView(_("Production"), "4::2")
    v2.q_fields = ["loc", "blank"]
    v2.a_fields = ["loc", "marked"]
    v2.a_on_top_of_q = True

    fact_views = [v1, v2]
    unique_fields = ["loc"]
    required_fields = ["loc", "blank", "marked"]


class MapPlugin(Plugin):
    
    name = _("Map")
    description = _("A card type for learning locations on a map")
    components = [Map]

