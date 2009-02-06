#
# html_css.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.renderer import Renderer
from mnemosyne.libmnemosyne.component_manager import config, filters

# Css table wizardry based on info from
# http://apptools.com/examples/tableheight.php


class HtmlCss(Renderer):
    
    def __init__(self):
        self._css = {} # {card_type.id: css}

    def update(self, card_type):
        self._css[card_type.id] = """<style type="text/css">
        table { height: 100%; """
        # Set aligment of the table (but not the contents within the table).
        try:
            alignment = config()["alignment"][card_type.id]
        except:
            alignment = "center"
        if alignment == "left":
            self._css[card_type.id] += "margin-left: 0; margin-right: auto; "
        elif alignment == "right":
            self._css[card_type.id] += "margin-left: auto; margin-right: 0; "
        else:
            self._css[card_type.id] += "margin-left: auto; margin-right: auto; "                
        self._css[card_type.id] += " }\n"
        # Background colours.
        self._css[card_type.id] += "body { "
        try:
            colour = config()["background_colour"][card_type.id]
            colour_string = ("%X" % colour)[2:] # Strip alpha.
            self._css[card_type.id] += "background-color: #%s;" % colour_string
        except:
            pass
        self._css[card_type.id] += """margin: 0;
        padding: 0;
        border: thin solid #8F8F8F; }\n"""
        for key in card_type.keys():
            self._css[card_type.id] += "div#%s { " % key
            # Set alignment within table cell.
            try:
                alignment = config()["alignment"][card_type.id]
                self._css[card_type.id] += "text-align: %s; " % alignment               
            except:
                pass
            # Text colours.
            try:
                colour = config()["font_colour"][card_type.id][key]
                colour_string = ("%X" % colour)[2:] # Strip alpha.
                self._css[card_type.id] += "color: #%s;" % colour_string
            except:
                pass
            # Text font.
            try:
                font_string = config()["font"][card_type.id][key]
                family,size,x,x,w,i,u,s,x,x = font_string.split(",")
                self._css[card_type.id] += "font-family: %s; " % family
                self._css[card_type.id] += "font-size: %s; " % size
                if w == "25":
                    self._css[card_type.id] += "font-weight: light; "
                if w == "75":
                    self._css[card_type.id] += "font-weight: bold; "                    
                if i == "1":
                    self._css[card_type.id] += "font-style: italic; "
                if i == "2":
                    self._css[card_type.id] += "font-style: oblique; "
                if u == "1":
                    self._css[card_type.id] += "text-decoration: underline; "
                if s == "1":
                    self._css[card_type.id] += "text-decoration: line-through; "
            except:
                pass                
            self._css[card_type.id] += "}\n"
        self._css[card_type.id] += "</style>"
        
    def css(self, card_type):
        if not card_type.id in self._css:
            self.update(card_type)
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
