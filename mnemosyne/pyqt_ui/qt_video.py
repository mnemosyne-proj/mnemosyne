#
# qt_video.py <Peter.Bienstman@gmail.com>
#

import re

from mnemosyne.libmnemosyne.filter import Filter

re_video = re.compile(r"""<video src=\"(.+?)\"(.*?)>""",
    re.DOTALL | re.IGNORECASE)
re_start = re.compile(r"""start=\"(.+?)\"""",
    re.DOTALL | re.IGNORECASE)
re_stop = re.compile(r"""stop=\"(.+?)\"""",
    re.DOTALL | re.IGNORECASE)


class QtVideo(Filter):

    def run(self, text, card, fact_key, **render_args):
        if "no_side_effects" in render_args and \
            render_args["no_side_effects"] == True:
            return text
        if not re_video.search(text):
            return text
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
