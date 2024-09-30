#
# escape_to_html.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.filter import Filter


class EscapeToHtml(Filter):

    """Escape literal < (unmatched tag) and newline from string."""

    def run(self, text, card, fact_key, **render_args):
        # Replace newline with <br>, but not when enclosed by tags like latex
        # or tables.
        lower_text = text.lower()
        linebreak_positions = []
        escape_breaks = True
        for i in range(len(text)):
            for tag in ["ul", "table", "latex", "script", "textarea"]:
                if lower_text[i:].startswith("<" + tag):
                    escape_breaks = False
                if lower_text[i:].startswith("</" + tag):
                    escape_breaks = True
            if (lower_text[i] == "\n" or lower_text[i] == "\r") \
                and escape_breaks:
                linebreak_positions.append(i)
        for linebreak_position in linebreak_positions:
            text = text[:linebreak_position] + text[linebreak_position:]\
                .replace("\n", "<br>", 1).replace("\r", "<br>", 1)
        # Escape hanging <.
        hanging = []
        open = 0
        pending = 0
        for i in range(len(text)):
            if text[i] == "<":
                if open != 0:
                    hanging.append(pending)
                    pending = i
                    continue
                open += 1
                pending = i
            elif text[i] == ">":
                if open > 0:
                    open -= 1
        if open != 0:
            hanging.append(pending)
        new_text = ""
        for i in range(len(text)):
            if i in hanging:
                new_text += "&lt;"
            else:
                new_text += text[i]
        return new_text
