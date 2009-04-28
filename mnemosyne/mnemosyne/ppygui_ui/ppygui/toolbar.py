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

from ppygui.core import *
from ppygui.w32comctl import *

SHLoadDIBitmap = windll.coredll.SHLoadDIBitmap
SHLoadDIBitmap.argtypes = [LPWSTR]
TBSTATE_ENABLED = 0x4
CCS_NOPARENTALIGN = 0x8

class BITMAP(Structure):
    _fields_ = [("bmType", LONG),
    		("bmWidth", LONG),
    		("bmHeight", LONG),
    		("bmWidthBytes", LONG),
    		("bmPlanes", WORD),
    		("bmBitsPixel", WORD),
    		("bmBits", LPVOID)]
            
class TBADDBITMAP(Structure):
    _fields_ = [('hInst', HINSTANCE),
                ('nID', INT),]
                
class ToolBar(Window):
    _w32_window_class = "ToolbarWindow32"
    _w32_window_style = WS_CHILD | WS_VISIBLE | CCS_NOPARENTALIGN
                
    def __init__(self, *args, **kw):
        Window.__init__(self, *args, **kw)
        self._buttons = []
            
    def add_bitmap(self, path, n=1):
        hbmp = SHLoadDIBitmap(path)
        tbab = TBADDBITMAP(NULL, hbmp)
        self._send_w32_msg(TB_ADDBITMAP, n, byref(tbab))
        
    def add_standard_bitmaps(self):
        tbab = TBADDBITMAP(0xFFFFFFFF, 0)
        self._send_w32_msg(TB_ADDBITMAP, 1, byref(tbab))
        
    def add_button(self, image=0, enabled=True, style='button', action=None):
        tbb = TBBUTTON()
        tbb.iBitmap = image
        if enabled:
            tbb.fsState |= TBSTATE_ENABLED
        if style == 'check':
            tbb.fsStyle = 0x2
        elif style == 'group':
            tbb.fsStyle = 0x2|0x4
        elif style == 'separator':
            tbb.fsStyle = 0x1
        elif style != 'button':
            raise ValueError("%s is not a valid style" %style)
        
        id = IdGenerator.next()
        tbb.idCommand = id
        self._send_w32_msg(TB_BUTTONSTRUCTSIZE, sizeof(TBBUTTON))
        self._send_w32_msg(TB_ADDBUTTONS, 1, byref(tbb))
        button = ToolBarButton(self, id)
        if action is not None:
            button.bind(action)
        self._buttons.append(button)
        
    def get_count(self):
        return len(self._buttons)
        
    def __getitem__(self, i):
        return self._buttons[i]
        
    def __delitem__(self, i):
        if not 0 <= i < self.count:
            raise IndexError(i)
        self._send_w32_msg(TB_DELETEBUTTON, i)
        del self._buttons[i]
        
class ToolBarButton(GuiObject):
    def __init__(self, toolbar, id):
        self._id = id
        self.toolbar = toolbar
        self._cmdmap = EventDispatchersMap()
        dispatcher = CMDEventDispatcher(self)
        self._cmdmap["clicked"] = dispatcher
        
    def bind(self, callback):
        self._cmdmap["clicked"].bind(callback)
        
    def enable(self, enabled=True):
        self.toolbar._send_w32_msg(TB_ENABLEBUTTON, self._id, MAKELONG(bool(enabled), 0))
        
    def disable(self):
        self.enable(False)
        
    def get_checked(self):
        return bool(self.toolbar._send_w32_msg(TB_ISBUTTONCHECKED, self._id))
        
    def set_checked(self, check):
        self.toolbar._send_w32_msg(TB_CHECKBUTTON, self._id, MAKELONG(bool(check), 0))
        
    