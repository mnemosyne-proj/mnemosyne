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
from w32comctl import *
from config import HIRES_MULT

import datetime

ICC_DATE_CLASSES = 0x100
DTS_TIMEFORMAT = 0x9
DTM_FIRST = 0x1000
DTM_GETSYSTEMTIME = DTM_FIRST+1
DTM_SETSYSTEMTIME = DTM_FIRST+2

DTN_FIRST = 4294966536
DTN_DATETIMECHANGED = DTN_FIRST + 1

class SYSTEMTIME(Structure):
    _keys_ = [("wYear", WORD),
                ("wMonth", WORD),
                ("wDayOfWeek", WORD),
                ("wDay", WORD),
                ("wHour", WORD),
                ("wMinute", WORD),
                ("wSecond", WORD),
                ("wMilliseconds", WORD),]
    
class Date(Control):
    _w32_window_class = "SysDateTimePick32"
    _w32_window_style = WS_CHILD
    _dispatchers = {'update' : (NTFEventDispatcher, DTN_DATETIMECHANGED)}
    _dispatchers.update(Control._dispatchers)
    
    def __init__(self, *args, **kw):
        Control.__init__(self, *args, **kw)
        self._best_size = None
        
    def get_value(self):
        st = SYSTEMTIME()
        self._send_w32_msg(DTM_GETSYSTEMTIME, 0, byref(st))
        return datetime.date(st.wYear, st.wMonth, st.wDay)

    def set_value(self, date):
        st = SYSTEMTIME()
        st.wYear = date.year
        st.wMonth = date.month
        st.wDay = date.day
        self._send_w32_msg(DTM_SETSYSTEMTIME, 0, byref(st))
        
    def _get_best_size(self):
        dc = GetDC(self._w32_hWnd)
        font = self._font._hFont
        SelectObject(dc, font)
        text = self.text
        cx, cy = GetTextExtent(dc, u'dd/mm/yyyy')
        return 15+cx/HIRES_MULT, 7+cy/HIRES_MULT
        
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
            
class Time(Control):
    _w32_window_class = "SysDateTimePick32"
    _w32_window_style = WS_CHILD | DTS_TIMEFORMAT
    _dispatchers = {'update' : (NTFEventDispatcher, DTN_DATETIMECHANGED)}
    _dispatchers.update(Control._dispatchers)
    
    def __init__(self, *args, **kw):
        Control.__init__(self, *args, **kw)
        self._best_size = None
        
    def get_value(self):
        st = SYSTEMTIME()
        self._send_w32_msg(DTM_GETSYSTEMTIME, 0, byref(st))
        return datetime.time(st.wHour, st.wMinute, st.wSecond)

    def set_value(self, time):
        st = SYSTEMTIME()
        self._send_w32_msg(DTM_GETSYSTEMTIME, 0, byref(st))
        st.wHour = time.hour
        st.wMinute = time.minute
        st.wSecond = time.second
        self._send_w32_msg(DTM_SETSYSTEMTIME, 0, byref(st))
    
    def _get_best_size(self):
        dc = GetDC(self._w32_hWnd)
        font = self._font._hFont
        SelectObject(dc, font)
        text = self.text
        cx, cy = GetTextExtent(dc, u'hh:mm:ss')
        return 15+cx/HIRES_MULT, 7+cy/HIRES_MULT
    
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
                 
def _InitDateControl():
    icc = INITCOMMONCONTROLSEX()
    icc.dwSize = sizeof(INITCOMMONCONTROLSEX)
    icc.dwICC = ICC_DATE_CLASSES 
    InitCommonControlsEx(byref(icc))

_InitDateControl()
