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
        f.run("")

    def test_html5(self):

        f = Html5Media(self.mnemosyne.component_manager)

        self.config()["autoplay"] = True
        self.config()["controls"] = True        

        assert f.run("""<audio src="a">""") == \
              """<audio src="a" autoplay=1 controls=1>"""

        self.config()["autoplay"] = True
        self.config()["controls"] = False

        assert f.run("""<video src="a">""") == \
              """<video src="a" autoplay=1>"""
    
        self.config()["autoplay"] = False
        self.config()["controls"] = True

        assert f.run("""<video src="a">""") == \
              """<video src="a" controls=1>"""
    
