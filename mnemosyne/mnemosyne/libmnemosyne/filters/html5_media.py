#
# html5_media.py <Peter.Bienstman@UGent.be>
#

import re

from mnemosyne.libmnemosyne.filter import Filter

re_media = re.compile(r"""<(audio|video)( src=\".+?\")>""", re.DOTALL | re.IGNORECASE)


class Html5Media(Filter):

    """Add autoplay and control tags to html5 media tags."""

    def run(self, text):
        options = ""
        if self.config()["media_autoplay"]:
            options += " autoplay=1"
        if self.config()["media_controls"]:
            options += " controls=1"
        return re.sub(re_media, r"<\1\2" + options + ">", text)
    

