#
# simple_html5_audio.py <Peter.Bienstman@UGent.be>
#

import re
import urllib.request, urllib.parse, urllib.error

from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.web_server.multiple_audiofile_support import InsertAudioplayerTags

re_audio = re.compile(r"""<audio src=\"(.+?)\"(.*?)>""",
    re.DOTALL | re.IGNORECASE)


class SimpleHtml5Audio(Filter):

    """Most simple html5 audio player to ensure maximum compatibility across
    a wide range of browsers and mobile devices.

    Issues:

     - no autoplay to prevent synchronisation bugs.
     - not very well suited for multiple audio files.
     - no support for start and stop tags.

    """

    def run(self, text, card, fact_key, **render_args):
        if not re_audio.search(text):
            return text
        for match in re_audio.finditer(text):
            filename = urllib.parse.quote(match.group(1).encode("utf-8"), safe="/:")
            filename = urllib.parse.quote(match.group(1), safe="/:")
            # Prevent wsgi from decoding this as as non-unicode behind
            # our back ( https://bugs.python.org/issue16679).
            filename = filename.replace("%", "___-___")
            text = text.replace(match.group(0), "")
            text += "<source src=\"" + filename + "\">" #test OK
        inserter = InsertAudioplayerTags()
        text = inserter.insert_audioplayer_tags(text, fact_key)
        return text
