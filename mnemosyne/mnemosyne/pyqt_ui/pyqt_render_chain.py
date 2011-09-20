#
# pyqt_render_chain.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.filters.latex import Latex
from mnemosyne.libmnemosyne.render_chain import RenderChain
from mnemosyne.libmnemosyne.renderers.html_css import HtmlCss
from mnemosyne.libmnemosyne.filters.html5_media import Html5Media
from mnemosyne.libmnemosyne.filters.expand_paths import ExpandPaths
from mnemosyne.pyqt_ui.mp3_clip_prevention import Mp3ClipPrevention
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml
from mnemosyne.libmnemosyne.filters.non_latin_font_size_increase import \
     NonLatinFontSizeIncrease

class PyQtRenderChain(RenderChain):

    id = "default"

    filters = [EscapeToHtml, Latex, ExpandPaths, Html5Media,
               Mp3ClipPrevention, NonLatinFontSizeIncrease]
    renderers = [HtmlCss]
