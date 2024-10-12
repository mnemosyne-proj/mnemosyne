#
# map.py <Peter.Bienstman@gmail.com>
#

import copy

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.fact_view import FactView


class Map(CardType):

    id = "4"
    name = _("Map")

    # List and name the keys.
    fact_keys_and_names = [("loc", _("Location")),
                           ("blank", _("Blank map")),
                           ("marked", _("Marked map"))]

    # Recognition.
    v1 = FactView(_("Recognition"), "4.1")
    v1.q_fact_keys = ["_", "marked"]
    v1.a_fact_keys = ["loc", "marked"]
    v1.a_on_top_of_q = True

    # Production.
    v2 = FactView(_("Production"), "4.2")
    v2.q_fact_keys = ["loc", "blank"]
    v2.a_fact_keys = ["loc", "marked"]
    v2.a_on_top_of_q = True

    fact_views = [v1, v2]
    unique_fact_keys = ["loc"]
    required_fact_keys = ["loc", "blank", "marked"]

    def fact_data(self, card):
        _fact_data = copy.copy(card.fact.data)
        _fact_data["_"] = "&nbsp;"  # Insert a blank line to improve layout.
        return _fact_data

    def fact_key_format_proxies(self):
        return {"loc": "loc", "blank": "blank",
                "marked": "marked", "_": "loc"}


class MapPlugin(Plugin):

    name = _("Map")
    description = _("""A card type for learning locations on a map.\n
Displays the answer map on top of the question map, rather than below it as a second map.""")
    components = [Map]
    supported_API_level = 3
