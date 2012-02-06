#
# test_filter.py <Peter.Bienstman@UGent.be>
#

from nose.tools import raises

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.filters.html5_media import Html5Media
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml

class TestFilter(MnemosyneTest):

    @raises(NotImplementedError)
    def test(self):
        f = Filter(None)
        f.run("", None, None)

    def test_html5(self):

        f = Html5Media(self.mnemosyne.component_manager)

        self.config()["media_autoplay"] = True
        self.config()["media_controls"] = True

        assert f.run("""<audio src="b">""", None, None) == \
              """<audio src="b" autoplay=1 controls=1>"""

        self.config()["media_autoplay"] = True
        self.config()["media_controls"] = False

        assert f.run("""<video src="b">""", None, None) == \
              """<video src="b" autoplay=1>"""

        self.config()["media_autoplay"] = False
        self.config()["media_controls"] = True

        assert f.run("""<video src="b">""", None, None) == \
              """<video src="b" controls=1>"""

    def test_escape_to_html(self):

         f = EscapeToHtml(self.mnemosyne.component_manager)

         assert f.run("a\nb", None, None) == "a<br>b"
         assert f.run("<latex>a\nb<\latex>", None, None) == "<latex>a\nb<\latex>"