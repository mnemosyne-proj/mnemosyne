#
# plain_text.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.renderer import Renderer


class PlainText(Renderer):

    def render_fields(self, field_data, fields, card_type,
                      render_chain, **render_args):
        text = ""
        for field in fields:
            s = field_data[field]
            for f in self.filters(render_chain):
                s = f.run(s, **render_args)
            text += s + "\n"
        return text

    
