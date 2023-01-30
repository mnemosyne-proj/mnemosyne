#
# render_chain.py <Peter.Bienstman@gmail.com>
#

import copy
import string

from mnemosyne.libmnemosyne.component import Component


class RenderChain(Component):

    """A RenderChain details the operations needed to get from the raw data
    in a card to a representation of its question and answer, in a form either
    suitable for displaying in a browser, or exporting to a text file, ... .

    First the raw data is sent through Filters, which perform operations which
    can be useful for many card types, like expanding relative paths.

    Sometimes Mnemosyne will try to assemble the answer together with the
    question on a single page, e.g. if config()["QA_split"] == "single_window".
    For some Renderers where this does not make sense, e.g. the card browser,
    set 'never_join_q_to_a = True'.

    Then this data is assembled in the right order in a Renderer, which can be
    card type specific.

    'filters': list of Filter classes
    'renderers': list or Renderer classes

    Plugins can add Filters or Renderers for a new card type to a chain at run
    time. In case the rendering of a card type does not fit comfortably in the
    scheme below, an alternative is to override 'render_question' and
    'render_answer' in CardType directly.

    Each client should have a render chain with id="default" on startup.

    """

    component_type = "render_chain"
    id = "default"

    never_join_q_to_a = False

    filters = []
    renderers = []

    def __init__(self, component_manager):
        # To have an nice syntax when defining renderers, we do the
        # instantiation here.
        Component.__init__(self, component_manager)
        self._filters = []
        for filter in self.filters:
            self._filters.append(filter(component_manager))
        self._renderers = []
        self._renderer_for_card_type = {}
        for renderer in self.renderers:
            renderer = renderer(component_manager)
            self._renderers.append(renderer)
            self._renderer_for_card_type[renderer.used_for] = renderer

    def register_filter_at_front(self, filter_class, after=[]):

        """Register a filter at the very front of the render chain, but after
           a list of other filters already in the chain. The list should
           contain class names. (Using strings instead of classes means a
           plugin writer does not need to import the filters he wants to use
           in this list.)

           'filter_class' should be a class, not an instance.

        """

        filter = filter_class(self.component_manager)
        pos = 0
        for i in range(0, len(self._filters)):
            if self._filters[i].__class__.__name__ in after:
                pos = i + 1
        self._filters.insert(pos, filter)

    def register_filter_at_back(self, filter_class, before=[]):

        """Register a filter at the back of the render chain, but before
           a list of other filters already in the chain. The list should
           contain class names. (Using strings instead of classes means a
           plugin writer does not need to import the filters he wants to use
           in this list.)

           'filter_class' should be a class, not an instance.

        """

        filter = filter_class(self.component_manager)
        pos = len(self._filters)
        for i in range(len(self._filters) - 1, -1, -1):
            if self._filters[i].__class__.__name__ in before:
                pos = i
        self._filters.insert(pos, filter)

    def register_filter(self, filter_class, in_front=False):

        """'filter_class' should be a class, not an instance."""

        if in_front:
            self.register_filter_at_front(filter_class)
        else:
            self.register_filter_at_back(filter_class)

    def filter(self, filter_class):
        for filter_i in self._filters:
            if isinstance(filter_i, filter_class):
                return filter_i

    def unregister_filter(self, filter_class):

        """'filter_class' should be a class, not an instance."""

        for filter in self._filters:
            if isinstance(filter, filter_class):
                self._filters.remove(filter)
                break

    def register_renderer(self, renderer_class):

        """'renderer_class' should be a class, not an instance."""

        renderer = renderer_class(self.component_manager)
        self._renderer_for_card_type[renderer.used_for] = renderer

    def unregister_renderer(self, renderer_class):

        """'renderer_class' should be a class, not an instance."""

        for card_type, renderer in self._renderer_for_card_type.items():
            if isinstance(renderer, renderer_class):
                del self._renderer_for_card_type[card_type]
                break

    def renderer_for_card_type(self, card_type):
        if card_type in self._renderer_for_card_type:
            return self._renderer_for_card_type[card_type]
        if "::" in card_type.id:
            parent_id, child_id = card_type.id.rsplit("::", 1)
            parent = self.database().card_type(parent_id, is_id_internal=-1)
            return self.renderer_for_card_type(parent)
        return self._renderer_for_card_type[None]

    def render_question(self, card, **render_args):
        fact_keys = card.fact_view.q_fact_keys
        decorators = card.fact_view.q_fact_key_decorators
        if self.config()["QA_split"] == "single_window":
            render_args["align_top"] = True
        return self._render(card, fact_keys, decorators, **render_args)

    def render_answer(self, card, **render_args):
        fact_keys, decorators = [], {}
        a_on_top_of_q = render_args.get("a_on_top_of_q", False)
        if self.config()["QA_split"] == "single_window" and \
           not self.never_join_q_to_a and not a_on_top_of_q:
            render_args["align_top"] = True
            fact_keys += card.fact_view.q_fact_keys
            fact_keys.append("__line__")
            decorators.update(card.fact_view.q_fact_key_decorators)
        fact_keys += card.fact_view.a_fact_keys
        decorators.update(card.fact_view.a_fact_key_decorators)
        return self._render(card, fact_keys, decorators, **render_args)

    def _render(self, card, fact_keys, decorators, **render_args):
        # Note that the filters run only on the data, not on the full content
        # generated by the renderer, which would be much slower.
        fact_data = copy.copy(card.card_type.fact_data(card))
        for fact_key in fact_keys:
            if fact_key == "__line__":
                fact_data[fact_key] = "<hr id=answer>"
            if fact_key not in fact_data:  # Optional key.
                continue
            for filter in self._filters:
                fact_data[fact_key] = filter.run(fact_data[fact_key],
                    card, fact_key, **render_args)
            if fact_key in decorators:
                fact_data[fact_key] = string.Template(\
                    decorators[fact_key]).safe_substitute(fact_data)
        renderer = self.renderer_for_card_type(card.card_type)
        return renderer.render(\
            fact_data, fact_keys, card.card_type, **render_args)

