import os

if os.name == "ce":
	import ppygui.api as gui
else:
	import simulator.api as gui

from mnemosyne.libmnemosyne import initialise_user_plugins
from mnemosyne.libmnemosyne.exceptions import MnemosyneError
from mnemosyne.libmnemosyne.component_manager import config, database
from mnemosyne.libmnemosyne.component_manager import ui_controller_main
from mnemosyne.libmnemosyne.component_manager import ui_controller_review
from mnemosyne.libmnemosyne.review_widget import ReviewWidget

class ReviewWdgt(gui.Frame, ReviewWidget):
    
    def __init__(self, parent=None):
        gui.Frame.__init__(self, parent)
        self.controller = ui_controller_review()
        
        #self.questionPrompt = gui.Label(self, "Question")
        self.question = gui.Html(self)
        self.question.font = gui.Font(size=14)
        #self.answerPrompt = gui.Label(self, "Answer")
        self.answer = gui.Html(self)
        self.answer.font = gui.Font(size=14)
        self.answerButton = gui.Button(self, "Show answer")
	
        cesizer = gui.VBox()
        mainSizer = gui.VBox()
        qSizer = gui.VBox()
        aSizer = gui.VBox()
        buttonsSizer = gui.HBox(border=(15, 15, 15, 15), spacing=20)
        self.bsizer = buttonsSizer
        self.createStatus()
        #qSizer.add(self.questionPrompt)
        qSizer.add(self.question)
        #aSizer.add(self.answerPrompt)
        aSizer.add(self.answer)

        #self.answerbar = gui.Label(self, "Options")
        self.statusbar = gui.Label(self, "Status")
        #mainSizer.add(self.questionPrompt)
        mainSizer.add(self.question)
        mainSizer.add(self.answerButton)
        #mainSizer.add(self.answerPrompt)
        mainSizer.add(self.answer)
        self.statusbar.sizer = self.statusSizer

        #self.answerPrompt.hide()
        self.answer.hide()

        self.answerButton.bind(clicked=self.controller.show_answer())
        i = 0
        while i < 6:
            gradeButton = gui.Button(self, title=str(i), border=True,
                                     action=self.controller.grade_answer)
            self.bsizer.add(gradeButton)	
            i = i + 1
        #self.buttonbar.sizer = self.bsizer
        mainSizer.add(self.bsizer)
        mainSizer.add(self.statusSizer)
        self.sizer = mainSizer

    def update_status_bar(self):
        db = database()
        self.queueLabel.text = "S: " + str(db.scheduled_count())
        self.unlearnedLabel.text = "N: " + str(db.non_memorised_count())
        self.totalLabel.text = "A: " + str(db.active_count()) # TODO: cache this
        
    def createStatus(self):
        self.unlearnedLabel = gui.Label(self, "N: ")
        self.totalLabel = gui.Label(self, "A: " )
        self.queueLabel = gui.Label(self, "S: ")
        self.statusSizer = gui.HBox(spacing=10);
        self.statusSizer.add(self.queueLabel)
        self.statusSizer.add(self.unlearnedLabel)
        self.statusSizer.add(self.totalLabel)
        return self.statusSizer
    
    def set_question_label(self, text):
        print "TODO category label"
        self.Layout()
        
    def set_question(self, text):
		self.question.value = text
		self.Layout()

    def set_answer(self, text):
		self.answer.value = text
		self.Layout()
        
    def clear_answer(self):
		self.answer.value = ""
		self.Layout()

    def enable_grades(self, text):
        print "TODO enable grades"    
        
class MainFrame(gui.CeFrame):
    
    def __init__(self, filename=None):
        gui.CeFrame.__init__(self, title="Mnemosyne")
        self.review_widget = ReviewWdgt(self)
        self.review_widget_sizer = gui.VBox()
        self.review_widget_sizer.add(self.review_widget)
        self.sizer = self.review_widget_sizer
        self.Layout()

        try:
            initialise_user_plugins()
        except MnemosyneError, e:
            self.error_box(e)
        if filename == None:
            filename = config()["path"]
        try:
            database().load(filename)
        except MnemosyneError, e:
            self.error_box(e)
            self.error_box(LoadErrorCreateTmp())
            filename = os.path.join(os.path.split(filename)[0],"___TMP___" \
                                    + database().suffix)
            database().new(filename)
        ui_controller_main().widget = self
        self.update_review_widget()
        ui_controller_review().new_question()

    def update_review_widget(self):
        ui_controller_review().widget = self.review_widget

    def update_status_bar(self):
        self.review_widget.update_status_bar()
        
                              
if __name__ == '__main__':
	app = gui.Application()
	app.mainframe = MainFrame()
	app.run()

