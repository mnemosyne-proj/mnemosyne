#
# new_card_type.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.card_types.vocabulary import Vocabulary

class DecoratedVocabulary(Vocabulary):

    id = "3_decorated"
    name = _("Vocabulary (decorated)")

    # The keys we inherit from Vocabulary, we just override the FactViews.

    # Recognition.
    v1 = FactView(_("Recognition"), "3::1")
    v1.q_fact_keys = ["f"]
    v1.a_fact_keys = ["p_1", "m_1", "n"]
    v1.q_fact_key_decorators = {"f": "What is the translation of ${f}?"}

    # Production.
    v2 = FactView(_("Production"), "3::2")
    v2.q_fact_keys = ["m_1"]
    v2.a_fact_keys = ["f", "p_1", "n"]
    v2.q_fact_key_decorators = {"m_1": "How do you say ${m_1}?"}

    fact_views = [v1, v2]


# Wrap it into a Plugin and then register the Plugin.

class DecoratedVocabularyPlugin(Plugin):

    name = "Decorated vocabulary"
    description = "Vocabulary card type with some extra text"
    components = [DecoratedVocabulary]
    supported_API_level = 3

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(DecoratedVocabularyPlugin)




