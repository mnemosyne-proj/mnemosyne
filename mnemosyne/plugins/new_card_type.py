#
# new_card_type.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.card_types.three_sided import ThreeSided

class DecoratedThreeSided(ThreeSided):

    id = "3_decorated"
    name = _("Foreign word with pronunciation (decorated)")

    # The fields we inherit from ThreeSided, we just override the FactViews.

    # Recognition.
    v1 = FactView(_("Recognition"), "3::1")
    v1.q_fields = ["f"]
    v1.a_fields = ["p", "t"]
    v1.q_field_decorators = {"f": "What is the translation of ${f}?"}
    
    # Production.
    v2 = FactView(_("Production"), "3::2")
    v2.q_fields = ["t"]
    v2.a_fields = ["f", "p"]
    v2.q_field_decorators = {"t": "How do you say ${t}?"}
    
    fact_views = [v1, v2]
    

# Wrap it into a Plugin and then register the Plugin.

class DecoratedThreeSidedPlugin(Plugin):
    
    name = "Decorated three-sided"
    description = "Three-sided card type with some extra text"
    components = [DecoratedThreeSided]

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(DecoratedThreeSidedPlugin)




