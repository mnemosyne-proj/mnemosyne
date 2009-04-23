import sys

if sys.platform == "win32":
	import ppygui.api as gui
else:
	import mnemosyne.ppygui_ui.simulator.api as gui


class QuestionPage(gui.Frame):
	def __init__(self, parent):
		gui.Frame.__init__(self, parent)
		self.questionPrompt = gui.Label(self,"Question")
		self.answerPrompt = gui.Label(self,"Answer")
		self.question = gui.Label(self,"ExQ")
		self.question.font = gui.Font(size=14,bold=True)
		self.answer = gui.Label(self,"ExA")
		self.answer.font = gui.Font(size=14,bold=True)
		self.answerButton = gui.Button(self,"Show Answer!")
	
		cesizer = gui.VBox()
		mainSizer = gui.VBox()
		qSizer = gui.VBox();
		aSizer = gui.VBox();
		buttonsSizer = gui.HBox( border=(15,15,15,15), spacing=20 );
		self.bsizer = buttonsSizer
		self.createStatus()
		qSizer.add(self.questionPrompt)
		qSizer.add(self.question)
		aSizer.add(self.answerPrompt)
		aSizer.add(self.answer)

		self.answerbar = gui.Label(self,"Options")
		self.statusbar = gui.Label(self,"Status")
		mainSizer.add(self.questionPrompt)
		mainSizer.add(self.question)
		mainSizer.add(self.answerButton)
		mainSizer.add(self.answerPrompt)
		mainSizer.add(self.answer)
		self.statusbar.sizer = self.statusSizer

		self.answerPrompt.hide()
		self.answer.hide()



		self.answerButton.bind(clicked=self.showAnswer)
		i = 0
		while i < 6:
			gradeButton = gui.Button(self,title=str(i),border=True,action=self.gradeAnswer)
			self.bsizer.add(gradeButton)	
			i = i + 1
		#self.buttonbar.sizer = self.bsizer
		mainSizer.add(self.bsizer)
		mainSizer.add(self.statusSizer)
		self.sizer = mainSizer
		
		#item = get_new_question(False)
		item = None
		self.qid=0
		if not item == None:
			self.question.text = item.q
			self.item = item
			self.state = 0

	def showAnswer(self,event):
		if self.state == 0:
			self.state = 1
			self.answer.text = self.item.a
			self.answerPrompt.show()
			self.answer.show()
			self.answerButton.hide()
			self.update()
			self.Layout()
			self.update()

	def gradeAnswer(self,event):
		if self.state == 1:
			self.item = get_new_question()
			self.answer.text = ""
			if self.item == None:
				self.question.text ="No Questions Left"
			else:
				self.question.text = self.item.q
				self.state = 0
				self.answer.hide()
				self.answerPrompt.hide()
				self.answerButton.show()
				button = event.window
				process_answer(self.item,int(button.text))
				self.updateStatus()
				self.Layout()

	def updateStatus(self):
		self.unlearnedLabel.text = "U: " + str(non_memorised_items())
		self.queueLabel.text = "Q: " + str(scheduled_items())

	def createStatus(self):
		self.unlearnedLabel = gui.Label(self,"U: ")
		self.totalLabel = gui.Label(self,"T: " )
#		self.totalLabel.text = "T: " + str(active_items())
		self.queueLabel = gui.Label(self,"Q: ")
		self.statusSizer = gui.HBox(spacing=10);
		self.statusSizer.add(self.queueLabel)
		self.statusSizer.add(self.unlearnedLabel)
		self.statusSizer.add(self.totalLabel)
		return self.statusSizer
	
	def setQuestion(self,item):
		self.question.text = item.q
		self.Layout()

class MainFrame(gui.CeFrame):
	def __init__(self):
		gui.CeFrame.__init__(self,title="Mnemosyne PPC")
		self.qPage = QuestionPage(self)
		self.qPageSizer = gui.VBox()
		self.qPageSizer.add(self.qPage)
		self.sizer = self.qPageSizer
		self.Layout()


		

	
if __name__ == '__main__':
	app=gui.Application()
	app.mainframe = MainFrame()
	app.run()

