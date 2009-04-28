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

from w32api import *
from config import HIRES

CreateFontIndirect=windll.coredll.CreateFontIndirectW

class LOGFONT(Structure):
    _fields_ = [("lfHeight", LONG),
                ("lfWidth", LONG),                
                ("lfEscapement", LONG),
                ("lfOrientation", LONG),
                ("lfWeight", LONG),
                ("lfItalic", BYTE),
                ("lfUnderline", BYTE),
                ("lfStrikeOut", BYTE),
                ("lfCharSet", BYTE),
                ("lfOutPrecision", BYTE),
                ("lfClipPrecision", BYTE),
                ("lfQuality", BYTE), 
                ("lfPitchAndFamily", BYTE),
                ("lfFaceName", TCHAR * 32)]

def rgb(r, g, b):
    return r+(g<<8)+(b<<16)
    
class Font(object):
        
    def __init__(self, name="Tahoma", size=9, bold=False, italic=False, color=(0,0,0), underline=False):
        
        height = int(-size*96/72.0)
        if HIRES :
            height *= 2
            
        lf = LOGFONT()
        lf.lfHeight = height
        lf.lfFaceName = name
        if bold :
            lf.lfWeight = 700
        if italic :
            lf.lfItalic = 1
        if underline :
            lf.lfUnderline = 1
        
        self._hFont = CreateFontIndirect(byref(lf))
        self._color = rgb(*color)
        
    def __del__(self):
        DeleteObject(self._hFont)
        
DefaultFont = Font(size=8)
ButtonDefaultFont = Font(size=8, bold=True)