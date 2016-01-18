#
# review_wdgt.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui, QtWebKit

import sys

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_review_wdgt import Ui_ReviewWdgt
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class QAOptimalSplit(object):

    """Algorithm to make sure the split between question and answer boxes is
    as optimal as possible.

    This code is not part of ReviewWidget, in order to be able to reuse this
    in Preview Cards.

    """

    used_for_reviewing = True

    def __init__(self):
        self.question.settings().setAttribute(\
            QtWebKit.QWebSettings.PluginsEnabled, True)
        self.answer.settings().setAttribute(\
            QtWebKit.QWebSettings.PluginsEnabled, True)
        # Add some dummy QWebViews that will be used to determine the actual
        # size of the rendered html. This information will then be used to
        # determine the optimal split between the question and the answer
        # pane.
        self.question_preview = QtWebKit.QWebView()
        self.question_preview.loadFinished.connect(\
            self.question_preview_load_finished)
        self.answer_preview = QtWebKit.QWebView()
        self.answer_preview.loadFinished.connect(\
            self.answer_preview_load_finished)
        # Calculate an offset to use in the stretching factor of the boxes,
        # e.g. question_box = question_label + question.
        self.stretch_offset = self.question_label.size().height()
        if self.question_box.spacing() != -1:
            self.stretch_offset += self.question_box.spacing()
        self.scrollbar_width = QtGui.QScrollBar().sizeHint().width()
        self.question_text = ""
        self.answer_text = ""
        self.required_question_size = self.question.size()
        self.required_answer_size = self.answer.size()
        self.is_answer_showing = False
        self.times_resized = 0

    def resizeEvent(self, event):
        # Update stretch factors when changing the size of the window.
        self.set_question(self.question_text)
        self.set_answer(self.answer_text)
        # To get this working the first time we start the program (in general,
        # the first one or two resize events, depending on whether or not we
        # changed the window size), we need to explicitly show the contents.
        # (Qt bug?). We don't do this on subsequent resizes to prevent flicker
        # and media replays.
        if self.times_resized < 2:
            self.reveal_question()
            if self.is_answer_showing:
                self.reveal_answer()
            self.times_resized += 1
        return QtGui.QWidget.resizeEvent(self, event)

    def question_preview_load_finished(self):
        self.required_question_size = \
            self.question_preview.page().currentFrame().contentsSize()
        self.update_stretch_factors()

    def answer_preview_load_finished(self):
        self.required_answer_size = \
            self.answer_preview.page().currentFrame().contentsSize()
        self.update_stretch_factors()

    def update_stretch_factors(self):
        total_height_available = self.question.height() + self.answer.height()
        # Correct the required heights of question and answer for the
        # presence of horizontal scrollbars.
        required_question_height = self.required_question_size.height()
        if self.required_question_size.width() > self.question.width():
            required_question_height += self.scrollbar_width
        required_answer_height = self.required_answer_size.height()
        if self.required_answer_size.width() > self.answer.width():
            required_answer_height += self.scrollbar_width
        total_height_available = self.question.height() + self.answer.height()
        # If both question and answer fit in their own boxes, there is no need
        # to deviate from a 50/50 split.
        if required_question_height < total_height_available / 2 and \
            required_answer_height < total_height_available / 2:
            question_stretch = 50
            answer_stretch = 50
        # Don't be clairvoyant about the answer size, unless we will need
        # a non 50/50 split to start with.
        # If we are only showing the question, we try to limit 'surprising',
        # 'clairvoyant' stretches if they are not needed.
        elif not self.is_answer_showing:
            if required_question_height < total_height_available / 2:
                # No need to be clairvoyant.
                question_stretch = 50
                answer_stretch = 50
            else:
                # Make enough room for the question.
                question_stretch = required_question_height
                if required_question_height + required_answer_height \
                    <= total_height_available:
                    # Already have the stretch set-up to accomodate the answer,
                    # which makes the UI more relaxed (no need to have a
                    # different non 50/50 split once the answer is shown).
                    answer_stretch = required_answer_height
                else:
                    # But if we don't have enough space to show both the
                    # question and the answer, make sure the question gets
                    # all the space it can get now.
                    answer_stretch = 50
        # We are showing both question and answer.
        else:
            answer_stretch = required_answer_height
            if required_question_height + required_answer_height \
                    <= total_height_available:
                # If we have enough space, stretch in proportion to height.
                question_stretch = required_question_height
            else:
                # If we are previewing cards, go for a 50/50 split.
                if not self.used_for_reviewing:
                    question_stretch = 50
                    answer_stretch = 50
                # If we don't have enough space to show both the question and
                # the answer, try to give the answer all the space it needs.
                else:
                    answer_stretch = required_answer_height
                    question_stretch = total_height_available - answer_stretch
                    if question_stretch < 50:
                        question_stretch = 50        
        self.vertical_layout.setStretchFactor(\
            self.question_box, question_stretch + self.stretch_offset)
        self.vertical_layout.setStretchFactor(\
            self.answer_box, answer_stretch + self.stretch_offset)

    def silence_media(self, text):
        # Silence media, but make sure the player widget still shows to get
        # correct information about the geometry.
        text = text.replace("var soundFiles = new Array(",
                            "var soundFiles = new Array('off',")
        text = text.replace("<audio src=\"", "<audio src=\"off")
        text = text.replace("<video src=\"", "<video src=\"off")
        return text

    def set_question(self, text):
        #self.main_widget().show_information(text.replace("<", "&lt;"))
        self.question_text = text
        self.question_preview.page().setPreferredContentsSize(\
            QtCore.QSize(self.question.size().width(), 1))
        self.question_preview.setHtml(self.silence_media(text))

    def set_answer(self, text):
        #self.main_widget().show_information(text.replace("<", "&lt;"))        
        self.answer_text = text
        self.answer_preview.page().setPreferredContentsSize(\
            QtCore.QSize(self.answer.size().width(), 1))
        self.answer_preview.setHtml(self.silence_media(text))

    def reveal_question(self):
        self.question.setHtml(self.question_text)

    def reveal_answer(self):
        self.is_answer_showing = True
        self.update_stretch_factors()
        self.answer.setHtml(self.answer_text)

    def clear_question(self):
        self.question.setHtml(self.empty())

    def clear_answer(self):
        self.is_answer_showing = False
        self.update_stretch_factors()
        self.answer.setHtml(self.empty())



class ReviewWdgt(QtGui.QWidget, QAOptimalSplit, Ui_ReviewWdgt, ReviewWidget):

    auto_focus_grades = True
    number_keys_show_answer = True

    key_to_grade_map = {QtCore.Qt.Key_QuoteLeft: 0, QtCore.Qt.Key_0: 0,
            QtCore.Qt.Key_1: 1, QtCore.Qt.Key_2: 2, QtCore.Qt.Key_3: 3,
            QtCore.Qt.Key_4: 4, QtCore.Qt.Key_5: 5}
     
    def __init__(self, component_manager):
        ReviewWidget.__init__(self, component_manager)
        parent = self.main_widget()
        QtGui.QWidget.__init__(self, parent)
        parent.setCentralWidget(self)
        self.setupUi(self)
        # TODO: move this to designer with update of PyQt.
        self.grade_buttons = QtGui.QButtonGroup()
        self.grade_buttons.addButton(self.grade_0_button, 0)
        self.grade_buttons.addButton(self.grade_1_button, 1)
        self.grade_buttons.addButton(self.grade_2_button, 2)
        self.grade_buttons.addButton(self.grade_3_button, 3)
        self.grade_buttons.addButton(self.grade_4_button, 4)
        self.grade_buttons.addButton(self.grade_5_button, 5)
        self.grade_buttons.buttonClicked[int].connect(self.grade_answer)
        # TODO: remove this once Qt bug is fixed.
        self.setTabOrder(self.grade_1_button, self.grade_2_button)
        self.setTabOrder(self.grade_2_button, self.grade_3_button)
        self.setTabOrder(self.grade_3_button, self.grade_4_button)
        self.setTabOrder(self.grade_4_button, self.grade_5_button)
        self.setTabOrder(self.grade_5_button, self.grade_0_button)
        self.setTabOrder(self.grade_0_button, self.grade_1_button)
        self.focus_widget = None
        self.sched = QtGui.QLabel("", parent.status_bar)
        self.notmem = QtGui.QLabel("", parent.status_bar)
        self.act = QtGui.QLabel("", parent.status_bar)
        parent.clear_status_bar()
        parent.add_to_status_bar(self.sched)
        parent.add_to_status_bar(self.notmem)
        parent.add_to_status_bar(self.act)
        parent.status_bar.setSizeGripEnabled(0)
        self.widget_with_last_selection = self.question
        self.question.selectionChanged.connect(self.selection_changed_in_q)
        self.answer.selectionChanged.connect(self.selection_changed_in_a)
        QAOptimalSplit.__init__(self) 
        self.mplayer = QtCore.QProcess()
        self.media_queue = []
        
    def deactivate(self):
        self.stop_media()

    def changeEvent(self, event):
        if hasattr(self, "show_button"):
            show_button_text = self.show_button.text()
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUi(self)
        # retranslateUI resets the show button text to 'Show answer',
        # so we need to work around this.
        if hasattr(self, "show_button"):
            self.show_button.setText(_(show_button_text))
        QtGui.QWidget.changeEvent(self, event)

    def keyPressEvent(self, event):
        if event.key() in self.key_to_grade_map and not event.isAutoRepeat():
            # Use controller function rather than self.is_answer_showing to
            # deal with the map card type.
            if self.review_controller().is_question_showing():
                if self.number_keys_show_answer:
                    self.show_answer()
            else:
                self.grade_answer(self.key_to_grade_map[event.key()])   
        elif event.key() == QtCore.Qt.Key_PageDown:
            self.scroll_down()
        elif event.key() == QtCore.Qt.Key_PageUp:
            self.scroll_up()
        elif event.key() == QtCore.Qt.Key_R and \
            event.modifiers() == QtCore.Qt.ControlModifier:
            self.review_controller().update_dialog(redraw_all=True) # Replay media.
        elif event.key() == QtCore.Qt.Key_C and \
            event.modifiers() == QtCore.Qt.ControlModifier:
            self.copy()
        # Work around Qt issue.
        elif event.key() in [QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete]:
            self.controller().delete_current_card()
        else:
            QtGui.QWidget.keyPressEvent(self, event)

    def empty(self):
        background = self.palette().color(QtGui.QPalette.Base).name()
        if self.review_controller().card:
            colour = self.config().card_type_property(\
            "background_colour", self.review_controller().card.card_type)
            if colour:
                background = ("%X" % colour)[2:] # Strip alpha.
        return """
        <html><head>
        <style type="text/css">
        table { height: 100%; }
        body  { background-color: """ + background + """;
                margin: 0;
                padding: 0;
                border: thin solid #8F8F8F; }
        </style></head>
        <body><table><tr><td>
        </td></tr></table></body></html>"""

    def scroll_down(self):
        if self.review_controller().is_question_showing() or \
           self.review_controller().card.fact_view.a_on_top_of_q:
            frame = self.question.page().mainFrame()
        else:
            frame = self.answer.page().mainFrame()
        x, y = frame.scrollPosition().x(), frame.scrollPosition().y()
        y += int(0.9*(frame.geometry().height()))
        #frame.scroll(x, y) # Seems buggy 20111121.
        frame.evaluateJavaScript("window.scrollTo(%d, %d);" % (x, y))

    def scroll_up(self):
        if self.review_controller().is_question_showing() or \
           self.review_controller().card.fact_view.a_on_top_of_q:
            frame = self.question.page().mainFrame()
        else:
            frame = self.answer.page().mainFrame()
        x, y = frame.scrollPosition().x(), frame.scrollPosition().y()
        y -= int(0.9*(frame.geometry().height()))
        #frame.scroll(x, y)  # Seems buggy 20111121.
        frame.evaluateJavaScript("window.scrollTo(%d, %d);" % (x, y))
        
    def selection_changed_in_q(self):
        self.widget_with_last_selection = self.question
        
    def selection_changed_in_a(self):
        self.widget_with_last_selection = self.answer
        
    def copy(self):
        self.widget_with_last_selection.pageAction(\
            QtWebKit.QWebPage.Copy).trigger()

    def show_answer(self):     
        self.review_controller().show_answer()

    def grade_answer(self, grade):
        self.vertical_layout.setStretchFactor(self.question_box, 50)
        self.vertical_layout.setStretchFactor(self.answer_box, 50)
        self.review_controller().grade_answer(grade)

    def set_question_box_visible(self, is_visible):
        if is_visible:
            self.question.show()
            self.question_label.show()
        else:
            self.question.hide()
            self.question_label.hide()

    def set_answer_box_visible(self, is_visible):
        if is_visible:
            self.answer.show()
            self.answer_label.show()
        else:
            self.answer.hide()
            self.answer_label.hide()

    def set_question_label(self, text):
        self.question_label.setText(text)

    def restore_focus(self):
        # After clicking on the question or the answer, that widget grabs the
        # focus, so that the keyboard shortcuts no longer work. This functions
        # is used to set the focus back to the correct widget.
        if self.focus_widget:
            self.focus_widget.setDefault(True)
            self.focus_widget.setFocus()

    def update_show_button(self, text, is_default, is_enabled):
        self.show_button.setText(text)
        self.show_button.setEnabled(is_enabled)
        if is_default:
            self.show_button.setDefault(True)
            self.show_button.setFocus()
            self.focus_widget = self.show_button

    def set_grades_enabled(self, is_enabled):
        self.grades.setEnabled(is_enabled)

    def set_grade_enabled(self, grade, is_enabled):
        self.grade_buttons.button(grade).setEnabled(is_enabled)

    def set_default_grade(self, grade):
        if self.auto_focus_grades:
            # On Windows, we seem to need to clear the previous default
            # first.
            for grade_i in range(6):
                self.grade_buttons.button(grade_i).setDefault(False)
            self.grade_buttons.button(grade).setDefault(True)
            self.grade_buttons.button(grade).setFocus()
            self.focus_widget = self.grade_buttons.button(grade)

    def set_grades_title(self, text):
        self.grades.setTitle(text)

    def set_grade_text(self, grade, text):
        self.grade_buttons.button(grade).setText(text)

    def set_grade_tooltip(self, grade, text):
        self.grade_buttons.button(grade).setToolTip(text)

    def update_status_bar_counters(self):
        scheduled_count, non_memorised_count, active_count = \
            self.review_controller().counters()
        self.sched.setText(_("Scheduled: %d ") % scheduled_count)
        self.notmem.setText(_("Not memorised: %d ") % non_memorised_count)
        self.act.setText(_("Active: %d ") % active_count)
        
    def play_media(self, filename, start=None, stop=None):
        if start is None:
            start = 0
        if stop is None:
            stop = 999999
        self.media_queue.append((filename, start, stop))
        if self.mplayer.state() != QtCore.QProcess.Running:
            self.play_next_file()
            
    def play_next_file(self):
        filename, start, stop = self.media_queue.pop(0)
        duration = stop - start
        if duration > 400:
            duration -= 300 # Compensate for mplayer overshoot. 
        self.mplayer = QtCore.QProcess()
        self.mplayer.finished.connect(self.done_playing)
        if sys.platform == "win32":            
            command = "mplayer.exe -slave -ao win32 -quiet \"" + filename + \
                "\" -ss " + str(start) + " -endpos " + str(duration) 
        elif sys.platform == "darwin":
            command = "./mplayer -slave -ao coreaudio -quiet \"" + filename + \
                "\" -ss " + str(start) + " -endpos " + str(duration)
        else:
            command = "mplayer -slave -quiet \"" + filename + \
                "\" -ss " + str(start) + " -endpos " + str(duration)
        self.mplayer.start(command)
            
    def done_playing(self, result):
        if len(self.media_queue) >= 1:
            self.play_next_file()
        
    def stop_media(self):
        if self.mplayer is not None:
            self.mplayer.write("quit\n");
        self.media_queue = []

    def redraw_now(self):
        self.repaint()
        self.parent().repaint()
