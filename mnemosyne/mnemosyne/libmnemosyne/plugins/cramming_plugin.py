#
# cramming_plugin.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.schedulers.cramming import Cramming
from mnemosyne.libmnemosyne.ui_controllers_review.SM2_controller_cramming \
     import SM2ControllerCramming


class CrammingPlugin(Plugin):

    name = _("Cramming scheduler")
    description = \
  _("Goes through cards in random order without saving scheduling information.")
    components = [Cramming, SM2ControllerCramming]    
