#
# cram_recent.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.study_mode import StudyMode
from mnemosyne.libmnemosyne.schedulers.cramming import Cramming
from mnemosyne.libmnemosyne.review_controllers.SM2_controller_cramming \
     import SM2ControllerCramming


class CramRecent(StudyMode):

    id = "CramRecent"
    name = _("Cram recently learned new cards")
    menu_weight = 4
    Scheduler = Cramming
    ReviewController = SM2ControllerCramming

    def activate(self):
        self.activate_components()
        self.review_controller().reset(new_only=True)