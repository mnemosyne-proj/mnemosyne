#
# cram_all.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
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
    