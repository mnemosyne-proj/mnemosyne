#
# simple_html5_audio.py <Peter.Bienstman@UGent.be>
#

import re
import urllib

from mnemosyne.libmnemosyne.filter import Filter

re_audio = re.compile(r"""<audio src=\"(.+?)\"(.*?)>""",
    re.DOTALL | re.IGNORECASE)


class SimpleHtml5Audio(Filter):

    """Most simple html5 audio player to ensure maximum compatibility across
    a wide range of browsers and mobile devices.

    Issues:

     - no autoplay to prevent synchronisation bugs.
     - whether the sound can be repeated depends on how well html5 support is
       implement in the browser.
     - not very well suited for multiple audio files.
     - no support for start and stop tags.

    """

    def run(self, text, card, fact_key, **render_args):
        if not re_audio.search(text):
            return text
        for match in re_audio.finditer(text):
            filename = urllib.quote(match.group(1).encode("utf-8"), safe="/:")
            text = text.replace(match.group(0), "")
            text += "<audio src=\"" + filename + "\" controls>"
        return text
