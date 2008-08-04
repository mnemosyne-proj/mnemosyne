##############################################################################
#
# three_sided.py <Peter.Bienstman@UGent.be>
#
##############################################################################

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView



##############################################################################
#
# ThreeSided
#
##############################################################################

class ThreeSided(CardType):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self):

        self.name = _("Foreign word with pronunciation"),
        self.id   = 3

        # Name the keys.

        self.fact_key_names['f'] = _("Foreign word")
        self.fact_key_names['p'] = _("Pronunciation")
        self.fact_key_names['t'] = _("Translation")        
        
        # Recognition.

        v = FactView(_("Recognition"))

        v.q_fields.append(("f", True))

        v.a_fields.append(("p", False))         
        v.a_fields.append(("t", False))       

        self.fact_views.append(v)
     
        # Back to front.

        v = FactView(_("Production"))

        v.q_fields.append(("t", True))

        v.a_fields.append(("f", False))        
        v.a_fields.append(("p", False))

        self.fact_views.append(v)     
