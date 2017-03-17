#
# scheduled_forgotten_new.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.study_mode import StudyMode
from mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne \
     import SM2Mnemosyne
from mnemosyne.libmnemosyne.review_controllers.SM2_controller \
     import SM2Controller


class ScheduledForgottenNew(StudyMode):
    
    id = 1
    name = _("Scheduled -> forgotten -> new")
    Scheduler = SM2Mnemosyne
    ReviewController = SM2Controller

    def activate(self):
        self.activate_components()
        self.review_controller().reset(new_only=False)