#
# plain_text.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.renderer import Renderer


class PlainText(Renderer):

    used_for = None  # All card types.

    def render_fields(self, data, fields, card_type, **render_args):
        text = ""
        for field in fields:
            if field in data and data[field]:
                text += data[field] + "\n"
        return text[:-1]

    
