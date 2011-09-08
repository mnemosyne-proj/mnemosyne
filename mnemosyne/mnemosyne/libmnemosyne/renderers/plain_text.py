#
# plain_text.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.renderer import Renderer


class PlainText(Renderer):

    used_for = None  # All card types.

    def render_fields(self, data, keys, card_type, **render_args):
        text = ""
        for key in keys:
            if key in data and data[key]:
                text += data[key] + "\n"
        return text[:-1]

    
