#
# html_css.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.renderer import Renderer

# Css table wizardry based on info from
# http://apptools.com/examples/tableheight.php


class HtmlCss(Renderer):

    """Renders the question or the answer as a full webpage.
    Tested on webkit-based browsers.

    We split out the components of the html page in different functions,
    to allow easier reuse by other renderers.
    
    """

    used_for = "default", "sync_to_card_only_client"
    table_height = "100%"
    
    def __init__(self, component_manager):
        Renderer.__init__(self, component_manager)
        # We cache the css creation to save some time, especially on mobile
        # devices.
        self._css = {} # {card_type.id: css}

    def body_css(self):
        return "body { margin: 0; padding: 0; border: thin solid #8F8F8F; }\n"

    def card_type_css(self, card_type):
        # Set aligment of the table (but not the contents within the table).
        css = "table { height: " + self.table_height + "; width: 100%; "
        try:
            alignment = self.config()["alignment"][card_type.id]
        except:
            alignment = "center"
        if alignment == "left":
            css += "margin-left: 0; margin-right: auto; "
        elif alignment == "right":
            css += "margin-left: auto; margin-right: 0; "
        else:
            css += "margin-left: auto; margin-right: auto; "
        # Background colours.
        try:
            colour = self.config()["background_colour"][card_type.id]
            colour_string = ("%X" % colour)[2:] # Strip alpha.
            css += "background-color: #%s;" % colour_string
        except:
            pass        
        css += "}\n"
        # Field tags.
        for key in card_type.keys():
            css += "div#%s { " % key
            # Set alignment within table cell.
            try:
                alignment = self.config()["alignment"][card_type.id]
            except:
                alignment = "center"
            css += "text-align: %s; " % alignment  
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
                css += "font-size: %spt; " % size
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

    def update(self, card_type):
        self._css[card_type.id] = \
                self.body_css() + self.card_type_css(card_type)
        
    def css(self, card_type):
        if not card_type.id in self._css:
            self.update(card_type)
        return self._css[card_type.id]

    def body(self, field_data, fields, render_chain, **render_args):
        # Note that the filter only run on the card data, not on the full
        # webpage. This is done for efficiency reasons. If a plugin needs
        # to modify e.g. the css, this is best done in a new renderer as
        # opposed to in a filter.
        html = ""
        for field in fields:
            s = field_data[field]
            for f in self.filters(render_chain):
                s = f.run(s, **render_args)
            html += "<div id=\"%s\">%s</div>" % (field, s)
        return html
                
    def render_fields(self, field_data, fields, card_type,
                      render_chain, **render_args):
        css = self.css(card_type)
        body = self.body(field_data, fields, render_chain, **render_args)  
        return """
        <html>
        <head>
        <style type="text/css">
        %s
        </style>
        </head>
        <body>
          <table>
            <tr>
              <td>%s</td>
            </tr>
          </table>
        </body>
        </html>""" % (css, body)
    

