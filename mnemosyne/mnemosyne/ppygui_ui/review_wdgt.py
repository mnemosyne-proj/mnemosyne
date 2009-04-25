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
    
    def __init__(self, parent):
        gui.Frame.__init__(self, parent)
        self.controller = ui_controller_review()
        self.all_cards = None # Total number of cards, to be cached.

        # Note: ppyui makes heavy use of properties, so we can't use e.g.
        # self.question, as the presence of self.get_question would then
        # require a function self.set_question too.
        
        self._question_label = gui.Label(self, "Question:")
        self._question = gui.Html(self)
        
        self._answer_label = gui.Label(self, "Answer:")
        self._answer = gui.Html(self)
        
        self.show_button = gui.Button(self, "Show answer")
        self.show_button.bind(clicked=self.show_answer)

        self.grade_sizer = gui.HBox(border=(5, 5, 5, 5), spacing=20)
        self.grade_buttons = []
        self.id_for_grade = {}
        for i in range(6):
            button = gui.Button(self, title=" " + str(i) + " ", border=True,
                                action=self.grade_answer)
            self.grade_buttons.append(button)
            self.id_for_grade[button._id] = i        
            self.grade_sizer.add(button)
                    
        self.status_sizer = gui.HBox(spacing=10)
        self.scheduled_label = gui.Label(self, "S: ")
        self.not_memorised_label = gui.Label(self, "NM: ")
        self.all_label = gui.Label(self, "A: " )
        self.status_sizer.add(self.scheduled_label)
        self.status_sizer.add(self.not_memorised_label)
        self.status_sizer.add(self.all_label)

        sizer = gui.VBox()
        sizer.add(self._question_label)
        sizer.add(self._question)
        sizer.add(self._answer_label)
        sizer.add(self._answer)
        sizer.add(self.show_button)
        sizer.add(self.grade_sizer)
        sizer.add(self.status_sizer)
        self.sizer = sizer
        
    def question_box_visible(self, visible):
        if visible:
            self._question_label.show()
            self._question.show()
        else:
            self._question_label.hide()
            self._question.hide()
            
    def answer_box_visible(self, visible):
        if visible:
            self._answer_label.show()
            self._answer.show()
        else:
            self._answer_label.hide()
            self._answer.hide()

    def set_question_label(self, text):
        self._question_label.text = text
        
    def set_question(self, text):
        print 'q', text
        self._question.value = text

    def set_answer(self, text):
		self._answer.value = text

    def clear_question(self):
		self._question.value = ""
               
    def clear_answer(self):
		self._answer.value = ""

    def update_show_button(self, text, default, enabled):
        self.show_button.text = text
        # TODO:
        #if enabled:
        #    self.show_button.show()
        #else:
        #    self.show_button.hide()

    def enable_grades(self, enabled):
        return
        # TODO
        if enabled:
            for button in self.grade_buttons:
                button.show()
        else:
            for button in self.grade_buttons:
                button.hide()

    def show_answer(self, event):
        self.controller.show_answer()
            
    def grade_answer(self, event):
        grade = self.id_for_grade[event.id]
        self.controller.grade_answer(grade)
        
    def update_status_bar(self):
        db = database()
        if not self.all_cards:
            self.all_cards = db.active_count()
        self.scheduled_label.text = "S: " + str(db.scheduled_count())
        self.not_memorised_label.text = "NM: " + str(db.non_memorised_count())
        self.all_label.text = "A: " + str(self.all_cards)

