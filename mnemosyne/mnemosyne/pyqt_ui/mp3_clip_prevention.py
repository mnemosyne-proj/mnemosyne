#
# mp3_clip_prevention.py <Peter.Bienstman@UGent.be>
#

import re
import os

from PyQt4 import QtCore 
from mnemosyne.libmnemosyne.filter import Filter

re_mp3 = re.compile(r"""<audio src=\"(.+?.mp3)\"""", re.DOTALL | re.IGNORECASE)


class Mp3ClipPrevention(Filter):

    """Work around library bug which clips last part of mp3 by adding silence.
    Works only for a single mp3 file per card.

    """

    def run(self, text, card, fact_key):
        match = re_mp3.search(text)
        if not match:
            return unicode(text)
        mp3 = file(match.group(1).replace("file:\\\\\\", ""), "rb")
        filename_with_silence = \
            os.path.join(self.database().media_dir(), "___.mp3")
        # When we try to play the sound file a second time, e.g. after opening
        # the configuration dialog, we get 'permission denied' errors.
        # As a hack, we just carry on in this case, and assume the file with
        # extra silence is the same that was already created.
        try:
            mp3_with_silence = file(filename_with_silence, "wb")
            mp3_with_silence.write(mp3.read())
            silence = QtCore.QFile(":/mnemosyne/pixmaps/silence.mp3")
            silence.open(QtCore.QIODevice.ReadOnly)
            mp3_with_silence.write(silence.readAll())
        except IOError:
            pass
        return text.replace(match.group(1),
           "file:\\\\\\" + filename_with_silence)

