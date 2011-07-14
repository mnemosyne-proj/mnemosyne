#
# html_css_card_browser.py <Peter.Bienstman@UGent.be>
#

import re

from mnemosyne.libmnemosyne.renderers.html_css import HtmlCss

colour_re = re.compile(r"color:.+?;")

class HtmlCssCardBrowser(HtmlCss):

    """Renders the question or the answer as html without tables, to be used
    in the card browser. The idea is to display everything as much as possible
    on a single line which fits with the rest of the table, so we only respect
    fonts families, colours and weights, not size and alignment.
    
    """
    
    def body_css(self):
        return "body { margin: 0; padding: 0; }\n"

    def card_type_css(self, card_type):
        css = "._search { color: red; }"
        # Field tags.
        for true_key, proxy_key in card_type.key_format_proxies().iteritems():
            css += ".%s { " % true_key
            # Font colours.
            colour = self.config().card_type_property(\
                "font_colour", card_type, proxy_key)
            if colour:
                colour_string = ("%X" % colour)[2:] # Strip alpha.
                css += "color: #%s; " % colour_string
            # Font.
            font_string = self.config().card_type_property(\
                "font", card_type, proxy_key)
            if font_string:
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
            css += "}\n"
        return css

    def body(self, data, fields, **render_args):
        html = ""
        for field in fields:
            if field in data and data[field]:
                data_field = data[field].replace("\n", " / ")
                html += "<span class=\"%s\">%s</span> / " % (field, data_field)
        return html[:-2]
                
    def render_fields(self, data, fields, card_type, **render_args):
        css = self.css(card_type)
        if "ignore_text_colour" in render_args and \
            render_args["ignore_text_colour"] == True:
            css = colour_re.sub("", css)
        if "search_string" in render_args and render_args["search_string"]:
            search_string = render_args["search_string"]
            for symbol in ["(", ")", "?", ".", "^", "*", "$", "+"]:
                search_string = search_string.replace(symbol, "\\" + symbol)
            search_re = re.compile("(" + search_string + ")", re.IGNORECASE)
            for field in fields:
                if field in data and data[field]:
                    data[field] = search_re.sub(\
                    "<span class=\"_search\">\\1</span>", data[field])
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
    
