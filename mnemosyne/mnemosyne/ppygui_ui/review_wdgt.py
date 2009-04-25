#
# review_wdgt.py <Peter.Bienstman@UGent.be>
#

import os

if os.name == "ce":
	import ppygui.api as gui
else:
	import emulator.api as gui

from mnemosyne.libmnemosyne.review_widget import ReviewWidget
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import ui_controller_review


# TODO: implement default actions.

class ReviewWdgt(gui.Frame, ReviewWidget):
    
    def __init__(self, parent=None):
        gui.Frame.__init__(self, parent)
        self.controller = ui_controller_review()
        self.all_cards = None # Total number of cards, to be cached.
        
        self.question_label = gui.Label(self, "Question:")
        self.question = gui.Html(self)
        
        self.answer_label = gui.Label(self, "Answer:")
        self.answer = gui.Html(self)
        
        self.show_button = gui.Button(self, "Show answer")
        self.show_button.bind(clicked=self.show_answer)

        self.grade_sizer = gui.HBox(border=(5, 5, 5, 5), spacing=20)
        # TODO: possible to simplify?
        self.grade_button_0 = gui.Button(self, title="0", border=True,
                                         action=self.grade_answer_0)
        self.grade_button_1 = gui.Button(self, title="1", border=True,
                                         action=self.grade_answer_1)
        self.grade_button_2 = gui.Button(self, title="2", border=True,
                                         action=self.grade_answer_2)
        self.grade_button_3 = gui.Button(self, title="3", border=True,
                                         action=self.grade_answer_3)
        self.grade_button_4 = gui.Button(self, title="4", border=True,
                                         action=self.grade_answer_4)
        self.grade_button_5 = gui.Button(self, title="5", border=True,
                                         action=self.grade_answer_5)      
        self.grade_sizer.add(self.grade_button_0)
        self.grade_sizer.add(self.grade_button_1)
        self.grade_sizer.add(self.grade_button_2)
        self.grade_sizer.add(self.grade_button_3)
        self.grade_sizer.add(self.grade_button_4)
        self.grade_sizer.add(self.grade_button_5)
        self.grade_buttons = []
        self.grade_buttons.append(self.grade_button_0)
        self.grade_buttons.append(self.grade_button_1)
        self.grade_buttons.append(self.grade_button_2)
        self.grade_buttons.append(self.grade_button_3)
        self.grade_buttons.append(self.grade_button_4)
        self.grade_buttons.append(self.grade_button_5)
        
        self.status_sizer = gui.HBox(spacing=10)
        self.scheduled_label = gui.Label(self, "S: ")
        self.not_memorised_label = gui.Label(self, "NM: ")
        self.all_label = gui.Label(self, "A: " )
        self.status_sizer.add(self.scheduled_label)
        self.status_sizer.add(self.not_memorised_label)
        self.status_sizer.add(self.all_label)

        sizer = gui.VBox()
        sizer.add(self.question_label)
        sizer.add(self.question)
        sizer.add(self.answer_label)
        sizer.add(self.answer)
        sizer.add(self.show_button)
        sizer.add(self.grade_sizer)
        sizer.add(self.status_sizer)
        self.sizer = sizer
        
    def question_box_visible(self, visible):
        if visible:
            self.question_label.show()
            self.question.show()
        else:
            self.question_label.hide()
            self.question.hide()
            
    def answer_box_visible(self, visible):
        if visible:
            self.answer_label.show()
            self.answer.show()
        else:
            self.answer_label.hide()
            self.answer.hide()

    def set_question_label(self, text):
        return
        # Labels can get their text only once.
        self.question_label.text = text
        
    def set_question(self, text):
		self.question.value = text

    def set_answer(self, text):
		self.answer.value = text

    def clear_question(self):
		self.question.value = ""
               
    def clear_answer(self):
		self.answer.value = ""

    def update_show_button(self, text, default, enabled):
        self.show_button.text = text
        if enabled:
            self.show_button.show()
        else:
            self.show_button.hide()

    def enable_grades(self, enabled):
        if enabled:
            for button in self.grade_buttons:
                button.show()
        else:
            for button in self.grade_buttons:
                button.hide()

    def show_answer(self, event):
        self.controller.show_answer()

    # TODO: possible to simplify?
            
    def grade_answer_0(self, event):
        print event
        self.controller.grade_answer(0)

    def grade_answer_1(self, event):
        self.controller.grade_answer(1)

    def grade_answer_2(self, event):
        self.controller.grade_answer(2)

    def grade_answer_3(self, event):
        self.controller.grade_answer(3)

    def grade_answer_4(self, event):
        self.controller.grade_answer(4)

    def grade_answer_5(self, event):
        self.controller.grade_answer(5)
        
    def update_status_bar(self):
        db = database()
        if not self.all_cards:
            self.all_cards = db.active_count()
        self.scheduled_label.text = "S: " + str(db.scheduled_count())
        self.not_memorised_label.text = "NM: " + str(db.non_memorised_count())
        self.all_label.text = "A: " + str(self.all_cards)

