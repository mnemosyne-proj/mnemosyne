#
# web_server_renderer.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.renderers.html_css import HtmlCss


class WebServerRenderer(HtmlCss):

    """Renders the question or the answer as html, to be embedded in another
    webpage.
        
    """

    def render(self, fact_data, fact_keys, card_type, **render_args):
        return self.body(fact_data, fact_keys, card_type, **render_args)

