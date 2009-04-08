#
# plain_text.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.renderer import Renderer
from mnemosyne.libmnemosyne.component_manager import filters

class PlainText(Renderer):
            
    def render_card_fields(self, fact, fields):
        text = ""
        for field in fields:
            key = field[0]
            s = fact[key]
            for f in filters():
                s = f.run(s, fact)
            text += s + "\n"
        return text
    
    def render_text(self, text, field_name, card_type):
        return text
    
