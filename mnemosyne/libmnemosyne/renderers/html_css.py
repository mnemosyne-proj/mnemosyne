#
# html_css.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.renderer import Renderer

# Css table wizardry based on info from
# http://apptools.com/examples/tableheight.php


class HtmlCss(Renderer):

    """Renders the question or the answer as a full webpage using tables.
    Tested on webkit-based browsers.

    We split out the components of the html page in different functions,
    to allow easier reuse by other renderers.

    """

    used_for = None  # All card types.
    table_height = "100%"

    def __init__(self, component_manager):
        Renderer.__init__(self, component_manager)
        # We cache the css creation to save some time, especially on mobile
        # devices.
        self._css = {} # {card_type.id: render_args: css}

    def body_css(self, **render_args):
        css = "html, body { margin: 0px; height: 100%;  width: 100%;}\n"
        css += "hr { background-color: black; height: 1px; border: 0; }\n"
        return css

    def card_type_css(self, card_type, **render_args):
        # Set aligment of the table (but not the contents within the table).
        # Use a separate id such that user created tables are not affected.
        css = "table.mnem { height: " + self.table_height + "; width: 100%; "
        css += "border: 1px solid #8F8F8F; "
        alignment = self.config().card_type_property(\
            "alignment", card_type, default="center")
        if alignment == "left":
            css += "margin-left: 0; margin-right: auto; "
        elif alignment == "right":
            css += "margin-left: auto; margin-right: 0; "
        else:
            css += "margin-left: auto; margin-right: auto; "
        # Background colours.
        colour = self.config().card_type_property(\
            "background_colour", card_type)
        if colour:
            colour_string = ("%X" % colour)[2:] # Strip alpha.
            css += "background-color: #%s; " % colour_string
        css += "}\n"
        # Key tags.
        for true_fact_key, proxy_fact_key in \
            card_type.fact_key_format_proxies().items():
            css += "div.%s { " % true_fact_key
            # Set alignment within table cell.
            alignment = self.config().card_type_property(\
                "alignment", card_type, proxy_fact_key, default="center")
            css += "text-align: %s; " % alignment
            # Font colours.
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
                css += "font-size: %spt; " % size
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

    def update(self, card_type, **render_args):
        if card_type.id not in self._css:
            self._css[card_type.id] = {}
        self._css[card_type.id][repr(sorted(render_args.items()))] =\
            self.body_css(**render_args) + \
            self.card_type_css(card_type, **render_args)

    def css(self, card_type, **render_args):
        render_args_hash = repr(sorted(render_args.items()))
        if not card_type.id in self._css or \
           not render_args_hash in self._css[card_type.id]:
            self.update(card_type, **render_args)
        return self._css[card_type.id][render_args_hash]

    def body(self, fact_data, fact_keys, card_type, **render_args):
        html = ""
        for fact_key in fact_keys:
            if fact_key in fact_data and fact_data[fact_key]:
                line = ""
                if render_args.get("align_top", False):
                    line +="<br>"
                line += "<div id=\"%s\" class=\"%s\">%s</div>" % \
                    (fact_key, fact_key, fact_data[fact_key])
                # Honour paragraph style also in user-created tables.
                line = line.replace("<td>",
                    "<td><div id=\"%s\" class=\"%s\">" % (fact_key, fact_key))
                line = line.replace("<TD>",
                    "<TD><div id=\"%s\" class=\"%s\">" % (fact_key, fact_key))
                line = line.replace("</td>", "</div></td>")
                line = line.replace("</TD>", "</div></TD>")
                html += line
        return html

    def render(self, fact_data, fact_keys, card_type, **render_args):
        css = self.css(card_type)
        valign = "valign=\"top\"" if render_args.get("align_top", False) else ""
        body = self.body(fact_data, fact_keys, card_type, **render_args)
        return """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style type="text/css">
        %s
        </style>
        <script type="text/javascript">
          function scroll_to_answer () {
            window.location.hash = "#answer"
          };
        </script>
        </head>
        <body onload="scroll_to_answer()">
          <table id="mnem1" class="mnem">
            <tr %s>
              <td>%s</td>
            </tr>
          </table>
        </body>
        </html>""" % (css, valign, body)

