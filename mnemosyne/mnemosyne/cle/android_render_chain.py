#
# android_render_chain.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.filters.latex import Latex
from mnemosyne.libmnemosyne.render_chain import RenderChain
from mnemosyne.libmnemosyne.renderers.html_css import HtmlCss
from mnemosyne.libmnemosyne.filters.RTL_handler import RTLHandler
from mnemosyne.libmnemosyne.filters.html5_video import Html5Video
from mnemosyne.libmnemosyne.filters.expand_paths import ExpandPaths
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml
from mnemosyne.libmnemosyne.filters.non_latin_font_size_increase import \
     NonLatinFontSizeIncrease


class AndroidRenderChain(RenderChain):

    """Renders either the question or answer as a complete web page.

    The ExpandPaths and EscapeToHtml filter needs to run after the
    Latex filter.

    """

    id = "android"

    filters = [Latex, EscapeToHtml, ExpandPaths, Html5Video,
               RTLHandler, NonLatinFontSizeIncrease]
    renderers = [HtmlCss]