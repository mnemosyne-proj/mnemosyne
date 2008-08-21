#
# make_html.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.filter import Filter


class MakeHtml(Filter):

    def run(self, text, obj):
        return \
            "<html><head>" + \
            obj.fact.card_type.css + \
            "</head><body><table><tr><td>" + \
            text + \
            "</td></tr></table></body></html>"
