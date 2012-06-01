#
# mplayer_audio.py <Peter.Bienstman@UGent.be>
#

import os
import re
import shutil
import subprocess

from mnemosyne.libmnemosyne.filter import Filter

re_audio = re.compile(r"""<audio src=\"(.+?)\">""", re.DOTALL | re.IGNORECASE)

# Don't show batch window.
info = subprocess.STARTUPINFO()
info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
info.wShowWindow = subprocess.SW_HIDE


class MplayerAudio(Filter):

    """Play sound externally in mplayer under Windows."""

    def run(self, text, card, fact_key, **render_args):
        if "no_side_effects" in render_args and \
            render_args["no_side_effects"] == True:
            return text
        if not re_audio.search(text):
            return text
        sound_files = []
        index = 0
        for match in re_audio.finditer(text):
            sound_file = match.group(1)
            # Workaround for lack of unicode support in Popen/mplayer.
            try:
                sound_file.decode("ascii")
            except UnicodeEncodeError:
                new_name = unicode(os.path.join(self.database().media_dir(),
                    "___" + str(index) + "___.mp3"))
                shutil.copy(sound_file.replace("file:///", ""), new_name)
                index += 1
                sound_file = new_name
            sound_files.append(sound_file)
            text = text.replace(match.group(0), "")
        subprocess.Popen(["mplayer.exe", "-ao", "win32"] + sound_files,
            startupinfo=info)
        return text
