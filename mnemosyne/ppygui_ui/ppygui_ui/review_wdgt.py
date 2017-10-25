#
# review_wdgt.py <Peter.Bienstman@UGent.be>
#

import os
if os.name == "ce":
        import ppygui.api as gui
else:
        import mnemosyne.ppygui_ui.emulator.api as gui

from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class ReviewWdgt(gui.Frame, ReviewWidget):

    def __init__(self, component_manager):
        ReviewWidget.__init__(self, component_manager)
        parent = self.main_widget()
        gui.Frame.__init__(self, parent)
        parent.set_central_widget(self)

        # Note: ppygui makes heavy use of properties, so we can't use e.g.
        # self.question, as the presence of self.question would then
        # require a function self.set_question too.
        self._question_label = gui.Label(self, "Question:")
        self._question = gui.Html(self)

        self._answer_label = gui.Label(self, "Answer:")
        self._answer = gui.Html(self)

        self.show_button = gui.Button(self, "Show answer")
        self.show_button.bind(clicked=self.show_answer)
        self.is_show_button_enabled = True

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
        self.is_grade_buttons_enabled = False

        self.status_bar = gui.Label(self)

        sizer = gui.VBox(border=(2, 2, 2, 2))
        sizer.add(self._question_label)
        sizer.add(self._question)
        sizer.add(self._answer_label)
        sizer.add(self._answer)
        sizer.add(self.show_button)
        sizer.add(self.grade_sizer)
        sizer.add(self.status_bar)        
        self.sizer = sizer
        self._question_text = ""
        self._answer_text = ""

        def show_answer(self, event):
                if not self.is_show_button_enabled:
                        return
                self.review_controller().show_answer()

        def grade_answer(self, event):
                if not self.is_grade_buttons_enabled:
                        return
                grade = self.id_for_grade[event.id]
                self.review_controller().grade_answer(grade)

        def set_question_box_visible(self, is_visible):
                if is_visible:
                        self._question_label.show()
                        self._question.show()
                else:
                        self._question_label.hide()
                        self._question.hide()

        def set_answer_box_visible(self, is_visible):
                if is_visible:
                        self._answer_label.show()
                        self._answer.show()
                else:
                        self._answer_label.hide()
                        self._answer.hide()

        def set_question_label(self, text):
                self._question_label.text = text

        def set_question(self, text):
                self._question_text = text

        def set_answer(self, text):
                self._answer_text = text

        def reveal_question(self, text):
                self._question.value = self._question_text

        def reveal_answer(self, text):
                self._answer.value = self._answer_text

        def clear_question(self):
                self._question.value = ""

        def clear_answer(self):
                self._answer.value = ""

        def update_show_button(self, text, is_default, is_enabled):
                if is_default:
                        self.show_button.focus()
                self.show_button.text = text
                self.is_show_button_enabled = is_enabled

        def set_grades_enabled(self, is_enabled):
                self.is_grade_buttons_enabled = is_enabled

        def set_default_grade(self, grade):
                self.grade_buttons[grade].focus()

        def update_status_bar_counters(self):
                scheduled_count, non_memorised_count, active_count = \
                        self.review_controller().counters()
                self.status_bar.text = "Sch.:%d Not mem.:%d Act.:%d" % \
                        (scheduled_count, non_memorised_count, active_count)

