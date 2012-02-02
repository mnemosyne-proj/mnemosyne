#
# mp3_handler.py <Peter.Bienstman@UGent.be>
#

import re
import os
import time

from PyQt4 import QtCore
from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.utils import rand_uuid

re_mp3 = re.compile(r"""<audio src=\"(.+?.mp3)\".*?>""",
    re.DOTALL | re.IGNORECASE)


class Mp3Handler(Filter):

    """Work around two library issues:

      * last part of of short mp3 is clipped. We do this by manually adding
        silence.
      * when several mp3 files are present in a card, they all start playing
        at once, so we first combine them in a single file.

    """

    def run(self, text, card, fact_key):
        match = re_mp3.search(text)
        if not match:
            return unicode(text)
        # We need to create a unique temporary filename each time we run,
        # otherwise we can get 'permission denied errors' on Windows if the
        # sound system hangs on to the file after it has been played.
        tmp_dir_name = os.path.join(self.database().media_dir(), "___TMP___")
        if not os.path.exists(tmp_dir_name):
            os.mkdir(tmp_dir_name)
        # Try to clean out old files that are no longer open.
        for filename in os.listdir(tmp_dir_name):
            try:
                os.remove(os.path.join(tmp_dir_name, filename))
            except:
                pass
        # Determine the new audio tag, keeping all its options.
        new_mp3_filename = os.path.join(tmp_dir_name, rand_uuid() + ".mp3")
        match = re_mp3.search(text)
        audio_tag = match.group(0).replace(match.group(1),
               "file:\\\\\\" + new_mp3_filename)
        # Join mp3 files.
        new_mp3 = file(new_mp3_filename, "wb")
        for match in re_mp3.finditer(text):
            mp3 = file(match.group(1).replace("file:\\\\\\", ""), "rb")
            new_mp3.write(mp3.read())
            text = text.replace(match.group(0), "")
        # Add silence.
        silence = QtCore.QFile(":/mnemosyne/pixmaps/silence.mp3")
        silence.open(QtCore.QIODevice.ReadOnly)
        new_mp3.write(silence.readAll())
        text = text + audio_tag
        return text


