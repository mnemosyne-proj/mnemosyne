#
# test_filter.py <Peter.Bienstman@UGent.be>
#

from nose.tools import raises

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.filters.html5_video import Html5Video
from mnemosyne.libmnemosyne.filters.html5_audio import Html5Audio
from mnemosyne.libmnemosyne.filters.RTL_handler import RTLHandler
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml

class TestFilter(MnemosyneTest):

    @raises(NotImplementedError)
    def test(self):
        f = Filter(None)
        f.run("", None, None)

    def test_html5_audio(self):

        f = Html5Audio(self.mnemosyne.component_manager)

        self.config()["media_autoplay"] = True
        self.config()["media_controls"] = True

        f.run("""<audio src="b">""", None, None)

        self.config()["media_autoplay"] = False
        self.config()["media_controls"] = True

        f.run("""<audio src="b">""", None, None)

    def test_html5_video(self):

        f = Html5Video(self.mnemosyne.component_manager)

        self.config()["media_autoplay"] = True
        self.config()["media_controls"] = True

        assert f.run("""<video src="b">""", None, None) == \
              """<video src="b" autoplay=1 controls=1>"""

        self.config()["media_autoplay"] = False
        self.config()["media_controls"] = True

        assert f.run("""<video src="b">""", None, None) == \
              """<video src="b" controls=1>"""

    def test_escape_to_html(self):

         f = EscapeToHtml(self.mnemosyne.component_manager)

         assert f.run("a\nb", None, None) == "a<br>b"
         assert f.run("<latex>a\nb<\latex>", None, None) == "<latex>a\nb<\latex>"

    def test_RTL_handler(self):

        f = RTLHandler(self.mnemosyne.component_manager)

        f.run(unichr(0x0591), None, None)
        f.run(unichr(0x0491), None, None)
        f.run("[a]" + unichr(0x0491), None, None)