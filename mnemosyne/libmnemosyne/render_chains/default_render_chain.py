#
# default_render_chain.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.filters.latex import Latex
from mnemosyne.libmnemosyne.render_chain import RenderChain
from mnemosyne.libmnemosyne.renderers.html_css import HtmlCss
from mnemosyne.libmnemosyne.filters.furigana import Furigana
from mnemosyne.libmnemosyne.filters.RTL_handler import RTLHandler
from mnemosyne.libmnemosyne.filters.html5_audio import Html5Audio
from mnemosyne.libmnemosyne.filters.html5_video import Html5Video
from mnemosyne.libmnemosyne.filters.expand_paths import ExpandPaths
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml
from mnemosyne.libmnemosyne.filters.non_latin_font_size_increase import \
     NonLatinFontSizeIncrease


class DefaultRenderChain(RenderChain):

    """Renders either the question or answer as a complete web page.

    The ExpandPaths and EscapeToHtml filter needs to run after the
    Latex filter.

    """

    id = "default"

    filters = [Latex, EscapeToHtml, ExpandPaths, Html5Audio, Html5Video,
               RTLHandler, Furigana, NonLatinFontSizeIncrease]
    renderers = [HtmlCss]

