#
# plain_text.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.renderer import Renderer


class PlainText(Renderer):
            
    def render_card_fields(self, fact, fields, exporting):
        text = ""
        for field in fields:
            key = field[0]
            s = fact[key]
            for f in self.filters():
                s = f.run(s, fact)
            text += s + "\n"
        return text
    
    def render_text(self, text, field_name, card_type, exporting):
        return text
    
