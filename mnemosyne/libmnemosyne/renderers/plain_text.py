#
# plain_text.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.renderer import Renderer


class PlainText(Renderer):

    used_for = None  # All card types.



    def render(self, fact_data, fact_keys, card_type, **render_args):
        text = ""
        for fact_key in fact_keys:
            if fact_key in fact_data and fact_data[fact_key]:
                text += fact_data[fact_key] + "\n"
        return text[:-1]


