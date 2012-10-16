#
# cramming_plugin.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.schedulers.cramming import Cramming
from mnemosyne.libmnemosyne.review_controllers.SM2_controller_cramming \
     import SM2ControllerCramming


class CrammingPlugin(Plugin):

    name = _("Cramming scheduler")
    description = \
  _("""Goes through the active cards in random order without saving scheduling information.\n
Once this plugin is active, you can configure the cramming scheduler through 'Configure Mnemosyne'.\n
To return to the original scheduler, just deactivate this plugin.""")
    components = [Cramming, SM2ControllerCramming]
