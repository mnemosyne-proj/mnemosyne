#
# html_css.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne.libmnemosyne.renderer import Renderer

# Css table wizardry based on info from
# http://apptools.com/examples/tableheight.php


class HtmlCss(Renderer):
    
    def __init__(self, component_manager):
        Renderer.__init__(self, component_manager)
        self._css = {} # {card_type.id: css}

    def update(self, card_type):
        # Load from external file if exists.
        css_path = os.path.join(self.config().data_dir, "css")
        css_path = os.path.join(css_path, card_type.id)
        if os.path.exists(css_path):
            f = file(css_path)
            self._css[card_type.id] = file(css_path).read()
            return       
        # Else, construct from configuration data.
        self._css[card_type.id] = """<style type="text/css">\n"""         
        # Background colours.
        self._css[card_type.id] += "body { "
        try:
            colour = self.config()["background_colour"][card_type.id]
            colour_string = ("%X" % colour)[2:] # Strip alpha.
            self._css[card_type.id] += "background-color: #%s;" % colour_string
        except:
            pass
        self._css[card_type.id] += \
            """margin: 0; padding: 0; border: thin solid #8F8F8F; }\n"""
        # Set aligment of the table (but not the contents within the table).
        self._css[card_type.id] += """table { height: 100%; """  
        try:
            alignment = self.config()["alignment"][card_type.id]
        except:
            alignment = "center"
        if alignment == "left":
            self._css[card_type.id] += "margin-left: 0; margin-right: auto; "
        elif alignment == "right":
            self._css[card_type.id] += "margin-left: auto; margin-right: 0; "
        else:
            self._css[card_type.id] += "margin-left: auto; margin-right: auto; "
        self._css[card_type.id] += "}\n"
        # Field tags.
        for key in card_type.keys():
            self._css[card_type.id] += "div#%s { " % key
            # Set alignment within table cell.
            try:
                alignment = self.config()["alignment"][card_type.id]
            except:
                alignment = "center"
            self._css[card_type.id] += "text-align: %s; " % alignment  
            # Text colours.
            try:
                colour = self.config()["font_colour"][card_type.id][key]
                colour_string = ("%X" % colour)[2:] # Strip alpha.
                self._css[card_type.id] += "color: #%s;" % colour_string
            except:
                pass
            # Text font.
            try:
                font_string = self.config()["font"][card_type.id][key]
                family,size,x,x,w,i,u,s,x,x = font_string.split(",")
                self._css[card_type.id] += "font-family: %s; " % family
                self._css[card_type.id] += "font-size: %s pt; " % size
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
                
    def render_card_fields(self, fact, fields, exporting):
        html = "<html><head>" + self.css(fact.card_type) + \
            "</head><body><table><tr><td>"
        for field in fields:
            s = fact[field]
            for f in self.filters():
                if not exporting or (exporting and f.run_on_export):
                    s = f.run(s)
            html += "<div id=\"%s\">%s</div>" % (field, s)
        html += "</td></tr></table></body></html>"
        return html
    
    def render_text(self, text, field_name, card_type, exporting):
        html = "<html><head>" + self.css(card_type) + \
            "</head><body><table><tr><td><div id=\"%s\">"
        html += "<div id=\"%s\">%s</div>" % (field_name, text)
        html += "</td></tr></table></body></html>"
        for f in self.filters():
            if not exporting or (exporting and f.run_on_export):
                html = f.run(html)        
        return html
