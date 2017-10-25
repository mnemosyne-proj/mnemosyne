## Copyright (c) Alexandre Delattre 2008
## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the
## "Software"), to deal in the Software without restriction, including
## without limitation the rights to use, copy, modify, merge, publish,
## distribute, sublicense, and/or sell copies of the Software, and to
## permit persons to whom the Software is furnished to do so, subject to
## the following conditions:

## The above copyright notice and this permission notice shall be
## included in all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
## MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
## NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
## LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
## OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
## WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

from .core import *
from .controls import Label
from .boxing import VBox, Spacer
from .font import Font
from .line import HLine

class DialogHeader(Frame):
    def __init__(self, parent, text):
        Frame.__init__(self, parent)
        self.label = Label(self, text, 
                           font=Font(size=8, 
                                     bold=True, 
                                     color=(0,0,255) 
                                     # XXX: Use system prefs instead of hardcoded blue
                                    )
                          )
        self.hline = HLine(self)
        sizer = VBox()
        sizer.add(Spacer(2,4))
        sizer.add(self.label, border=(4,0,0,0))
        sizer.add(Spacer(2,4))
        sizer.add(self.hline)
        self.sizer = sizer
        
    def set_text(self, text):
        self.label.set_text(text)
        
    def get_text(self):
        return self.label.get_text()