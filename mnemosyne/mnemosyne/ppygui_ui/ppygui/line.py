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

from core import *

class HLine(Window):
    def __init__(self, parent):
        Window.__init__(self, parent)
        self.bind(paint=self.on_paint)
        
    def on_paint(self, event):
        ps = PAINTSTRUCT()
        hdc = BeginPaint(self._w32_hWnd, byref(ps))
        rc = self.client_rect
        r, b =  rc.right, rc.bottom
        hpen = CreatePen(0, 2, 0)
        SelectObject(hdc, hpen)
        line = (POINT*2)()
        line[0].x = 0
        line[0].y = b/2
        line[1].x = r
        line[1].y = b/2
        
        Polyline(hdc, line, 2)
        EndPaint(self._w32_hWnd, byref(ps))
        
    def get_best_size(self):
        return None, 1
        
class VLine(Window):
    def __init__(self, parent):
        Window.__init__(self, parent)
        self.bind(paint=self.on_paint)
        
    def on_paint(self, event):
        ps = PAINTSTRUCT()
        hdc = BeginPaint(self._w32_hWnd, byref(ps))
        rc = self.client_rect
        r, b =  rc.right, rc.bottom
        hpen = CreatePen(0, 2, 0)
        SelectObject(hdc, hpen)
        
        line = (POINT*2)()
        line[0].x = r/2
        line[0].y = 0
        line[1].x = r/2
        line[1].y = b
        
        Polyline(hdc, line, 2)
        EndPaint(self._w32_hWnd, byref(ps))
        DeleteObject(hpen)
        
    def get_best_size(self):
        return 1, None