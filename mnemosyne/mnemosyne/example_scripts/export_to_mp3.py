#
# export_to_mp3.py <Peter.Bienstman>
#

# Script to export the audio of today's revisions to an mp3 file for hands-off
# review. Only works for mp3 files.

# Adapt it your own need. It uses linux external tools, so it needs to be
# modified to run under Windows.

import re
import os
import time
import shutil
import subprocess

HOUR = 60 * 60 # Seconds in an hour.
DAY = 24 * HOUR # Seconds in a day.

silence = os.path.abspath("silence.mp3")
SILENCE_FACTOR = 1.2 # Silence will be 120% of audio length.

from mnemosyne.script import Mnemosyne

# 'data_dir = None' will use the default sysem location, edit as appropriate.
data_dir = None
mnemosyne = Mnemosyne(data_dir)

# Use mplayer to determine the lenght of an mp3 file.
re_length = re.compile(r"""ID_LENGTH=([0-9]*\.[0-9])""",
    re.DOTALL | re.IGNORECASE)
def determine_length(filename):
    out = subprocess.check_output(["mplayer", "-really-quiet","-vo", "null",
        "-ao", "null", "-frames", "0", "-identify", filename])
    return float(re_length.search(out).group(1))

# Collect all the facts which are either still due or reviewed today.
facts = set()
for cursor in mnemosyne.database().con.execute("""select _id from cards where
    active=1 and grade!=-1 and (?>=next_rep or ?<=last_rep)""",
    (mnemosyne.scheduler().adjusted_now(), time.time() - DAY)):
    card = mnemosyne.database().card(cursor[0], is_id_internal=True)
    facts.add(card.fact)

# For each fact, collect all the mp3 files and add silence near the end.
re_sound = re.compile(r"""audio src=['\"](.+?)['\"]""",
    re.DOTALL | re.IGNORECASE)
subprocess.call(["mp3wrap", "mnemosyne.mp3", silence, silence])
for fact in facts:
    length = 0
    filenames = []
    for match in re_sound.finditer("".join(list(fact.data.values()))):
        filename = os.path.join(\
            mnemosyne.database().media_dir(), match.group(1))
        print((filename, determine_length(filename)))
        length += determine_length(filename)
        filenames.append(filename)
    for i in range(int(length * SILENCE_FACTOR)):
        filenames.append(silence)
    subprocess.call(["mp3wrap", "-a", "mnemosyne_MP3WRAP.mp3"] + filenames)
shutil.move("mnemosyne_MP3WRAP.mp3", "mnemosyne.mp3")
