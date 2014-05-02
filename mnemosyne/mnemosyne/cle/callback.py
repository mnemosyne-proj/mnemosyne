#
# callback.py <Peter.Bienstman@UGent.be>
#


class Callback:
	
	"""Class to handle callbacks to Javascript."""
	
	def set_callback(self, callback):
		self.callback = callback

	def make_toast(self, message):
		self.callback(message)
		
callback = Callback()