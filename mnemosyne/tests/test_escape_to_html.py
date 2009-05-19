#
# test_escape_to_html.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml


class TestEscapeToHtml:

    def test_1(self):
        in_string = "<1"
        out_string = "&lt;1"
        assert EscapeToHtml(None).run(in_string) == out_string

    def test_2(self):
        in_string = "<1>"
        out_string = "<1>"
        assert EscapeToHtml(None).run(in_string) == out_string
        
    def test_3(self):
        in_string = "a\nb"
        out_string = "a<br>b"
        assert EscapeToHtml(None).run(in_string) == out_string
        
    def test_4(self):
        in_string = "<><"
        out_string = "<>&lt;"
        assert EscapeToHtml(None).run(in_string) == out_string
        
    def test_5(self):
        in_string = "<<>"
        out_string = "&lt;<>"
        assert EscapeToHtml(None).run(in_string) == out_string
