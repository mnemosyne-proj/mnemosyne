#
# render_chain_WM.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.ppygui_ui.html_css_WM import HtmlCss_WM
from mnemosyne.libmnemosyne.filters.latex import Latex
from mnemosyne.libmnemosyne.render_chain import RenderChain
from mnemosyne.libmnemosyne.filters.expand_paths import ExpandPaths
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml


class RenderChain_WM(RenderChain):

    """Renders either the question or answer as a complete web page.

    The ExpandPaths filter needs to run after the Latex filter.
    
    """

    id = "default"

    filters = [EscapeToHtml, Latex, ExpandPaths]
    renderers = [HtmlCss_WM]
