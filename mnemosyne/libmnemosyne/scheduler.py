#
# scheduler.py <Peter.Bienstman@gmail.com>
#

import calendar
import datetime
import time

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.gui_translator import _


HOUR = 60 * 60  # Seconds in an hour.
DAY = 24 * HOUR  # Seconds in a day.


class Scheduler(Component):

    name = ""
    component_type = "scheduler"

    def reset(self):

        """Called when starting the scheduler for the first time."""

        raise NotImplementedError

    def set_initial_grade(self, cards, grade):

        """Sets the initial grades for a set of sister cards, making sure
        their next repetitions do no fall on the same day.

        Called when cards are given their initial grade outside of the
        review process, e.g. when the user gives an initial grade when
        adding a new card in the GUI. Therefore, 'unseen' is still left to
        True, as this card has not yet been seen in the interactive review
        process.

        Cards which don't have initial grade information available (e.g. for
        cards created during import or conversion from different card type),
        get their initial grade when they are encountered in the interactive
        review process for the first time.

        In both cases, this initial grading is seen as the first repetition.

        In this way, both types of cards are treated in the same way. (There
        is an ineffectual asymmetry left in the log messages they generate,
        but all the relevant information can still be parsed from them.)

        """

        raise NotImplementedError

    def avoid_sister_cards(self, card):

        """Change card.next_rep to make sure that the card is not scheduled
        on the same day as a sister card.

        Factored out here to allow this to be used by e.g. MnemoGogo.

        """

        raise NotImplementedError

    def rebuild_queue(self, learn_ahead=False):

        """Called by the rest of the library when an existing queue risks
        becoming invalid, e.g. when cards have been deleted in the GUI.
        'next_card' also makes use of this in certain implementations.

        """

        raise NotImplementedError

    def is_in_queue(self, card):

        """To check whether the queue needs to be rebuilt, e.g. if it contains
        a card that was deleted in the GUI.

        """

        raise NotImplementedError

    def remove_from_queue_if_present(self, card):
        raise NotImplementedError

    def next_card(self, learn_ahead=False):
        raise NotImplementedError

    def is_prefetch_allowed(self):

        """Can we display a new card before having processed the grading of
        the previous one?

        """

        raise NotImplementedError

    def grade_answer(self, card, new_grade, dry_run=False):
        raise NotImplementedError

    def scheduled_count(self):
        raise NotImplementedError

    def non_memorised_count(self):
        raise NotImplementedError

    def active_count(self):
        raise NotImplementedError

    def card_count_scheduled_n_days_from_now(self, n):

        """Yesterday: n=-1, today: n=0, tomorrow: n=1, ... .

        Is not implemented in the database, because this could need internal
        scheduler information.
        """

        raise NotImplementedError

    def next_rep_to_interval_string(self, next_rep, now=None):

        """Converts next_rep to a string like 'tomorrow', 'in 2 weeks', ...

        """

        raise NotImplementedError

    def last_rep_to_interval_string(self, last_rep, now=None):

        """Converts last_rep to a string like 'yesterday', '2 weeks ago', ...

        """

        raise NotImplementedError

    def midnight_UTC(self, timestamp):

        """Round a timestamp to a value with resolution of a day, storing it
        in a timezone independent way, as a POSIX timestamp corresponding to
        midnight UTC on that date.

        E.g. if the scheduler sets 'next_rep' to 2012/1/1 12:14 local time,
        this function will return the timestamp corresponding to
        2012/1/1 00;00 UTC.

        Important: the timestamp needs to have the meaning of local time,
        not e.g. UTC, so calling midnight_UTC twice will give unexpected
        results.

        """

        # Create a time tuple containing the local date only, i.e. throwing
        # away hours, minutes, etc.
        # Android/Crystax 10.3.2 actually has a 2038 overflow problem...
        try:
            date_only = datetime.date.fromtimestamp(timestamp).timetuple()
        except OverflowError:
            date_only = datetime.date.fromtimestamp(2**31-2).timetuple()
        # Now we reinterpret this same time tuple as being UTC and convert it
        # to a POSIX timestamp. (Note that timetuples are 'naive', i.e. they
        # themselves do not contain timezone information.)
        return int(calendar.timegm(date_only))

    def adjusted_now(self, now=None):

        """Timezone information and 'day_starts_at' will only become relevant
        when the queue is built, not at schedule time, to allow for
        moving to a different timezone after a card has been scheduled.
        Cards are due when 'adjusted_now >= next_rep', and this function
        makes sure that happens at h:00 local time (with h being
        'day_starts_at').

        """
        
        if now == None:
            now = time.time()
        # The larger 'day_starts_at', the later the card should become due,
        # i.e. larger than 'next_card', so the more 'now' should be decreased.
        now -= self.config()["day_starts_at"] * HOUR
        # 'altzone' or 'timezone' contains the offset in seconds west of UTC.
        # This number is positive for the US, where a card should become
        # due later than in Europe, so 'now' should be decreased by this
        # offset.
        # As for when to use 'altzone' instead of 'timezone' if daylight
        # savings time is active, this is a matter of big confusion
        # among the Python developers themselves:
        # http://bugs.python.org/issue7229
        if time.localtime(now).tm_isdst and time.daylight:
            now -= time.altzone
        else:
            now -= time.timezone 
        return int(now)

    def next_rep_to_interval_string(self, next_rep, now=None):

        """Converts next_rep to a string like 'tomorrow', 'in 2 weeks', ...

        """

        if now is None:
            now = self.adjusted_now()
        interval_days = (next_rep - now) / DAY
        if interval_days >= 365:
            interval_years = interval_days/365.
            return _("in") + " " + "%.1f" % interval_years + " " + \
                   _("years")
        elif interval_days >= 62:
            interval_months = int(interval_days/31)
            return _("in") + " " + str(interval_months) + " " + \
                   _("months")
        elif interval_days >= 31:
            return _("in 1 month")
        elif interval_days >= 1:
            return _("in") + " " + str(int(interval_days) + 1) + " " + \
                   _("days")
        elif interval_days >= 0:
            return _("tomorrow")
        elif interval_days >= -1:
            return _("today")
        elif interval_days >= -2:
            return _("1 day overdue")
        elif interval_days >= -31:
            return str(int(-interval_days)) + " " + _("days overdue")
        elif interval_days >= -62:
            return _("1 month overdue")
        elif interval_days >= -365:
            interval_months = int(-interval_days/31)
            return str(interval_months) + " " + _("months overdue")
        else:
            interval_years = -interval_days/365.
            return "%.1f " % interval_years +  _("years overdue")

    def last_rep_to_interval_string(self, last_rep, now=None):

        """Converts next_rep to a string like 'yesterday', '2 weeks ago', ...

        """

        if now is None:
            now = time.time()
        # To perform the calculation, we need to 'snap' the two timestamps
        # to midnight UTC before calculating the interval.
        now = self.midnight_UTC(\
            now - self.config()["day_starts_at"] * HOUR)
        last_rep = self.midnight_UTC(\
            last_rep - self.config()["day_starts_at"] * HOUR)
        interval_days = (last_rep - now) / DAY
        if interval_days > -1:
            return _("today")
        elif interval_days > -2:
            return _("yesterday")
        elif interval_days > -31:
            return str(int(-interval_days)) + " " + _("days ago")
        elif interval_days > -62:
            return _("1 month ago")
        elif interval_days > -365:
            interval_months = int(-interval_days/31.)
            return str(interval_months) + " " + _("months ago")
        else:
            interval_years = -interval_days/365.
            return "%.1f " % interval_years +  _("years ago")
