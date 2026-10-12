#
# scheduled_forgotten_new_SM2.py
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.study_modes.scheduled_forgotten_new import \
     ScheduledForgottenNew
from mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne import SM2Mnemosyne


class ScheduledForgottenNewSM2(ScheduledForgottenNew):

    """The original SM-2 based study mode, kept available as an option.
    The default study mode now uses the FixedIntervals scheduler.

    """

    id = "ScheduledForgottenNewSM2"
    name = _("Scheduled -> forgotten -> new (classic SM-2)")
    menu_weight = 5
    Scheduler = SM2Mnemosyne
