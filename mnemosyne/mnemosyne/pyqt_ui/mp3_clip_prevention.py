#
# mp3_clip_prevention.py <Peter.Bienstman@UGent.be>
#

import re
import os
import time

from PyQt4 import QtCore 
from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.utils import rand_uuid

re_mp3 = re.compile(r"""<audio src=\"(.+?.mp3)\"""", re.DOTALL | re.IGNORECASE)


class Mp3ClipPrevention(Filter):

    """Work around library bug which clips last part of mp3. We do this by
    manually adding silence.

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
        # Create files with added silence.
        for match in re_mp3.finditer(text):
            mp3 = file(match.group(1).replace("file:\\\\\\", ""), "rb")
            filename_with_silence = \
                os.path.join(tmp_dir_name, rand_uuid() + ".mp3")
            mp3_with_silence = file(filename_with_silence, "wb")
            mp3_with_silence.write(mp3.read())
            silence = QtCore.QFile(":/mnemosyne/pixmaps/silence.mp3")
            silence.open(QtCore.QIODevice.ReadOnly)
            mp3_with_silence.write(silence.readAll())
            text = text.replace(match.group(1),
               "file:\\\\\\" + filename_with_silence)
        return text

    

