#
# new_only.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.study_mode import StudyMode
from mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne \
     import SM2Mnemosyne
from mnemosyne.libmnemosyne.review_controllers.SM2_controller \
     import SM2Controller


class NewOnly(StudyMode):

    id = "NewOnly"
    name = _("Study new unlearned cards only")
    menu_weight = 2
    Scheduler = SM2Mnemosyne
    ReviewController = SM2Controller

    def activate(self):
        self.activate_components()
        self.review_controller().reset(new_only=True)
