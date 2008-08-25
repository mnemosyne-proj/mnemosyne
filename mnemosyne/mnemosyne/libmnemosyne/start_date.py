#
# start_date.py <Peter.Bienstman@UGent.be>
#

import datetime
from mnemosyne.libmnemosyne.component_manager import config


class StartDate:

    """Class to hold the date and time when the database was created, and to
    calculate how many days have passed since then.

    """

    def __init__(self, start=None):
        self.init(start)

    def init(self, start=None):
        if not start:
            self.start = datetime.datetime.now()
        else:
            self.start = start

    def days_since_start(self):

        """Note that this should be cached as much as possible for
        efficiency reasons.

        """

        h = config()["day_starts_at"]
        adjusted_start = self.start.replace(hour=h, minute=0, second=0)
        dt = datetime.datetime.now() - adjusted_start
        return dt.days

