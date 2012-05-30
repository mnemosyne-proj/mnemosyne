#
# mplayer_audio.py <Peter.Bienstman@UGent.be>
#

import os
import re
import sys
import codecs
import locale
import subprocess

from mnemosyne.libmnemosyne.filter import Filter

re_audio = re.compile(r"""<audio src=\"(.+?)\">""", re.DOTALL | re.IGNORECASE)

# Encoding.

encoding = sys.stdin.encoding #None
#try:
#    preferredencoding = locale.getpreferredencoding()
#    codecs.lookup(preferredencoding)
#    encoding = preferredencoding.lower()
#except LookupError:
#    pass

# Don't show batch window.

info = subprocess.STARTUPINFO()
info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
info.wShowWindow = subprocess.SW_HIDE


class MplayerAudio(Filter):

    """Play sound externally in mplayer under Windows."""

    def run(self, text, card, fact_key, **render_args):
        if not re_audio.search(text):
            return text
        sound_files = []
        for match in re_audio.finditer(text):
            sound_file = match.group(1)
            if encoding:
                sound_file.encode(encoding)
            sound_files.append(sound_file)
            text = text.replace(match.group(0), "")
        subprocess.Popen(["mplayer.exe", "-ao", "win32"] + sound_files,
            startupinfo=info)
        return text
