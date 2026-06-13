#
# frontend.py <lucascontre95@gmail.com>
#

"""Server-side implementations of libmnemosyne's UI component interfaces.

`libmnemosyne` is UI-agnostic: the review controller drives a `ReviewWidget`
through a set of setters, and the rest of the core talks to a `MainWidget` for
messages and dialogs. Here we provide head-less implementations that simply
*record* whatever the core pushes at them, so the FastAPI routers can read that
state back and render it as HTML.

This mirrors `mnemosyne/web_server/review_wdgt.py`, but without baking a full
HTML page into the widget -- rendering is the routers' job (Jinja2 + HTMX).
"""

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class WebMainWidget(MainWidget):

    """Captures messages/questions instead of popping up Qt dialogs.

    Informational and error messages are buffered in `messages` so a router can
    surface them as flash/toast notifications. `show_question` has no human to
    ask mid-request, so it records the prompt and returns a safe default (0,
    i.e. the first / least destructive option). Flows that genuinely need a user
    decision (e.g. import conflicts) get an explicit confirmation step in their
    router rather than relying on this default.
    """

    # Keep the buffer bounded; it is drained by the UI but we never want it to
    # grow without limit if nobody reads it.
    MAX_MESSAGES = 100

    def __init__(self, component_manager):
        super().__init__(component_manager)
        self.messages = []
        self.pending_questions = []
        self.window_title = "Mnemosyne"
        self.status_bar_message = ""

    def _record(self, level, text):
        self.messages.append((level, text))
        if len(self.messages) > self.MAX_MESSAGES:
            del self.messages[:-self.MAX_MESSAGES]

    def drain_messages(self):
        """Return and clear the buffered messages."""
        messages, self.messages = self.messages, []
        return messages

    def activate(self):
        pass

    def set_window_title(self, text):
        self.window_title = text

    def show_information(self, text):
        self._record("info", text)

    def show_error(self, text):
        self._record("error", text)

    def show_question(self, text, option0, option1, option2=""):
        self.pending_questions.append((text, option0, option1, option2))
        return 0

    def show_export_metadata_dialog(self, metadata=None, read_only=False):
        # There is no interactive dialog on a head-less server. The Mnemosyne
        # export formats (*.cards / *.db) ask for card-set metadata here; we
        # supply empty metadata, exactly like libmnemosyne's own database-merge
        # path does (`metadata = {}`). When called read-only during import it
        # just echoes back what was parsed, so returning it is a no-op.
        if read_only:
            return metadata
        return metadata if metadata is not None else {}

    def set_status_bar_message(self, text):
        self.status_bar_message = text


class WebReviewWidget(ReviewWidget):

    """Holds the current review state pushed by the SM2 review controller.

    The controller calls these setters during `update_dialog`; routers read the
    resulting attributes to render the question/answer/grade panel.
    """

    def __init__(self, component_manager):
        super().__init__(component_manager)
        # Render card HTML for the browser (rewrites media URLs, audio/video
        # players, LaTeX, etc.) -- reuses the legacy web server's render chain.
        self.review_controller().set_render_chain("web_server")
        self.question_label = _("Question:")
        self.question = ""
        self.is_question_box_visible = True
        self.answer_label = _("Answer:")
        self.answer = ""
        self.is_answer_box_visible = True
        self.show_button_text = _("Show answer")
        self.is_show_button_enabled = True
        self.is_grades_enabled = False
        self.default_grade = 0
        self.grade_titles = {}

    # -- state recording -----------------------------------------------------

    def set_question_box_visible(self, is_visible):
        self.is_question_box_visible = is_visible

    def set_answer_box_visible(self, is_visible):
        self.is_answer_box_visible = is_visible

    def set_question_label(self, text):
        self.question_label = text

    def set_question(self, text):
        self.question = text

    def set_answer(self, text):
        self.answer = text

    def clear_question(self):
        self.question = ""

    def clear_answer(self):
        self.answer = ""

    def update_show_button(self, text, is_default, is_enabled):
        self.show_button_text = text
        self.is_show_button_enabled = is_enabled

    def set_grades_enabled(self, is_enabled):
        self.is_grades_enabled = is_enabled

    def set_default_grade(self, grade):
        self.default_grade = grade

    def set_grade_text(self, grade, text):
        self.grade_titles[grade] = text

    def update_status_bar_counters(self):
        pass

    # -- no-ops on a stateless HTTP front-end --------------------------------

    def reveal_question(self):
        pass

    def reveal_answer(self):
        pass

    def play_media(self, filename, start=None, stop=None):
        pass

    def stop_media(self):
        pass

    def redraw_now(self):
        # The browser redraws on its own once we return the response.
        pass

    # -- convenience for routers ---------------------------------------------

    def card_type_css(self):
        """CSS for the current card type, or '' when there is no card."""
        card = self.review_controller().card
        if card is None:
            return ""
        renderer = self.render_chain().renderer_for_card_type(card.card_type)
        return renderer.card_type_css(card.card_type)
