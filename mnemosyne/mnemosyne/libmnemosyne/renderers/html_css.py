#
# html_css.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.renderer import Renderer
from mnemosyne.libmnemosyne.component_manager import filters

# Css table wizardry Based on info from
# http://apptools.com/examples/tableheight.php

class HtmlCss(Renderer):
    
    def __init__(self):
        self._css = {} # {card_type.id: css}
        
    def css(self, card_type):
        if card_type.id in self._css:
            return self._css[card_type.id]
        else:
            self._css[card_type.id] = """
            <style type="text/css">
            table { margin-left: auto;
                margin-right: auto; /* Centers table, but not its contents. */
                height: 100%; }
            body { color: black;
                background-color: white;
                margin: 0;
                padding: 0;
                border: thin solid #8F8F8F; }\n"""
            for field in card_type.fields: # Center content in table.
                self._css[card_type.id] += "div#"+ field[0] + \
                        " {text-align: center;}\n"
            self._css[card_type.id] += "</style>"
            return self._css[card_type.id]
            
    def render_card_fields(self, fact, fields):
        html = "<html><head>" + self.css(fact.card_type) + \
            "</head><body><table><tr><td>"
        for field in fields:
            key = field[0]
            s = fact[key]
            for f in filters():
                s = f.run(s, fact)
            html += "<div id=\"%s\">%s</div>" % (key, s)
        html += "</td></tr></table></body></html>"
        return html
