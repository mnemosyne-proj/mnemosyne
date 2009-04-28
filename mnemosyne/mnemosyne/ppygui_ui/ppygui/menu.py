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

class AbstractMenuBase(GuiObject):
    
    def __init__(self):
        if type(self) == AbstractMenuBase :
            raise TypeError("Cannot instantiate an abstract class") 
        self._hmenu = self._create_menu()
        self._items = []
        
    def get_count(self):
        return len(self._items)
        
    def append(self, text, callback=None, enabled=True):
        new_id = IdGenerator.next()
        item = MenuItem(self, new_id)
        AppendMenu(self._hmenu, MF_STRING, new_id, unicode(text))
        item.enable(enabled)
        item.bind(callback)
        self._items.append(item)
        return item
        
    def append_menu(self, text, menu):
        if not isinstance(menu, AbstractMenuBase):
            raise TypeError("arg 1 must be an instance of a subclass of AbstractMenuBase")
        if self._hmenu == menu._hmenu :
            raise ValueError("a menu cannot contain itself")
        AppendMenu(self._hmenu, MF_POPUP, menu._hmenu, unicode(text))
        self._items.append(menu)    
        
    def append_separator(self):
        AppendMenu(self._hmenu, MF_SEPARATOR, 0,0)
        
    def insert(self, i, text, enabled=True):
        pass
        
    def insert_menu(self, i, menu):
        pass
        
    def insert_separator(self, i):
        pass
        
    def __getitem__(self, i):
        return self._items[i]
        
    def __delitem__(self, i):
        if not 0 <=i<self.count:
            raise IndexError 
        #RemoveMenu(self._hmenu, MF_BYPOSITION, i) 
        del self._items[i]
        
    def destroy(self):
        del self._items[:]
        DestroyMenu(self._hmenu)
        
    def __del__(self, ):
        print "del Menu(%i)" %self._hmenu
    
class MenuWrapper(AbstractMenuBase):
    def __init__(self, hmenu):
        self._hmenu = hmenu
        self._items = []
            
class Menu(AbstractMenuBase):
    def _create_menu(self):
        return CreateMenu()
        
class PopupMenu(AbstractMenuBase):
    def _create_menu(self):
        return CreatePopupMenu()
        
    def popup(self, win, x, y):
        return TrackPopupMenuEx(self._hmenu, 0, x, y, win._w32_hWnd, 0)

    
class MenuItem(GuiObject):
    
    def __init__(self, menu, id):
        self._menu = menu
        self._id = id
        self._cmdmap = EventDispatchersMap()
        dispatcher = CMDEventDispatcher(self)
        self._cmdmap["clicked"] = dispatcher
        
    def enable(self, value=True):
        if value :
            EnableMenuItem(self._menu._hmenu, self._id, MF_ENABLED)
        else :
            EnableMenuItem(self._menu._hmenu, self._id, MF_GRAYED)
            
    def disable(self):
        self.enable(False)
        
    def check(self, value=True):
        if value :
            CheckMenuItem(self._menu._hmenu, self._id, MF_CHECKED)
        else :
            CheckMenuItem(self._menu._hmenu, self._id, MF_UNCHECKED)
            
    def uncheck(self):
        self.check(False)
        
    def bind(self, callback):
        self._cmdmap["clicked"].bind(callback)
        
    def __del__(self):
        IdGenerator.reuseid(self._id)
        print "del MenuItem(%i)" %self._id
        
def recon_context(win, event):
    shi = SHRGINFO()
    shi.cbSize = sizeof(SHRGINFO) 
    shi.hwndClient = win._w32_hWnd
    shi.ptDown = POINT(*event.position)
    shi.dwFlags = SHRG_RETURNCMD
    if SHRecognizeGesture(byref(shi)) == GN_CONTEXTMENU :
        return True
    return False 
    
def context_menu(win, event, popmenu):
    rc = win.window_rect
    x, y = event.position
    return popmenu.popup(win, x+rc.left, y+rc.top)
    