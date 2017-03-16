#
# cram_all.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.study_mode import StudyMode
from mnemosyne.libmnemosyne.schedulers.cramming import Cramming
from mnemosyne.libmnemosyne.review_controllers.SM2_controller_cramming \
     import SM2ControllerCramming


class CramAll(StudyMode):
    
    id = 3
    name = _("Cram all cards")
    Scheduler = Cramming
    ReviewController = SM2ControllerCramming
    
    def activate(self):
        self.register_components()
        self.review_controller().reset()
        print(self.review_widget())
        self.review_widget().activate()