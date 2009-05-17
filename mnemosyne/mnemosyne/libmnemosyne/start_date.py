#
# start_date.py <Peter.Bienstman@UGent.be>
#

import datetime


class StartDate:

    """Class to hold the date and time when the database was created, and to
    calculate how many days have passed since then.

    Dates in Mnemosyne are stored as days since the creation of the database.
    This is a floating point number, to accomodate schedulers doing minute-
    level scheduling.

    The rejected alternatives to store dates are:

    Storing dates as ISO timestamp (the default in SQL) makes it slow to sort
    on interval (difference between two dates) and also consumes a lot more
    space.

    A Unix timestamp is measured in seconds, whereas Mnemosyne's natural unit
    is days.

    Using days since the start of the Unix epoch results in bigger numbers
    (although this is less relevant if the date is stored as a float).

    Using Python datetime objects throughout the code would result in more
    verbose code and more conversions.

    """

    def __init__(self, start=None):
        self.init(start)

    def init(self, start=None):
        if not start:
            self.start = datetime.datetime.now()
        else:
            self.start = start

    def days_since_start(self, day_starts_at):

        """Note that this should be cached as much as possible for
        efficiency reasons.

        """

        adjusted_start = self.start.replace(hour=day_starts_at,
                                            minute=0, second=0)
        dt = datetime.datetime.now() - adjusted_start
        return dt.days

