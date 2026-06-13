# Mnemosyne configuration file.

# This file contains settings which we deem to be too specialised to be
# accesible from the GUI. However, if you use some of these settings, feel
# free to inform the developers so that it can be re-evaluated if these
# settings need to be exposed in the GUI.

# Science server. Only change when prompted by the developers.
science_server = "mnemosyne-proj.dyndns.org:80"

# Set to True to prevent you from accidentally revealing the answer when
# clicking the edit button.
only_editable_when_answer_shown = False

# Set to False if you don't want the tag names to be shown in the review
# window.
show_tags_during_review = True

# The number of daily backups to keep. Set to -1 for no limit.
max_backups = 10

# Start the card browser with the last used colum sort. Could have a
# performance penalty for large databases.
start_card_browser_sorted = True

# The moment the new day starts. Defaults to 3 am. Could be useful to change
# if you are a night bird. You can only set the hours, not minutes, and
# midnight corresponds to 0.
day_starts_at = 3

# On mobile clients with slow SD cards copying a large database for the backup
# before sync can take longer than the sync itself, so we offer reckless users
# the possibility to skip this.
backup_before_sync = True

# Latex preamble. Note that for the pre- and postamble you need to use double
# slashes instead of single slashes here, to have them escaped when Python
# reads them in.
latex_preamble = r"""
\documentclass[12pt]{article}
\pagestyle{empty}
\begin{document}"""

# Latex postamble.
latex_postamble = r"""\end{document}"""

# Latex command.
latex = "latex -interaction=nonstopmode"

# Latex dvipng command.
dvipng = "dvipng -D 200 -T tight tmp.dvi"

# Put an upper limit on the scheduled interval. Does not work retroactively, only for new reviews.
# Should be set on each device, including mobile clients. Be careful with this setting: if you
# accidentally set it e.g. to 1 day, you will mess up your schedule completely.
max_scheduled_interval_days = None

