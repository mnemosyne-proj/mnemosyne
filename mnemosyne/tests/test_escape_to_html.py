#
# test_escape_to_html.py <Peter.Bienstman@UGent.be>
#

from nose.tools import raises

from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml

class TestFilter:
    
    @raises(NotImplementedError)
    def test(self):
        f = Filter()
        f.run("", None)


class TestEscapeToHtml:

    def test_1(self):
        in_string = "<1"
        out_string = "&lt;1"
        assert EscapeToHtml().run(in_string, None) == out_string

    def test_2(self):
        in_string = "<1>"
        out_string = "<1>"
        assert EscapeToHtml().run(in_string, None) == out_string
        
    def test_3(self):
        in_string = "a\nb"
        out_string = "a<br>b"
        assert EscapeToHtml().run(in_string, None) == out_string
        
    def test_4(self):
        in_string = "<><"
        out_string = "<>&lt;"
        assert EscapeToHtml().run(in_string, None) == out_string
        
    def test_5(self):
        in_string = "<<>"
        out_string = "&lt;<>"
        assert EscapeToHtml().run(in_string, None) == out_string
