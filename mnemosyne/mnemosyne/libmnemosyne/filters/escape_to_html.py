#
# escape_to_html.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.filter import Filter


class EscapeToHtml(Filter):

    """Escape literal < (unmatched tag) and new line from string."""

    def run(self, text, card, fact_key, **render_args):
        hanging = []
        open = 0
        pending = 0
        for i in range(len(text)):
            if text[i] == '<':
                if open != 0:
                    hanging.append(pending)
                    pending = i
                    continue
                open += 1
                pending = i
            elif text[i] == '>':
                if open > 0:
                    open -= 1
        if open != 0:
            hanging.append(pending)
        new_text = ""
        for i in range(len(text)):
            if text[i] == '\n':
                new_text += "<br>"
            elif i in hanging:
                new_text += "&lt;"
            else:
                new_text += text[i]
        return new_text
