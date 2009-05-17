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
    fields = [("loc", _("Location")),
              ("blank", _("Blank map")),
              ("marked", _("Marked map"))]

    # Recognition.
    v1 = FactView("1", _("Recognition"))
    v1.q_fields = ["marked"]
    v1.a_fields = ["loc"]
    v1.required_fields = ["marked", "loc"]

    # Production.
    v2 = FactView("2", _("Production"))
    v2.q_fields = ["loc", "blank"]
    v2.a_fields = ["marked"]
    v2.required_fields = ["loc", "blank", "marked"]
    v2.a_on_top_of_q = True

    fact_views = [v1, v2]

    # The following field needs to be unique.
    unique_fields = ["loc"]


class MapPlugin(Plugin):
    
    name = _("Map")
    description = _("A card type for learning locations on a map")
    components = [Map]

