#
# simple_html5_audio.py <Peter.Bienstman@UGent.be>
#

import re
import urllib.request, urllib.parse, urllib.error

from mnemosyne.libmnemosyne.filter import Filter


class PlayerIdContainer:
    def __init__(self):         
        self.id = 1


apc = PlayerIdContainer()


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
        counter = 0
        for match in re_audio.finditer(text):
            filename = urllib.parse.quote(match.group(1).encode("utf-8"), safe="/:")
            filename = urllib.parse.quote(match.group(1), safe="/:")
            # Prevent wsgi from decoding this as as non-unicode behind
            # our back ( https://bugs.python.org/issue16679).
            filename = filename.replace("%", "___-___")
            text = text.replace(match.group(0), "")
            text += "<source src=\"" + filename + "\">" + '\n'
            counter += 1
        if 1 < counter:
            str1 = '<audio id="player_{id}" autoplay controls>\n<source src='.format(id = apc.id)
            text = text.replace('<source src=', str1, 1)
            apc.id += 1
        elif 1 == counter:
            str1 = '<audio autoplay controls><source src='
            text = text.replace('<source src=', str1, 1)
        text += '</audio>'
        return text
