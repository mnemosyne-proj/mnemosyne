#
# cramming_plugin.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import D_
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.schedulers.cramming import Cramming
from mnemosyne.libmnemosyne.review_controllers.SM2_controller_cramming \
     import SM2ControllerCramming


class CrammingPlugin(Plugin):

    name = D_("Cramming scheduler")
    description = \
  D_("Goes through cards in random order without saving scheduling information.")
    components = [Cramming, SM2ControllerCramming]    
