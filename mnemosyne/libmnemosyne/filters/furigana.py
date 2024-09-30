#
# furigana.py <Peter.Bienstman@gmail.com>
#

import re

from mnemosyne.libmnemosyne.filter import Filter

class Furigana(Filter):

    ruby_re = r"([\u4E00-\u9FFF]+)\[([\u3040-\u309F]+)\]"

    def run(self, text, card, fact_key, **render_args):
        return re.sub(self.ruby_re, r"<ruby>\1<rt>\2</rt></ruby>", text)
