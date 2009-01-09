#
# html_css.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.renderer import Renderer
from mnemosyne.libmnemosyne.component_manager import filters

# TODO: read card type css from $basedir/css/$card_type if it exits.
# TODO: add convenience functions to modify the css on disk:
#   set_background(card_type, color), set_font(card_type, fact_key, font),
#   set_alignment(card_type, fact_key, alignment), ...

# Based on info from http://apptools.com/examples/tableheight.php

class HtmlCss(Renderer):
    
    def __init__(self):
        self._css = {} # {card_type: css}
        
    def css(self, card_type):
        if card_type in self._css:
            return self._css[card_type]
        else:
            self._css[card_type] = """
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
                self._css[card_type] += "div#"+ field[0] + \
                        " {text-align: center;}\n"
            self._css[card_type] += "</style>"
            return self._css[card_type]
            
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
