#
# callback.py <Peter.Bienstman@UGent.be>
#

import libstarpy

SrvGroup = libstarpy._GetSrvGroup()
Service = SrvGroup._GetService("","")

class Callback:
	
	"""Class to handle callbacks to Javascript."""
	
	def set_callback(self, _callback):
		self.callback = _callback

	def makeToast(self, activity):
		AbsoluteLayout = Service._ImportRawContext(\
		    "java","android/widget/AbsoluteLayout",True,""); 
		print AbsoluteLayout
		activity.printStr("Big success")
		#activity = Service._ImportRawContext(\
		#		    "java","org/mnemosyne/MnemosyneActivity",True,"");		
		#self.callback(message)
		
#callback = Callback()

class Driver:
	
	def __init__(self):
		self.callback = Callback()
		
	def drive(self, activity):
		self.callback.makeToast(activity)
		
driver = Driver()