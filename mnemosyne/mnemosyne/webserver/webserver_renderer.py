#
# webserver_renderer.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.renderers.html_css import HtmlCss


class WebserverRenderer(HtmlCss):

    """Renders the question or the answer as html, to be embedded in another
    webpage.
        
    """

    def render_fields(self, data, fields, card_type, **render_args):
        return self.body(data, fields, **render_args)

