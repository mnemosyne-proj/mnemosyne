#
# html_css_light.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.renderers.html_css import HtmlCss


class HtmlCssLight(HtmlCss):

    """Renders the question or the answer as html without tables, to be used
    e.g. in the card browser. The idea is to display everything as much as
    possible on a single line which fits with the rest of the table, so we
    only respect fonts families and weights, not size and alignment.
    
    """
    
    def body_css(self):
        return "body { margin: 0; padding: 0; }\n"

    def card_type_css(self, card_type):
        css = ""
        # Field tags.
        for key in card_type.keys():
            css += ".%s { " % key
            # Text colours.
            try:
                colour = self.config()["font_colour"][card_type.id][key]
                colour_string = ("%X" % colour)[2:] # Strip alpha.
                css += "color: #%s;" % colour_string
            except:
                pass
            # Text font.
            try:
                font_string = self.config()["font"][card_type.id][key]
                family,size,x,x,w,i,u,s,x,x = font_string.split(",")
                css += "font-family: \"%s\"; " % family
                if w == "25":
                    css += "font-weight: light; "
                if w == "75":
                    css += "font-weight: bold; "                    
                if i == "1":
                    css += "font-style: italic; "
                if i == "2":
                    css += "font-style: oblique; "
                if u == "1":
                    css += "text-decoration: underline; "
                if s == "1":
                    css += "text-decoration: line-through; "
            except:
                pass                
            css += "}\n"
        return css

    def body(self, data, fields, **render_args):
        html = ""
        for field in fields:
            html += "<span class=\"%s\">%s</span> / " % (field, data[field])
        return html[:-2]
                
    def render_fields(self, data, fields, card_type, **render_args):
        css = self.css(card_type)
        body = self.body(data, fields, **render_args)
        return """
        <html>
        <head>
        <style type="text/css">
        %s
        </style>
        </head>
        <body>
        %s
        </body>
        </html>""" % (css, body)
    
