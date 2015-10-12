#
# mplayer_video.py <Peter.Bienstman@UGent.be>
#

import os
import re

from mnemosyne.libmnemosyne.utils import copy
from mnemosyne.libmnemosyne.filter import Filter

re_video = re.compile(r"""<video src=\"(.+?)\"(.*?)>""",
    re.DOTALL | re.IGNORECASE)
re_start = re.compile(r"""start=\"(.+?)\"""",
    re.DOTALL | re.IGNORECASE)
re_stop = re.compile(r"""stop=\"(.+?)\"""",
    re.DOTALL | re.IGNORECASE)


class MplayerVideo(Filter):

    """Play video externally in mplayer."""

    def run(self, text, card, fact_key, **render_args):
        if "no_side_effects" in render_args and \
            render_args["no_side_effects"] == True:
            return text
        if not re_video.search(text):
            return text
        index = 0
        for match in re_video.finditer(text):
            video_file = match.group(1)
            start, stop = 0, 999999
            if match.group(2):
                start_match = re_start.search(match.group(2))
                if start_match:
                    start = float(start_match.group(1))
                stop_match = re_stop.search(match.group(2))
                if stop_match:
                    stop = float(stop_match.group(1))
            text = text.replace(match.group(0), "")
            self.review_widget().play_media(video_file, start, stop)        
        return text
