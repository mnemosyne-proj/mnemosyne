#
# M_sided.py <Peter.Bienstman@gmail.com>
#

import os
import sys
import copy

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml


class MSided(CardType):

    """Abstract parent class for M-sided card types with Anki syntax."""

    id = "7"
    name = _("M-sided")
    hidden_from_UI = True

    # Need to be overwritten with correct instance variables at creation.
    fact_keys_and_names = []
    fact_views = []
    unique_fact_keys = []
    required_fact_keys = []

    def __init__(self, component_manager):
        super().__init__(component_manager)
        # Add Anki files to Python path.
        path = os.path.join(os.path.dirname(sys.modules['mnemosyne'].__file__),
                            "libmnemosyne", "renderers")
        if path not in sys.path:
            sys.path.append(path)
        from mnemosyne.libmnemosyne.renderers.anki_renderer import AnkiRenderer
        self.renderer = AnkiRenderer(component_manager)

    def render_question(self, card, render_chain="default", **render_args):
        return self._render(card, render_chain, render_QA="Q", **render_args)

    def render_answer(self, card, render_chain="default", **render_args):
        # If we cannot isolate the question from the answer, and we need
        # the 'FrontSide' info, calculate this info first.
        if self.config()["QA_split"] == "single_window" or \
                "<hr id=answer>" not in card.fact_view.extra_data["afmt"]:
            if "FrontSide" in card.fact_view.extra_data["afmt"]:
                new_render_args = copy.copy(render_args)
                new_render_args["body_only"] = True
                render_args["FrontSide"] = \
                    self.render_question(card, render_chain, **new_render_args)
        return self._render(card, render_chain, render_QA="A", **render_args)

    def _render(self, card, render_chain="default", **render_args):
        # Because there is no list of fact keys for q or a for this card type,
        # we need to run the filters after assembling the content, not before.
        html = self.renderer.render(\
            card, card.fact.data, render_chain, **render_args)
        if "body_only" in render_args and render_args["body_only"] == True:
            return html  # Filters will be run later.
        for filter in self.render_chain(render_chain)._filters:
            # EscapeToHtml introduces <br> inside css.
            if filter.__class__ != EscapeToHtml:
                html = filter.run(html, card, fact_key=None, **render_args)
        return html

