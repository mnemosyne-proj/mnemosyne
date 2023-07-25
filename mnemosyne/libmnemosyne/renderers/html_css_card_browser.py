#
# html_css_card_browser.py <Peter.Bienstman@gmail.com>
#

import re

from mnemosyne.libmnemosyne.renderers.html_css import HtmlCss

colour_re = re.compile(r"color:.+?;")

class HtmlCssCardBrowser(HtmlCss):

    """Renders the question or the answer as html to be used in the card 
    browser. The idea is to display everything as much as possible on a 
    single line which fits with the rest of the table, so we only respect
    fonts families, colours and weights, not size and alignment.

    """

    def body_css(self, **render_args):
        return "body { margin: 0px; height: 100%;  width: 100%;}\n"

    def card_type_css(self, card_type, **render_args):
        self.table_height = "100%"
        css = "table.mnem { height: " + self.table_height + "; width: 100%;}\n"
        css += "._search { color: red; }\n"       
        # Key tags.
        for true_fact_key, proxy_fact_key in \
            card_type.fact_key_format_proxies().items():
            css += ".%s { " % true_fact_key 
            # Font colours.
            if "force_text_colour" in render_args and \
               render_args["force_text_colour"]:
                colour = render_args["force_text_colour"]
            else:
                colour = self.config().card_type_property(\
                    "font_colour", card_type, proxy_fact_key)
            if colour:
                colour_string = ("%X" % colour)[2:] # Strip alpha.
                css += "color: #%s; " % colour_string
            # Font.
            font_string = self.config().card_type_property(\
                "font", card_type, proxy_fact_key)
            if font_string:
                style = ""
                if font_string.count(",") == 9:
                    family,size,x,x,w,i,u,s,x,x = font_string.split(",")
                elif font_string.count(",") == 10:
                    family,size,x,x,w,i,u,s,x,x,x = font_string.split(",")
                elif font_string.count(",") == 15:
                    family,size,x,x,w,i,u,s,x,x,x,x,x,x,x,style \
                        = font_string.split(",")
                else:
                    #Segoe UI,11,-1,5,400,0,0,0,0,0,0,0,0,0,0,1,Regular
                    #Segoe UI,26,-1,5,700,1,1,1,0,0,0,0,0,0,0,1,Bold Italic
                    family,size,x,x,w,i,u,s,x,x,x,x,x,x,x,x,style \
                        = font_string.split(",")                    
                css += "font-family: \"%s\"; " % family
                if w == "25":
                    css += "font-weight: light; "
                if w == "75" or "bold" in style.lower():
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

    def body(self, fact_data, fact_keys, **render_args):
        html = ""
        for fact_key in fact_keys:
            if fact_key in fact_data and fact_data[fact_key]:
                fact_data_fact_key = fact_data[fact_key].replace("\n", " / ")
                html += "<span class=\"%s\">%s</span> / " % \
                    (fact_key, fact_data_fact_key)
        return html[:-2]

    def render(self, fact_data, fact_keys, card_type, **render_args):
        css = self.css(card_type, **render_args)
        if "ignore_text_colour" in render_args and \
            render_args["ignore_text_colour"] == True:
            css = colour_re.sub("", css)
        if "search_string" in render_args and render_args["search_string"]:
            search_string = render_args["search_string"]
            for symbol in ["\\", "(", ")", "?", ".", "^", "*",
                "$", "+", "[", "]"]:  # / needs to be listed first.
                search_string = search_string.replace(symbol, "\\" + symbol)
            search_re = re.compile("(" + search_string + ")", re.IGNORECASE)
            for fact_key in fact_keys:
                if fact_key in fact_data and fact_data[fact_key]:
                    fact_data[fact_key] = search_re.sub(\
                    "<span class=\"_search\">\\1</span>", fact_data[fact_key])
        body = self.body(fact_data, fact_keys, **render_args)
        if body == "":
            body = "&nbsp;"   
        return """
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="utf-8">
            <style type="text/css">
            %s
            </style>
            </head>
            <body>
            <table id="mnem1" class="mnem">
            <tr>
              <td>%s</td>
            </tr>
            </table>
            </body>
            </html>""" % (css, body)        
