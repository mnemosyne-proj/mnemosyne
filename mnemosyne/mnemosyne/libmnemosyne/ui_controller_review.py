#
# ui_controller_review.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class UiControllerReview(Component):

    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.widget = None
        self.card = None

    def current_card(self):
        raise NotImplementedError

    def new_question(self):
        raise NotImplementedError

    # TODO: add



    # TODO: list calls made back to widget

    # set_window_title(title)
    # enable_edit_current_card(bool)
    # enable_delete_current_card(bool)
    # enable_edit_deck(bool)
    # question_box_visible(bool)
    # answer_box_visible(bool)
    # set_question_label(text)
    # set_question(text)
    # set_answer(text)
    # clear_question()
    # clear_answer()
    # update_show_button(text,default,enabled)

