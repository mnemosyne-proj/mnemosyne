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

class Message(object):
    
    @classmethod
    def _makeiconstyle(cls, icon):
        assert icon in ['info', 'question', 'warning', 'error']
        if icon == 'info' :
            return MB_ICONASTERISK
        elif icon == 'question':
            return MB_ICONQUESTION
        elif icon == 'warning':
            return MB_ICONWARNING
        elif icon == 'error':
            return MB_ICONERROR
    
    @classmethod
    def _messagebox(cls, title, caption, style, parent=None):
        if not parent :
            hwnd = 0
        else :
            hwnd = parent._w32_hWnd
            
        return MessageBox(hwnd, str(caption), str(title), style)
        
    @classmethod
    def ok(cls, title, caption, icon='info', parent=None):
        style = MB_OK
        style |= cls._makeiconstyle(icon)
        cls._messagebox(title, caption, style, parent)
        return 'ok'
        
    @classmethod
    def okcancel(cls, title, caption, icon='info', parent=None):
        style = MB_OKCANCEL
        style |= cls._makeiconstyle(icon)
        res = cls._messagebox(title, caption, style, parent)
        if res == IDOK :
            return 'ok'
        else :
            return 'cancel'
    
    @classmethod        
    def yesno(cls, title, caption, icon='info', parent=None):
        style = MB_YESNO
        style |= cls._makeiconstyle(icon)
        res = cls._messagebox(title, caption, style, parent)
        if res == IDYES :
            return 'yes'
        else : 
            return 'no'
        
    @classmethod        
    def yesnocancel(cls, title, caption, icon='info', parent=None):
        style = MB_YESNOCANCEL
        style |= cls._makeiconstyle(icon)
        res = cls._messagebox(title, caption, style, parent)
        if res == IDYES :
            return 'yes'
        elif res == IDNO : 
            return 'no'
        else :
            return 'cancel'
