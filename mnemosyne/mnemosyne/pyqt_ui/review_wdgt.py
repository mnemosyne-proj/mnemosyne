#
# review_wdgt.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_review_wdgt import Ui_ReviewWdgt
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget

def determine_stretch_factor(page):

    """Approximate algorithm to make sure the split between question and
    answer boxes is as optimal as possible.

    Ideally, we would need the total height in pixels of the complete rendered
    page, not counting the borders, but doing so seems impossible or buggy in
    Qt. Instead, we make a simpler estimate based on the height of the
    pictures in the page and an estimate of the text size provided by the
    renderer..

    This code is not part of ReviewWidget, in order to be able to reuse this
    in Preview Cards.
    
    """

    # Estimate for images.
    images = page.mainFrame().findAllElements("img")
    viewport_width = page.viewportSize().width()
    running_width = 0
    stretch = 0
    for image in images:
        running_width += image.geometry().width()
        if running_width < viewport_width:
            stretch = max(stretch, image.geometry().height())
        else:
            stretch += image.geometry().height()
            running_width = 0
    # Estimate for text.
    stretch += int(page.mainFrame().\
        findFirstElement("text_size_estimate").attribute("value"))   
    if stretch < 50:
        stretch = 50
    return stretch
    
        
class ReviewWdgt(QtGui.QWidget, Ui_ReviewWdgt, ReviewWidget):

    auto_focus_grades = True
    
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
        self.focus_widget = None
        self.sched = QtGui.QLabel("", parent.status_bar)
        self.notmem = QtGui.QLabel("", parent.status_bar)
        self.act = QtGui.QLabel("", parent.status_bar)
        parent.clear_status_bar()
        parent.add_to_status_bar(self.sched)
        parent.add_to_status_bar(self.notmem)
        parent.add_to_status_bar(self.act)
        parent.status_bar.setSizeGripEnabled(0)
        # Since the images are loaded lazily, we can only determine the
        # stretch factors after the images have been loaded.
        self.question.loadFinished.connect(self.question_load_finished)
        self.answer.loadFinished.connect(self.answer_load_finished)
        
    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUi(self)
        QtGui.QWidget.changeEvent(self, event)

    def keyPressEvent(self, event):
        if not event.isAutoRepeat() and event.key() in \
            [QtCore.Qt.Key_0, QtCore.Qt.Key_1, QtCore.Qt.Key_2,
            QtCore.Qt.Key_3, QtCore.Qt.Key_4, QtCore.Qt.Key_5] and \
            self.review_controller().state == "SELECT SHOW":
                self.show_answer()
        elif event.key() == QtCore.Qt.Key_PageDown:
            self.scroll_down()
        elif event.key() == QtCore.Qt.Key_PageUp:
            self.scroll_up()
        elif event.key() == QtCore.Qt.Key_R and \
            event.modifiers() == QtCore.Qt.ControlModifier:
            self.review_controller().update_dialog(redraw_all=True) # Replay media.
        else:
            QtGui.QWidget.keyPressEvent(self, event)

    def empty(self):
        background = "white"
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
        <body><table><tr><td><text_size_estimate value=\"0\">
        </td></tr></table></body></html>"""

    def scroll_down(self):
        if self.review_controller().state == "SELECT SHOW":
            frame = self.question.page().mainFrame()
        else:
            frame = self.answer.page().mainFrame()   
        x, y = frame.scrollPosition().x(), frame.scrollPosition().y()
        y += int(0.9*(frame.geometry().height()))
        #frame.scroll(x, y) # Seems buggy 20111121.
        frame.evaluateJavaScript("window.scrollTo(%d, %d);" % (x, y))
        
    def scroll_up(self):
        if self.review_controller().state == "SELECT SHOW":
            frame = self.question.page().mainFrame()
        else:
            frame = self.answer.page().mainFrame()   
        x, y = frame.scrollPosition().x(), frame.scrollPosition().y()
        y -= int(0.9*(frame.geometry().height()))
        #frame.scroll(x, y)  # Seems buggy 20111121.
        frame.evaluateJavaScript("window.scrollTo(%d, %d);" % (x, y))
        
    def show_answer(self):
        self.review_controller().show_answer()

    def grade_answer(self, grade):
        self.vertical_layout.setStretchFactor(self.question_box, 1)
        self.vertical_layout.setStretchFactor(self.answer_box, 1)            
        self.main_widget().timer_1.start(self.main_widget().TIMER_1_INTERVAL)
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

    def set_question(self, text):        
        self.question.setHtml(text)
            
    def set_answer(self, text):
        self.answer.setHtml(text)      
        
    def question_load_finished(self):
        stretch = determine_stretch_factor(self.question.page())
        self.vertical_layout.setStretchFactor(self.question_box, stretch)
        
    def answer_load_finished(self):
        stretch = determine_stretch_factor(self.answer.page())
        self.vertical_layout.setStretchFactor(self.answer_box, stretch)
                     
    def clear_question(self):
        self.question.setHtml(self.empty())
        
    def clear_answer(self):
        self.answer.setHtml(self.empty())

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

    def redraw_now(self):
        self.repaint()        
        self.parent().repaint()
