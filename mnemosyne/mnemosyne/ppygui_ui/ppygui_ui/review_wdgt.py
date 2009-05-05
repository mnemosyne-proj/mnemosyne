#
# review_wdgt.py <Peter.Bienstman@UGent.be>
#

import os
if os.name == "ce":
	import ppygui.api as gui
else:
	import emulator.api as gui

from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.component_manager import ui_controller_review
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class ReviewWdgt(gui.Frame, ReviewWidget):
    
    def __init__(self, parent):
        gui.Frame.__init__(self, parent)
       
        # Total number of cards for statusbar, to be cached.
        self.all_cards = None

        # Note: ppygui makes heavy use of properties, so we can't use e.g.
        # self.question, as the presence of self.get_question would then
        # require a function self.set_question too.
        self._question_label = gui.Label(self, "Question:")
        self._question = gui.Html(self)
        
        self._answer_label = gui.Label(self, "Answer:")
        self._answer = gui.Html(self)
        
        self.show_button = gui.Button(self, "Show answer")
        self.show_button.bind(clicked=self.show_answer)
        self.show_button_enabled = True

        self.grade_sizer = gui.HBox(border=(2, 2, 2, 2), spacing=5)
        self.grade_buttons = []
        self.id_for_grade = {}
        for i in range(6):
            button = gui.Button(self, title=3*" " + str(i) + 3*" ",
                                action=self.grade_answer)
            self.grade_buttons.append(button)
            self.id_for_grade[button._id] = i        
            self.grade_sizer.add(button)
            if i == 0:
                self.grade_0_button = button
            elif i == 4:
                self.grade_4_button = button                
        self.grade_buttons_enabled = False

        self.status_sizer = gui.HBox(spacing=10)
        self.scheduled_label = gui.Label(self)
        self.not_memorised_label = gui.Label(self)
        self.all_label = gui.Label(self)
        self.status_sizer.add(self.scheduled_label)
        self.status_sizer.add(self.not_memorised_label)
        self.status_sizer.add(self.all_label)

        sizer = gui.VBox(border=(2, 2, 2, 2))
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
        self._question.value = text

    def set_answer(self, text):
        self._answer.value = text

    def clear_question(self):
		self._question.value = ""
               
    def clear_answer(self):
		self._answer.value = ""

    def update_show_button(self, text, default, enabled):
        if default:
            self.show_button.focus()
            self.show_button.border = True
        else:
            self.show_button.border = False        
        self.show_button.text = text
        self.show_button_enabled = enabled
        # TODO: test if this works.
        self.show_button.enabled = enabled
        self.layout()

    def enable_grades(self, enabled):
        self.grade_buttons_enabled = enabled
        
    def grade_4_default(self, use_4):
        if use_4:
            self.grade_4_button.focus()
            self.grade_4_button.border = True
        else:
            self.grade_0_button.focus()
            self.grade_0_button.border = True
        self.layout()
        
    def show_answer(self, event):
        if not self.show_button_enabled:
            return
        ui_controller_review().show_answer()
           
    def grade_answer(self, event):
        if not self.grade_buttons_enabled:
            return
        grade = self.id_for_grade[event.id]
        ui_controller_review().grade_answer(grade)

    def update_status_bar(self):
        db = database()
        self.scheduled_label.text = \
            "Sch.: " + str(db.scheduled_count())
        self.not_memorised_label.text = \
            "Not mem.: " + str(db.non_memorised_count())
        if not self.all_cards:
            self.all_cards = db.active_count()
        self.all_label.text = \
            "Act.: " + str(self.all_cards)
        self.layout()
      

# Register widget.

component_manager.register(ReviewWdgt)
