##############################################################################
#
# ui_controller_review.py <Peter.Bienstman@UGent.be>
#
##############################################################################

from plugin import Plugin



##############################################################################
#
# UiControllerReview
#
##############################################################################

class UiControllerReview(Plugin):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self, name, description, can_be_unregistered=True):

        self.type                = "ui_controller_review"
        self.widget              = None
        self.name                = name
        self.description         = description
        self.can_be_unregistered = can_be_unregistered

    


    ##########################################################################
    #
    # Functions to be implemented by the actual controller.
    #
    ##########################################################################

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
    
