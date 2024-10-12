#
# cram_all.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.study_mode import StudyMode
from mnemosyne.libmnemosyne.schedulers.cramming import Cramming
from mnemosyne.libmnemosyne.review_controllers.SM2_controller_cramming \
     import SM2ControllerCramming


class CramAll(StudyMode):

    id = "CramAll"
    name = _("Cram all cards")
    menu_weight = 3
    Scheduler = Cramming
    ReviewController = SM2ControllerCramming

    def activate(self):
        self.activate_components()
        self.review_controller().reset(new_only=False)