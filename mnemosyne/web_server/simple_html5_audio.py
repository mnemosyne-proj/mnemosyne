#
# simple_html5_audio.py <Peter.Bienstman@gmail.com>
#

import re
import urllib.request, urllib.parse, urllib.error

from mnemosyne.libmnemosyne.filter import Filter

player_id = 1

re_audio = re.compile(r"""<audio src=\"(.+?)\"(.*?)>""",
    re.DOTALL | re.IGNORECASE)


class SimpleHtml5Audio(Filter):
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
            text += "<source src=\"" + filename + "\">" + '\n'
        global player_id
        str1 = '\n<audio id="player_{id}" autoplay controls>\n<source src='.format(id = player_id)
        text = text.replace('<source src=', str1, 1)
        text += '</audio>\n'
        player_id += 1
        return text
