#
# export_stats.py <Peter.Bienstman@gmail.com>
#

HOUR = 60 * 60 # Seconds in an hour.
DAY = 24 * HOUR # Seconds in a day.

from mnemosyne.script import Mnemosyne
from openSM2sync.log_entry import EventTypes

# 'data_dir = None' will use the default sysem location, edit as appropriate.
data_dir = None
mnemosyne = Mnemosyne(data_dir)

for n in range(-10, 0):
    start_of_day = mnemosyne.database().start_of_day_n_days_ago(abs(n))
    print((n, mnemosyne.database().con.execute(\
            """select avg(grade) from log where ?<=timestamp and timestamp<?
            and event_type=? and scheduled_interval!=0""",
            (start_of_day, start_of_day + DAY, EventTypes.REPETITION)).\
            fetchone()[0]))

mnemosyne.finalise()
