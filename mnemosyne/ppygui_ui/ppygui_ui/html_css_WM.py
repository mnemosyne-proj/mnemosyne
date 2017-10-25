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
    
    def render(self, fact_data, fact_keys, card_type,
               render_chain, **render_args):
        html = "<html><head><style type=\"text/css\">\n" + \
            self.css(card_type) + "</style></head><body><table "
        alignment = self.config().card_type_property(\
            "alignment", card_type, default="center")
        if alignment == "left":
            html += "align=left"
        elif alignment == "right":
            html += "align=right"
        else:
            html += "align=center"
        html += "><tr><td>"
        for fact_key in fact_keys:
            if fact_key in fact_data and fact_data[fact_key]:
                html += "<div id=\"%s\">%s</div>" % \
                        (fact_key, fact_data[fact_key])          
        html += "</td></tr></table></body></html>"
        return html
