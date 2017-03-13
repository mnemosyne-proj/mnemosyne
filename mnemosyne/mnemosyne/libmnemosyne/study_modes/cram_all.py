#
# cram_all.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.study_mode import StudyMode


class CramAll(StudyMode):
    
    id = 3
    name = _("Cram all cards")

    def activate(self):     
        from mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne \
             import SM2Mnemosyne
        from mnemosyne.libmnemosyne.review_controllers.SM2_controller \
            import SM2Controller
        scheduler = SM2Mnemosyne(self.component_manager)
        review_controller = SM2Controller(self.component_manager)
        self.component_manager.register(scheduler)
        self.component_manager.register(review_controller)
        scheduler.activate()
        review_controller.activate()