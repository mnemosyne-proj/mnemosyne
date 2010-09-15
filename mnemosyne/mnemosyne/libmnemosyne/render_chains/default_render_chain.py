#
# default_render_chain.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.filters.latex import Latex
from mnemosyne.libmnemosyne.render_chain import RenderChain
from mnemosyne.libmnemosyne.renderers.html_css import HtmlCss
from mnemosyne.libmnemosyne.filters.html5_media import Html5Media
from mnemosyne.libmnemosyne.filters.expand_paths import ExpandPaths
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml


class DefaultRenderChain(RenderChain):

    """Renders either the question or answer as a complete web page.

    The ExpandPaths filter needs to run after the Latex filter.
    
    """

    id = "default"

    filters = [EscapeToHtml, Latex, ExpandPaths, Html5Media]
    renderers = [HtmlCss]
