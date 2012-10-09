#
# mplayer_video.py <Peter.Bienstman@UGent.be>
#

import os
import re
import shutil
import subprocess

from mnemosyne.libmnemosyne.filter import Filter

re_video = re.compile(r"""<video src=\"(.+?)\"(.*?)>""",
    re.DOTALL | re.IGNORECASE)
re_start = re.compile(r"""start=\"(.+?)\"""",
    re.DOTALL | re.IGNORECASE)
re_stop = re.compile(r"""stop=\"(.+?)\"""",
    re.DOTALL | re.IGNORECASE)

# Don't show batch window.
info = subprocess.STARTUPINFO()
info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
info.wShowWindow = subprocess.SW_HIDE


class MplayerVideo(Filter):

    """Play video externally in mplayer under Windows."""

    def run(self, text, card, fact_key, **render_args):
        if "no_side_effects" in render_args and \
            render_args["no_side_effects"] == True:
            return text
        if not re_video.search(text):
            return text
        video_files = []
        index = 0
        for match in re_video.finditer(text):
            video_file = match.group(1)
            # Workaround for lack of unicode support in Popen/mplayer.
            try:
                video_file.decode("ascii")
            except UnicodeEncodeError:
                new_name = unicode(os.path.join(self.database().media_dir(),
                    "___" + str(index) + "___.mp4"))
                shutil.copy(video_file.replace("file:///", ""), new_name)
                index += 1
                video_file = new_name
            video_files.append(video_file)
            start, stop = 0, 999999
            if match.group(2):
                start_match = re_start.search(match.group(2))
                if start_match:
                    start = float(start_match.group(1))
                stop_match = re_stop.search(match.group(2))
                if stop_match:
                    stop = float(stop_match.group(1))
            text = text.replace(match.group(0), "")
        duration = stop - start
        if duration > 400:
            duration -= 300 # Compensate for mplayer overshoot.
        subprocess.Popen(["mplayer.exe", "-ao", "win32"] + video_files + \
            ["-ss", str(start), "-endpos", str(duration)],
            startupinfo=info)
        return text
