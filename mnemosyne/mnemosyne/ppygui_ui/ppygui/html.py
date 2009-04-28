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
from ctypes import cdll, Structure, Union

DTM_ADDTEXTW = WM_USER+102
DTM_ENDOFSOURCE = WM_USER + 104
DTM_NAVIGATE = WM_USER + 120
DTM_ZOOMLEVEL = WM_USER + 116
DTM_CLEAR = WM_USER + 113
DTM_ENABLESHRINK = WM_USER + 107
DTM_ENABLECONTEXTMENU = WM_USER + 110

class _U_NM_HTMLVIEW(Union):
    _fields_ = [('dwCookie', DWORD),
                ('dwFlags', DWORD)
                ]
                
class NM_HTMLVIEW(Structure):
    _fields_ = [('hdr', NMHDR),
                ('szTarget', LPCTSTR),
                ('szData', LPCTSTR),
                ('_u', _U_NM_HTMLVIEW),
                ('szExInfo', LPCTSTR),
                ]
    _anonymous_ = ('_u',)

NM_BEFORENAVIGATE = WM_USER + 109

class BeforeNavigateEvent(NotificationEvent):
    def __init__(self, hwnd, nmsg, wparam, lparam):
        NotificationEvent.__init__(self, hwnd, nmsg, wparam, lparam)
        nmhtml = NM_HTMLVIEW.from_address(lparam)
        self._url = nmhtml.szTarget
        
    def get_url(self):
        return self._url
    
class Html(Control):
    _w32_window_class = "DISPLAYCLASS"
    _dispatchers = {"navigate" : (NTFEventDispatcher, NM_BEFORENAVIGATE, BeforeNavigateEvent)
                    }
    _dispatchers.update(Control._dispatchers)
    
    def _addtext(self, txt, plain=False):
        txt=unicode(txt)
        self._send_w32_msg(DTM_ADDTEXTW, int(plain), txt)
        
    def _endofsource(self):
        self._send_w32_msg(DTM_ENDOFSOURCE)
    
    def navigate(self, url):
        url = unicode(url)
        self._send_w32_msg(DTM_NAVIGATE, 0, url)
        
    def set_zoom_level(self, level):
        if not level in range(5):
            raise TypeError, 'level must be in [0,1,2,3,4]'
        self._send_w32_msg(DTM_ZOOMLEVEL, 0, level)
        
    def set_value(self, html):
        self.clear()
        self._addtext(html)
        self._endofsource()
        
    def set_text(self, txt):
        self.clear()
        self._addtext(txt, True)
        self._endofsource()
    
    def clear(self):
        self._send_w32_msg(DTM_CLEAR)
        
    def enablecontextmenu(self, val=True):
        self._send_w32_msg(DTM_ENABLECONTEXTMENU, 0,  MAKELPARAM(0,int(val)))
        
    def enableshrink(self, val=True):
        self._send_w32_msg(DTM_ENABLESHRINK, 0,  MAKELPARAM(0,int(val))) 
    
def _InitHTMLControl():
    cdll.htmlview.InitHTMLControl(GetModuleHandle(0))
    
_InitHTMLControl()