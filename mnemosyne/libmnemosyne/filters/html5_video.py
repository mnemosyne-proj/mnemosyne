#
# html5_video.py <Peter.Bienstman@gmail.com>
#

import re

from mnemosyne.libmnemosyne.filter import Filter

re_video = re.compile(r"""<video( src=\".+?\")>""", re.DOTALL | re.IGNORECASE)


class Html5Video(Filter):

    """Add autoplay and control tags to html5 video tags."""

    def run(self, text, card, fact_key, **render_args):
        options = ""
        if self.config()["media_autoplay"]:
            options += " autoplay=1"
        if self.config()["media_controls"]:
            options += " controls=1"
        return re.sub(re_video, r"<video\1" + options + ">", text)


