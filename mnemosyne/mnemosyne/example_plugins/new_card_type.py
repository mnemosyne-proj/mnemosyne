#
# new_card_type.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.card_types.vocabulary import Vocabulary

class DecoratedVocabulary(Vocabulary):

    id = "3_decorated"
    name = _("Vocabulary (decorated)")

    # The fields we inherit from Vocabulary, we just override the FactViews.

    # Recognition.
    v1 = FactView(_("Recognition"), "3::1")
    v1.q_fields = ["f"]
    v1.a_fields = ["p_1", "m_1", "n"]
    v1.q_field_decorators = {"f": "What is the translation of ${f}?"}
    
    # Production.
    v2 = FactView(_("Production"), "3::2")
    v2.q_fields = ["m_1"]
    v2.a_fields = ["f", "p_1", "n"]
    v2.q_field_decorators = {"m_1": "How do you say ${m_1}?"}
    
    fact_views = [v1, v2]
    

# Wrap it into a Plugin and then register the Plugin.

class DecoratedVocabularyPlugin(Plugin):
    
    name = "Decorated vocabulary"
    description = "Vocabulary card type with some extra text"
    components = [DecoratedVocabulary]

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(DecoratedVocabularyPlugin)




