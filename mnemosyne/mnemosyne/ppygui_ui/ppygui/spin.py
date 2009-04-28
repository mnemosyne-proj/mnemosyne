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

from core import Frame, CustomEventDispatcher, \
    GetDC, SelectObject, GetTextExtent
from config import HIRES_MULT
from controls import Edit, UpDown
from boxing import HBox

class Spin(Frame):
    _dispatchers = {'update' : (CustomEventDispatcher,)}
    _dispatchers.update(Frame._dispatchers)
    
    def __init__(self, parent, range=(0,100), visible=True, enabled=True, **kw):
        Frame.__init__(self, parent, visible=visible, enabled=enabled)
        self._buddy = Edit(self)
        self._ud = UpDown(self)
        self._ud.buddy = self._buddy
        
        self._buddy.bind(update=self._on_edit_update)
        
        sizer = HBox(spacing=-1)
        sizer.add(self._buddy)
        sizer.add(self._ud)
        self.sizer = sizer
        self.set(range=range, **kw)
        self._best_size = None
    
    def get_value(self):
        return self._ud._get_pos()
        
    def set_value(self, val):
        if not self._low <= val <= self._high:
            raise ValueError('Invalid value retrieved by the spin control')
        self._ud._set_pos(val)    
        

    doc_value = 'The displayed int in range'
        
    def _on_edit_update(self, event):
        self.events['update'].call(None)
        
    def get_range(self):
        return self._low, self._high
        
    def set_range(self, rg):
        self._low, self._high = rg
        self._ud.range = rg
        self._best_size = None
        
    doc_range = 'The range of valid ints as a tuple (low, high)'
        
    def _get_best_size(self):
        #return self.sizer.get_best_size()
        dc = GetDC(self._w32_hWnd)
        font = self._buddy._font._hFont
        SelectObject(dc, font)
        cx, cy = GetTextExtent(dc, str(self._high))
        return 20 + cx/HIRES_MULT, 7+cy/HIRES_MULT
        
    def get_font(self):
        return Control.get_font(self)
            
    def set_font(self, value):
        Control.set_font(self, value)
        self._best_size = None
        
    def get_best_size(self):
        if self._best_size is None:
            best_size = self._get_best_size()
            self._best_size = best_size
            return best_size
        else:
            return self._best_size