#
# test_filter.py <Peter.Bienstman@UGent.be>
#

from nose.tools import raises

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.filters.html5_media import Html5Media


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
    
