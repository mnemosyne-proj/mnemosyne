#
# three_sided.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView


class ThreeSided(CardType):

    def __init__(self, language_name=""):
        CardType.__init__(self)
        if not language_name:
            self.id = "3"
            self.name = _("Foreign word with pronunciation")
            self.is_language = False
        else:
            self.id = "3_" + language_name
            self.name = language_name
            self.is_language = True

        # List and name the keys.
        self.fields.append(("f", _("Foreign word")))
        self.fields.append(("p", _("Pronunciation")))
        self.fields.append(("t", _("Translation")))

        # Recognition.
        v = FactView(1, _("Recognition"))
        v.q_fields = ["f"]
        v.a_fields = ["p", "t"]
        v.required_fields = ["f"]
        self.fact_views.append(v)

        # Production.
        v = FactView(2, _("Production"))
        v.q_fields = ["t"]
        v.a_fields = ["f", "p"]
        v.required_fields = ["t"]
        self.fact_views.append(v)
    
        # The foreign word field needs to be unique. As for duplicates is the
        # answer field, these are better handled through a synonym detection 
        # plugin.
        self.unique_fields = ["f"]
        
        # CSS.
        self.css = """
            <style type="text/css">
            table { margin-left: auto;
                margin-right: auto; /* Centers  table, but not its contents. */
                height: 100%; }
            body {  color: black;
                background-color: white;
                margin: 0;
                padding: 0;
                border: thin solid #8F8F8F; }
            f { font-weight: bold;
                text-align: center; } /* Align contents within the cell. */
            t { text-align: center; }
            p { color: green;
                text-align: center; }               
            </style>
        """
