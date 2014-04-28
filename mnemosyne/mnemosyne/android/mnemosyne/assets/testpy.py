import os

class Class1:

	def setCallBack(self, callback1, callback2):
		self.callback1 = callback1
		self.callback2 = callback2

	def postExec(self):
		print("hello from Python, trying callback")
		self.callback1()
		
	def getNum(self, input):
		print("hello 2 from Python, trying callback")
		# was 123 456, 479
		input = (input[0]+1, input[1]+1)
		#print("Python" + str(input) + str(input.type))
		output = self.callback2(input)
		#print (output, output.type)
		return output+1

class1 = Class1()

		
def tt(a,b) :
    print(a,b)
    return 666,777
g1 = 123

def yy(a,b,z) :
    print(a,b,z)
    return {'jack': 4098, 'sape': 4139}

class Multiply :
    def __init__(self,x,y) :
        self.a = x
        self.b = y
    
    def multiply(self,a,b):
        print("multiply....",self,a,b)
        return a * b