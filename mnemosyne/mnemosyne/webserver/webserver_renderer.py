#
# webserver_renderer.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.renderers.html_css import HtmlCss


class WebserverRenderer(HtmlCss):

    """Renders the question or the answer as html, to be embedded in another
    webpage.
        
    """

    used_for = "webserver"
    
    def render_fields(self, field_data, fields, card_type,
                      render_chain, **render_args):
        return self.body(field_data, fields, render_chain, **render_args)

