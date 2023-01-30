#
# front_to_back.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView


class FrontToBack(CardType):

    id = "1"
    name = _("Front-to-back only")

    # List and name the keys.
    fact_keys_and_names = [("f", _("Front")),
                           ("b", _("Back"))]

    # Front-to-back.
    v = FactView(_("Front-to-back"), "1.1")
    v.q_fact_keys = ["f"]
    v.a_fact_keys = ["b"]

    fact_views = [v]
    unique_fact_keys = ["f"]
    required_fact_keys = ["f"]
