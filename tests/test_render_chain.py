#
# test_render_chain.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.renderer import Renderer


class TestRenderChain(MnemosyneTest):

    def test_add_filter(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["default"])[0]

        class MyFilter(Filter):
            def run(self, text, card, fact_key):
                return "666"

        self.render_chain().register_filter(MyFilter)

        assert "666" in card.question()
        assert isinstance(self.render_chain().filter(MyFilter), MyFilter)
        assert self.render_chain().filter(TestRenderChain) is None

        assert type(self.render_chain()._filters[0]) \
               != type(MyFilter(self.mnemosyne.component_manager))

        self.render_chain().unregister_filter(MyFilter)
        assert "666" not in card.question()

        self.render_chain().unregister_filter(type(1))

    def test_add_filter_2(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["default"])[0]

        class MyFilter(Filter):
            def run(self, text, card, fact_key):
                return "666"

        self.render_chain().register_filter(MyFilter, in_front=True)
        assert "666" in card.question()

        assert type(self.render_chain()._filters[0]) \
               == type(MyFilter(self.mnemosyne.component_manager))

    def test_add_filter_order(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["default"])[0]

        class MyFilter1(Filter):
            def run(self, text, card, fact_key):
                return "666"

        class MyFilter2(Filter):
            def run(self, text, card, fact_key):
                return "[%s]" % text

        class MyFilter3(Filter):
            def run(self, text, card, fact_key):
                return "(%s)" % text

        class MyFilter4(Filter):
            def run(self, text, card, fact_key):
                return "{%s}" % text

        def equals(filter_class):
            ty = type(filter_class(self.mnemosyne.component_manager))
            def eq(x):
                return type(x) == ty
            return eq

        self.render_chain().register_filter_at_front(MyFilter1)
        assert "666" in card.question()

        self.render_chain().register_filter_at_front(MyFilter2, [MyFilter1.__name__])
        assert "[666]" in card.question()

        self.render_chain().register_filter_at_back(MyFilter3, [MyFilter2.__name__])
        assert "[(666)]" in card.question()

        self.render_chain().register_filter_at_front(MyFilter4, [MyFilter3.__name__])
        assert "[{(666)}]" in card.question()

        assert type(self.render_chain()._filters[0]) \
               == type(MyFilter1(self.mnemosyne.component_manager))

        assert type(self.render_chain()._filters[1]) \
               == type(MyFilter3(self.mnemosyne.component_manager))

        assert type(self.render_chain()._filters[2]) \
               == type(MyFilter4(self.mnemosyne.component_manager))

        assert type(self.render_chain()._filters[3]) \
               == type(MyFilter2(self.mnemosyne.component_manager))

    def test_add_card_type_renderer(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["default"])[0]

        class MyRenderer(Renderer):
            used_for = card_type_1
            def render(self, fact_data, fields, card_type, **render_args):
                return "666"

        self.render_chain().register_renderer(MyRenderer)
        assert "666" in card.question()

        card_type_2 = self.card_type_with_id("2")
        card = self.controller().create_new_cards(fact_data, card_type_2,
            grade=-1, tag_names=["default"])[0]
        assert "666" not in card.question()

        self.render_chain().unregister_renderer(MyRenderer)
        assert "666" not in card.question()

        self.render_chain().unregister_renderer(type(1))

    def test_latex(self):
        fact_data = {"f": "<latex>1<2</latex>",
                     "b": "answer"}
        card_type_1 = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["default"])[0]
        card.question()

        filename = os.path.join(os.path.abspath("dot_test"),
            "default.db_media", "_latex", "tmp.tex")
        contents = "".join(open(filename).readlines())
        assert '<' in contents
        assert "&lt;" not in contents
