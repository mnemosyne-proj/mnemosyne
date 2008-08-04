##############################################################################
#
# simple_card.py <Peter.Bienstman@UGent.be>
#
##############################################################################

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView



##############################################################################
#
# Simple
#
##############################################################################

class Simple(CardType):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self):

        self.name = _("Front-to-back only")
        self.id   = 1

        # Name the keys.

        self.fact_key_names['q'] = _("Question")
        self.fact_key_names['a'] = _("Answer")
        
        # Front to back.

        v = FactView(_("Front-to-back"))

        v.q_fields.append(("q", True))
        
        v.a_fields.append(("a", False))       

        self.fact_views.append(v)
 
