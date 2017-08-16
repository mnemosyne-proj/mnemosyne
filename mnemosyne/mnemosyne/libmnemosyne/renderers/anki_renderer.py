#
# anki_renderer.py <Peter.Bienstman@UGent.be>
#

import re
import copy

from mnemosyne.libmnemosyne.renderer import Renderer
from mnemosyne.libmnemosyne.card_types.M_sided import MSided
from mnemosyne.libmnemosyne.renderers.anki.template import render as _render


class AnkiRenderer(Renderer):

    """Renders the question or the answer using the Anki syntax."""

    used_for = MSided

    def render(self, card, filtered_fact_data, render_chain, **render_args):
        card_type = card.card_type
        extra_data = card.fact_view.extra_data
        extra_data["ord"] = card.extra_data["ord"]
        fields = {}
        for fact_key, fact_key_name in card_type.fact_keys_and_names:
            fields[fact_key_name] = filtered_fact_data.get(fact_key, "")
        fields["Tags"] = "" # Mnemosyne shows tags elsewhere.
        fields["Type"] = card_type.name
        fields["Deck"] = ""
        fields["Subdeck"] = ""
        fields["Card"] = card.fact_view.name
        fields["c%d" % (extra_data["ord"] + 1)] = "1"
        if render_args["render_QA"] == "Q":
            if render_chain in ["plain_text", "card_browser"] \
               and extra_data["bqfmt"]:
                template = extra_data["bqfmt"]
            else:
                template = extra_data["qfmt"]
            template = re.sub("{{(?!type:)(.*?)cloze:", r"{{\1cq-%d:" \
                                % (extra_data["ord"]+1), template)
            template = template.replace("<%cloze:", "<%%cq:%d:" % (
                    extra_data["ord"] + 1))
        else:
            if render_chain in ["plain_text", "card_browser"] and \
               extra_data["bafmt"]:
                    template = extra_data["bafmt"]
            else:
                template = extra_data["afmt"]
            # If possible, strip the question part from the template, so that
            # we can display Q and A in a separate window.
            if self.config()["QA_split"] != "single_window":
                if "<hr id=answer>" in template:
                    template = template.split("<hr id=answer>", 1)[1].strip()
            # Deal with clozes.
            template = re.sub("{{(.*?)cloze:", r"{{\1ca-%d:" \
                              % (extra_data["ord"]+1), template)
            template = template.replace("<%cloze:", "<%%ca:%d:" % (
                    extra_data["ord"] + 1))
            if "FrontSide" in render_args:
                fields["FrontSide"] = render_args["FrontSide"].\
                    replace("audio src", "audio_off src")
        body = _render(template, fields)
        if render_chain in ["plain_text", "card_browser"] or \
           ("body_only" in render_args and render_args["body_only"] == True):
            return body
        else:
            return """
            <!doctype html>
            <html>
            <head><style>%s</style></head>
            <body class="card">%s</body>
            </html>""" % (card_type.extra_data["css"], body)

