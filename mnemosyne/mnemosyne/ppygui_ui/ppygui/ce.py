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
from .config import HIRES_MULT
from .controls import TBBUTTONINFO 
from .menu import Menu, PopupMenu, MenuWrapper
from .toolbar import ToolBar

# FixMe: Refactor these constants
TBIF_STATE = 0x4
TBSTATE_ENABLED = 0x4
TBSTATE_INDETERMINATE = 0x10

SHFullScreen = cdll.aygshell.SHFullScreen
SHFS_SHOWSIPBUTTON = 0x4
SHFS_HIDESIPBUTTON = 0x8
SHCMBF_HIDESIPBUTTON = 0x4

SHInitExtraControls = cdll.aygshell.SHInitExtraControls
SHInitExtraControls()

class SIPPref(Window):
    '''
    A hidden Window that automatically
    controls the Software Input Panel
    according to the control focused in
    the parent window.
    
    It should be instancied after all
    other controls in the parent window
    '''
    _w32_window_class = "SIPPREF"
    _w32_window_style = WS_CHILD
    _id = -1
    
    def __init__(self, parent):
        Window.__init__(self, parent, visible=False)

def make_sippref(parent):
    CreateWindowEx(0, "SIPPREF", "", WS_CHILD, -10, -10, 5, 5, parent._w32_hWnd, next(IdGenerator), GetModuleHandle(0), 0)
    
class CommandBarItem(GuiObject):
    '''\
    Not implemented yet, will be used for managing the main menubar 
    aka command bar
    '''
    def __init__(self, cb_hWnd, index):
        self.cb_hWnd = cb_hWnd
        self.index = index
        
    def set_text(self, txt):
        tbbi = TBBUTTONINFO()
        tbbi.cbSize = sizeof(tbbi)
        tbbi.dwMask = TBIF_TEXT | 0x80000000
        tbbi.pszText = str(txt)
        SendMessage(self.cb_hWnd, WM_USER+64, self.index, byref(tbbi))
    
    def enable(self, val=True):
        tbbi = TBBUTTONINFO()
        tbbi.cbSize = sizeof(tbbi)
        tbbi.dwMask = TBIF_STATE | 0x80000000
        if val:
            tbbi.fsState = TBSTATE_ENABLED
        else:
            tbbi.fsState = TBSTATE_INDETERMINATE
        SendMessage(self.cb_hWnd, WM_USER+64, self.index, byref(tbbi))
    
        
    def disable(self):
        self.enable(False)
        
class CommandBarAction(CommandBarItem):
    '''\
    Not implemented yet, will be used for managing the main menubar 
    aka command bar
    '''
    def __init__(self, cb_hWnd, index, menu_item):
        CommandBarItem.__init__(self, cb_hWnd, index)
        self.menu_item = menu_item
    
    def bind(self, cb):
        self.menu_item.bind(cb)   
        
class CommandBarMenu(CommandBarItem, MenuWrapper):
    '''\
    Not implemented yet, will be used for managing the main menubar 
    aka command bar
    '''
    def __init__(self, cb_hWnd, index, hMenu):
        CommandBarItem.__init__(self, cb_hWnd, index)
        MenuWrapper.__init__(self, hMenu)
    

class CeFrame(Frame):
    '''\
    CeFrame is a frame designed to be a Windows CE compliant window.
    A CeFrame will track the SIP position and size and will automatically
    resize itself to always fit the screen.
    '''
    _dispatchers = {"_activate" : (MSGEventDispatcher, WM_ACTIVATE),
                    "_settingchanged" : (MSGEventDispatcher, WM_SETTINGCHANGE),
                    }
    _dispatchers.update(Frame._dispatchers)
    
    def __init__(self, parent=None, title="PocketPyGui", action=None, menu=None, tab_traversal=True, visible=True, enabled=True, has_sip=True, has_toolbar=False):
        '''\
        Arguments :
            - parent: the parent window of this CeFrame.
            - title: the title as appearing in the title bar.
            - action : a tuple ('Label', callback) .
            - menu : the title of the right menu as a string
                     if not None, the menu can be filled via the cb_menu attribute
                     after CeFrame initialization.
        '''
        Frame.__init__(self, parent, title, tab_traversal=tab_traversal, visible=visible, enabled=enabled)
        self.bind(_activate=self._on_activate,
                  _settingchanged=self._on_setting_changed)
        if has_toolbar :
            self.toolbar = ToolBar(self)
        else:
            self.toolbar = None
        self.__create_menubar(action, menu, has_sip)
        
        
    def layout(self):
        if self.toolbar is None:
            return Frame.layout(self)
        if self._sizer is not None:
            rc = RECT()
            GetClientRect(self._w32_hWnd, byref(rc))
            self._sizer.size(rc.left, rc.top, rc.right, rc.bottom-24*HIRES_MULT)
            self.toolbar.move(rc.left, rc.bottom-26*HIRES_MULT, rc.right-rc.left, 26*HIRES_MULT)
    
    
    def __create_menubar(self, action, menu, has_sip):
        mbi = SHMENUBARINFO()
        mbi.cbSize = sizeof(SHMENUBARINFO)
        mbi.hwndParent = self._w32_hWnd
        mbi.hInstRes = GetModuleHandle(0)
        
        slots = []
        
        empty = True
        has_action = False
        has_menu = False
        
        if (action is None) and (menu is None) :
            mbi.dwFlags = SHCMBF_EMPTYBAR
            
        else :
            empty = False
            temp_menu = Menu()
            i = 0
            if action is not None:
                label, cb = action
                action_item = temp_menu.append(label, callback=cb)
                #self.action = CommandBarAction(item, 0)
            else:
                action_item = temp_menu.append("", enabled=False)
                
            if menu is not None:
                sub_menu = PopupMenu()
                temp_menu.append_menu(menu, sub_menu) 
                has_menu = True
                
            mbi.dwFlags = SHCMBF_HMENU
            mbi.nToolBarId = temp_menu._hmenu
            
        if not has_sip:
            mbi.dwFlags |= SHCMBF_HIDESIPBUTTON
        SHCreateMenuBar(byref(mbi))
        self._mb_hWnd = mbi.hwndMB
        
        if not empty:
            self.cb_action = CommandBarAction(mbi.hwndMB, 0, action_item)
            
            if has_menu:
                tbbi = TBBUTTONINFO()
                tbbi.cbSize = sizeof(tbbi)
                tbbi.dwMask = 0x10 | 0x80000000
                SendMessage(mbi.hwndMB, WM_USER+63, 1, byref(tbbi))
                hMenu = tbbi.lParam         
                self.cb_menu = CommandBarMenu(mbi.hwndMB, 0, hMenu)
        
        rc = RECT()
        GetWindowRect(self._w32_hWnd, byref(rc))
        rcmb = RECT()
        GetWindowRect(self._mb_hWnd, byref(rcmb))
        rc.bottom -= (rcmb.bottom - rcmb.top)
        self.move(rc.left, rc.top, rc.right-rc.left, rc.bottom-rc.top)
        
    def _on_activate(self, event):
        if not hasattr(self, '_shai'):
            self._shai = InitSHActivateInfo()
        SHHandleWMActivate(event.hWnd, event.wParam, event.lParam, byref(self._shai), 0)
    
    def _on_setting_changed(self, event):
        SHHandleWMSettingChange(self._w32_hWnd, event.wParam, event.lParam, byref(self._shai))

    def show_sipbutton(self, show=True):
        if show:
            SHFullScreen(self._w32_hWnd, SHFS_SHOWSIPBUTTON)
        else:
            SHFullScreen(self._w32_hWnd, SHFS_HIDESIPBUTTON)
        
    def hide_sipbutton(self):
        self.show_sipbutton(False)