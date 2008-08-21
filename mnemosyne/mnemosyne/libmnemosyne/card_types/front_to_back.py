#
# front_to_back.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView


class FrontToBack(CardType):

    def __init__(self):
        CardType.__init__(self)
        self.id = "1"
        self.name = _("Front-to-back only")

        # List and name the keys.
        self.fields.append(("q", _("Question")))
        self.fields.append(("a", _("Answer")))

        # Front-to-back.
        v = FactView(1, _("Front-to-back"))
        v.q_fields = ["q"]
        v.a_fields = ["a"]
        v.required_fields = ["q"]
        self.fact_views.append(v)
    
        # The following field needs to be unique.
        self.unique_fields = ["q"]
        
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
            q { text-align: center; } /* Align contents within the cell. */
            a { text-align: center; }
            </style>
        """
