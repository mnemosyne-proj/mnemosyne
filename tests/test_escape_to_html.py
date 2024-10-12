#
# test_escape_to_html.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml


class TestEscapeToHtml:

    def test_1(self):
        in_string = "<1"
        out_string = "&lt;1"
        assert EscapeToHtml(None).run(in_string, None, None) == out_string

    def test_2(self):
        in_string = "<1>"
        out_string = "<1>"
        assert EscapeToHtml(None).run(in_string, None, None) == out_string

    def test_3(self):
        in_string = "a\nb"
        out_string = "a<br>b"
        assert EscapeToHtml(None).run(in_string, None, None) == out_string

    def test_4(self):
        in_string = "<><"
        out_string = "<>&lt;"
        assert EscapeToHtml(None).run(in_string, None, None) == out_string

    def test_5(self):
        in_string = "<<>"
        out_string = "&lt;<>"
        assert EscapeToHtml(None).run(in_string, None, None) == out_string

    def test_6(self):
        in_string = "<latex>\n</latex>"
        assert "<br>" not in EscapeToHtml(None).run(in_string, None, None)
        in_string = "<latex></latex>\n"
        assert "<br>" in EscapeToHtml(None).run(in_string, None, None)
        in_string = "<ul>\n</ul>"
        assert "<br>" not in EscapeToHtml(None).run(in_string, None, None)
        in_string = "<ul></ul>\n"
        assert "<br>" in EscapeToHtml(None).run(in_string, None, None)
        in_string = "<table>\n</table>"
        assert "<br>" not in EscapeToHtml(None).run(in_string, None, None)
        in_string = "<table></table>\n"
        assert "<br>" in EscapeToHtml(None).run(in_string, None, None)