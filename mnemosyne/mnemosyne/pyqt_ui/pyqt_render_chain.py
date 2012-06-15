#
# pyqt_render_chain.py <Peter.Bienstman@UGent.be>
#

import sys

from mnemosyne.libmnemosyne.filters.latex import Latex
from mnemosyne.libmnemosyne.render_chain import RenderChain
from mnemosyne.libmnemosyne.renderers.html_css import HtmlCss
from mnemosyne.libmnemosyne.filters.html5_audio import Html5Audio
from mnemosyne.libmnemosyne.filters.html5_video import Html5Video
from mnemosyne.libmnemosyne.filters.expand_paths import ExpandPaths
from mnemosyne.libmnemosyne.filters.add_RTL_marker import AddRTLMarker
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml
from mnemosyne.libmnemosyne.filters.non_latin_font_size_increase import \
     NonLatinFontSizeIncrease
if sys.platform == "win32":
    from mnemosyne.pyqt_ui.mplayer_audio import MplayerAudio

class PyQtRenderChain(RenderChain):

    id = "default"

    if sys.platform == "win32":
        filters = [Latex, EscapeToHtml, ExpandPaths, MplayerAudio,
            Html5Video, AddRTLMarker, NonLatinFontSizeIncrease]
    else:
        filters = [Latex, EscapeToHtml, ExpandPaths, Html5Audio,
            Html5Video, AddRTLMarker, NonLatinFontSizeIncrease]

    renderers = [HtmlCss]
