#
# html_css_old.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne.libmnemosyne.renderers.html_css import HtmlCss 


class HtmlCss_WM(HtmlCss):

    """Modified version of html_css.py to work better with older,
    non-standard compliant browsers. It has been tweaked specifically for
    the html widget in Windows Mobile.

    Changes:
    - table height is 95% instead of 100% to avoid spurious scrollbars.
    - centering is done in html as opposed to only in css.
      
    """
    
    used_for = "default"
    table_height = "95%"
    
    def render_fields(self, field_data, fields, card_type,
                      render_chain, **render_args):
        html = "<html><head><style type=\"text/css\">\n" + \
            self.css(card_type) + "</style></head><body><table "
        try:
            alignment = self.config()["alignment"][card_type.id]
        except:
            alignment = "center"
        if alignment == "left":
            html += "align=left"
        elif alignment == "right":
            html += "align=right"
        else:
            html += "align=center"
        html += "><tr><td>"
        for field in fields:
            s = field_data[field]
            for f in self.filters(render_chain):
                s = f.run(s, **render_args)
            html += "<div id=\"%s\">%s</div>" % (field, s)            
        html += "</td></tr></table></body></html>"
        return html

