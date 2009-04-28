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
from ctypes import *
from weakref import WeakValueDictionary
import weakref
from font import *

__doc__ = '''
This module contains the core mechanism of pycegui
'''

class GuiType(type):
    '''\
    The metaclass of GuiObject, useful for automatic property generation
    '''

    def __init__(cls, name, bases, dict):
        # Here we create properties based on
        # the set_xxx/get_xxx methods and
        # doc_xxx attribute of the class we construct.
        type.__init__(cls, name, bases, dict)
        methods = [(name, obj) for name, obj in dict.items() if callable(obj)]  
        properties = {}
        for name, obj in methods :
            if name[:4] in ['get_', 'set_']:
                property_name, meth_type = name[4:], name[:3]
                if not property_name in properties :
                    properties[property_name] = {}

                obj.__doc__ = "%ster for property %s" %(meth_type, property_name) 
                properties[property_name][meth_type] = obj
                doc_name = "doc_%s" %property_name
                
                if doc_name in dict :
                    properties[property_name]['doc'] = dict[doc_name]
                else:
                    properties[property_name]['doc'] = ''
        
        for property_name, property_data in properties.items() :
            prop = _makeprop(property_name, property_data)
            setattr(cls, property_name, prop)
            
        setattr(cls, '_properties', properties)
                
        
        
        
def _makeprop(property_name, property_data):
    # A property factory used to reference
    # property getters and setters as locals
    # of this function
    fget = None
    fset = None
    fdel = None
    
    if 'get' in property_data :
        fget = lambda self : getattr(self, "get_%s" %property_name)()
        
    if 'set' in property_data :
        fset = lambda self, val : getattr(self, "set_%s" %property_name)(val)
        
    doc = property_data.get('doc', None)
    prop = property(fget = fget,
                    fset = fset,
                    fdel = fdel,
                    doc = doc,
                    )
                    
    return prop
    

class GuiObject(object):
    '''\
    The most basic pycegui type. 
    '''
    __metaclass__ = GuiType
    
    def __init__(self, **kw):
        self.set(**kw)
    
    def set(self, **kw):
        '''\
        set(self, prop1=value1, prop2=value2, ...) --> sets the property prop1 to value1, prop2 to value2, ...
        '''
        for option, value in kw.items() :
            try :
                getattr(self, "set_%s" %option)(value)
            except AttributeError:
                raise AttributeError("can't set attribute '%s'" %option)
        
        

# Global objects and procedures
class IdGenerator(object):
    '''
    A global class to generate unique integers
    ids starting from 1000
    '''
    
    current_id = 999
    recycle = []
    
    @classmethod
    def next(cls):
        if cls.recycle :
            return cls.recycle.pop(0)
        cls.current_id += 1
        return cls.current_id
        
    @classmethod    
    def reuseid(cls, id):
        cls.recycle.append(id)

# The dict which maps HWND to gui.Window instances
hwndWindowMap =  WeakValueDictionary()
hInstance = GetModuleHandle(NULL)
wndClasses = []
# Dict which contains gui.Window data at creation time
createHndlMap = {}

schedulees = {}

WM_SCHEDULE = 0x8000 + 2

class Schedulee():
    '''
    Used internally by PPyGui. Not documented yet
    '''
    def __init__(self, func, args, kw):
        self.func = func
        self.args = args
        self.kw = kw
    
    def apply(self):
        self.func(*self.args, **self.kw)
    
mainframe_hwnd = 0

def schedule(func, args=[], kw={}):
    '''
    Schedule the fuction func
    to be called as function(*args, **kw)
    in the main thread.
    Gui objects are not generally thread
    safe, so a thread should use schedule instead
    of modifying directly the gui
    '''
    schedulee = Schedulee(func, args, kw)
    sid = id(schedulee)
    schedulees[sid] = schedulee
    assert PostMessage(mainframe_hwnd, WM_SCHEDULE, 0, sid) != 0
    
            
def globalWndProc(hWnd, nMsg, wParam, lParam):
    '''
    Used internally by PPyGui. Not documented yet
    '''

    if nMsg == WM_CREATE:
        createStruct = CREATESTRUCT.from_address(int(lParam))
        window = createHndlMap.get(int(createStruct.lpCreateParams), None)
        if window:
            hwndWindowMap[hWnd] = window
    
    elif nMsg == WM_SCHEDULE:
        sid = lParam
        schedulee = schedulees[sid]
        schedulee.apply()
        del schedulees[sid]
        return 0
    
    elif 306<=nMsg<=312: #Handle WM_CTLCOLOR* messages
        try:
            hbrush=DefWindowProc(hWnd, nMsg, wParam, lParam)
            win = hwndWindowMap[lParam]
            win._on_color(wParam)
            return hbrush
        except:
            return 0
            
    # A WM_ACTIVATE could occur before
    # the callback is bound to the 'activate' signal
    # Handle it statically here
    elif nMsg == WM_ACTIVATE : 
        if hWnd in hwndWindowMap:
            try :
                hwndWindowMap[hWnd]._on_activate(Event(hWnd, nMsg, wParam, lParam))
                return 0
            except:
                pass
       
    handled = False
        
    dispatcher = registeredEventDispatcher.match(hWnd, nMsg, wParam, lParam)
    if dispatcher :
        if dispatcher.isconnected() :
            handled, result = dispatcher.dispatch(hWnd, nMsg, wParam, lParam)
            if handled : return result
            
    win = hwndWindowMap.get(hWnd, None)    
    if win and win._issubclassed:
        return CallWindowProc(win._w32_old_wnd_proc, hWnd, nMsg, wParam, lParam)
    
    return DefWindowProc(hWnd, nMsg, wParam, lParam)

cGlobalWndProc = WNDPROC(globalWndProc)

class RegisteredEventsDispatcher(object):
    '''
    Used internally by PPyGui. Not documented yet
    '''
    
    def __init__(self):
        self.msged = {}
        self.cmded = {}
        self.ntfed = {}
        self.ntfed2 = {}
        
    def match(self, hWnd, nMsg, wParam, lParam):
        if nMsg == WM_COMMAND :
            cmd = HIWORD(wParam)
            id = LOWORD(wParam)
            #print cmd, id
            if cmd == 4096 and id == 1:
                try:
                    win = hwndWindowMap[hWnd]
                    return win.onok()
                except AttributeError:
                    pass
            elif cmd == 4096 and id == 2:
                print 'cancel message'
#                try:
#                    win = hwndWindowMap[hWnd]
#                    win.close()
#                except AttributeError:
#                    pass
              
            try :
                return self.cmded[(id, cmd)]
            except :
                pass
                
        elif nMsg == WM_NOTIFY :
            nmhdr = NMHDR.from_address(int(lParam))
            hWnd = nmhdr.hwndFrom
            code = nmhdr.code
            
            try :
                return self.ntfed[(hWnd, code)]
            except :
                pass
                
            id = nmhdr.idFrom
            try :
                return self.ntfed2[(id, code)]
            except :
                pass
                
            #print 'debug', hWnd, code, nmhdr.idFrom
        elif nMsg in [WM_HSCROLL, WM_VSCROLL]:
            #Scroll messages are sent to parent
            #The source hWnd is lParam 
            try :
                #print "WM_XSCROLL lParam", lParam
                return self.msged[(lParam, nMsg)]
            except :
                pass
        
        else :
            try :
                #if dispatch.w32_hWnd == hWnd and dispatch.nMsg == nMsg :
                return self.msged[(hWnd, nMsg)]
            except :
                pass
                    
    def install(self, dispatcher):
        if isinstance(dispatcher, MSGEventDispatcher):
            self.msged[(dispatcher.w32_hWnd, dispatcher.nMsg)] = dispatcher
        elif isinstance(dispatcher, CMDEventDispatcher):
            self.cmded[(dispatcher._id, dispatcher.cmd)] = dispatcher
        elif isinstance(dispatcher, NTFEventDispatcher):
            self.ntfed[(dispatcher.w32_hWnd, dispatcher.code)] = dispatcher
            if hasattr(dispatcher, '_id'):
                self.ntfed2[(dispatcher._id, dispatcher.code)] = dispatcher
    
    def remove(self, dispatcher):
#        for d in [self.msged, self.cmded, self.ntfed]:
#            for key, disp in d.items() :
#                if disp is dispatcher :
#                    del d[key]
#                    break
                    #return
        if isinstance(dispatcher, MSGEventDispatcher):
            del self.msged[(dispatcher.w32_hWnd, dispatcher.nMsg)]
        elif isinstance(dispatcher, CMDEventDispatcher):
            del self.cmded[(dispatcher._id, dispatcher.cmd)]
        elif isinstance(dispatcher, NTFEventDispatcher):
            del self.ntfed[(dispatcher.w32_hWnd, dispatcher.code)]
            if hasattr(dispatcher, '_id'):
                del self.ntfed2[(dispatcher._id, dispatcher.code)]
            
registeredEventDispatcher = RegisteredEventsDispatcher()

# Events and EventDispatcher objects

class Event(GuiObject):
    '''\
    Basic object that wraps a win32 message, it is often
    the first argument received by a callback.
    Use the read-only properties to have more information about an Event instance.
    '''
    def __init__(self, hWnd, nMsg, wParam, lParam):
        self.hWnd = hWnd
        self.nMsg = nMsg
        self.wParam = wParam
        self.lParam = lParam
        self._window = hwndWindowMap.get(hWnd, None)
        self.handled = True
    
    def get_window(self):
        return self._window
        
    doc_window = "Source Window instance that triggered the event"
    
    def skip(self):
        '''\
        Tells the default window procedure to handle the event.
        '''
        self.handled = False
        
class SizeEvent(Event):
    '''\
    An Event that is raised by a window when resized
    '''
    def __init__(self, hWnd, nMsg, wParam, lParam):
        self._size = LOWORD(lParam), HIWORD(lParam)
        Event.__init__(self, hWnd, nMsg, wParam, lParam)
        
    def get_size(self):
        return self._size
          
    doc_size = 'The new size of the window as a tuple (widht, height)'
    
class CommandEvent(Event):
    '''\
    An Event that wraps Win32 WM_COMMAND messages
    '''
    def __init__(self, hWnd, nMsg, wParam, lParam):
        self.id, self._cmd = LOWORD(wParam), HIWORD(wParam)
        #print lParam
        Event.__init__(self, lParam, nMsg, wParam, lParam)
        
    def get_cmd(self):
        return self._cmd
        
class NotificationEvent(Event):
    '''\
    An Event that wraps Win32 WM_NOTIFY messages
    '''
    def __init__(self, hWnd, nMsg, wParam, lParam):
        nmhdr = NMHDR.from_address(int(lParam))
        hwndFrom = nmhdr.hwndFrom
        self._code = nmhdr.code
        self.nmhdr = nmhdr
        Event.__init__(self, hwndFrom, nMsg, wParam, lParam)
        
    def get_code(self):
        return self._code
        
class StylusEvent(Event):
    '''
    An Event that is raised on interaction of a window with the stylus.
    '''
    def __init__(self, hWnd, nMsg, wParam, lParam):
       pt = GET_POINT_LPARAM(lParam)
       self._position = pt.x, pt.y
       Event.__init__(self, hWnd, nMsg, wParam, lParam)
       
    def get_position(self):
        return self._position
        
    doc_position = 'The position of the stylus as a tuple (left, top)'
    

class KeyEvent(Event):
    '''
    An event raised when the user press a keyboard
    or move the joystick in the window
    '''
    def __init__(self, hWnd, nMsg, wParam, lParam):
        self._key_code = wParam
        self._repeat_count = lParam & 65535
        Event.__init__(self, hWnd, nMsg, wParam, lParam)
        
    def get_key_code(self):
        return self._key_code
    
    doc_key_count = 'The virtual key code of the key pressed'
    
    def get_repeat_count(self):
        return self._repeat_count
     
class CharEvent(Event):
    '''
    An event raised when the user press a keyboard
    or move the joystick in the window
    '''
    def __init__(self, hWnd, nMsg, wParam, lParam):
        self._key_code = wParam
        self._repeat_count = lParam & 65535
        Event.__init__(self, hWnd, nMsg, wParam, lParam)
        
    def get_key(self):
        return unichr(self._key_code)

class EventDispatcher(object):
    '''
    Used internally by PPyGui. Not documented yet
    '''
        
    def __init__(self, eventclass = Event) :
        self.eventclass = eventclass 
        self.callback = None
        
    def isconnected(self):
        return bool(self.callback)
    
    def bind(self, callback=None):
        if callback is not None :
            self.callback = callback
    
    def unbind(self):
        self.callback = None
        
    def dispatch(self, hWnd, nMsg, wParam, lParam):
        if self.callback :
            event = self.eventclass(hWnd, nMsg, wParam, lParam)
            res = self.callback(event)
            if res is None:
                res = 0
            return event.handled, res
        return False
        
class CustomEventDispatcher(EventDispatcher):
    def call(self, event):
        if self.callback is not None:
            self.callback(event)
        
class MSGEventDispatcher(EventDispatcher):
    '''
    Used internally by PPyGui. Not documented yet
    '''
    
    def __init__(self, win, nMsg, eventclass = Event):
        self.w32_hWnd = win._w32_hWnd
        self.nMsg = nMsg
        EventDispatcher.__init__(self, eventclass)
    
        
class CMDEventDispatcher(EventDispatcher):
    '''
    Used internally by PPyGui. Not documented yet
    '''
    
    def __init__(self, win, cmd=0, eventclass = CommandEvent):
        self._id = win._id
        self.cmd = cmd
        EventDispatcher.__init__(self, eventclass)
    
class MenuEventDispatcher(EventDispatcher):
    '''
    Used internally by PPyGui. Not documented yet
    '''
    
    def __init__(self, id):
        self._id = id
        self.cmd = 0
        EventDispatcher.__init__(self, CommandEvent)
        
class NTFEventDispatcher(EventDispatcher):
    '''
    Used internally by PPyGui. Not documented yet
    '''
    
    def __init__(self, win, code, eventclass = NotificationEvent):
        self.w32_hWnd = win._w32_hWnd
        if hasattr(win, '_id'):
            self._id = win._id
        self.code = code
        EventDispatcher.__init__(self, eventclass)
        
class EventDispatchersMap(dict):
    '''
    Used internally by PPyGui. Not documented yet
    '''
    
    def __setitem__(self, i, dispatcher):
        registeredEventDispatcher.install(dispatcher)
        dict.__setitem__(self, i, dispatcher)
        
    def __del__(self):
        for event, dispatcher in self.items():
            registeredEventDispatcher.remove(dispatcher)
        
class Window(GuiObject):
    '''\
    The base class of all displayable elements
    Events:
        - paint -> Event: sent when the window needs repainting
        - close -> Event: sent when the user or os request the window to be closed
        - destroy -> Event: sent when the window is about to be destroyed
        - size -> SizeEvent: sent when the window is resized
        - lbdown -> StylusEvent: sent when the stylus is pressed down on the window 
        - lbmove -> StylusEvent: sent when the stylus is sliding on the window 
        - lbup -> StylusEvent: sent when the stylus is pressed down on the window 
    '''
    
    
    _w32_window_class = None
    _w32_window_style = WS_CHILD
    _w32_window_style_ex = 0
    _w32_window_class_style = CS_HREDRAW | CS_VREDRAW
    _dispatchers = {'paint': (MSGEventDispatcher, WM_PAINT,), 
                    'close' : (MSGEventDispatcher, WM_CLOSE,),
                    'destroy' : (MSGEventDispatcher, WM_DESTROY,),
                    'size' : (MSGEventDispatcher, WM_SIZE, SizeEvent),
                    'lbdown' : (MSGEventDispatcher, WM_LBUTTONDOWN, StylusEvent),
                    'lbmove' : (MSGEventDispatcher, WM_MOUSEMOVE, StylusEvent),
                    'lbup' : (MSGEventDispatcher, WM_LBUTTONUP, StylusEvent),
                    'chardown' : (MSGEventDispatcher, WM_CHAR, CharEvent),
                    'keydown' : (MSGEventDispatcher, WM_KEYDOWN, KeyEvent),
                    'focus' : (MSGEventDispatcher, WM_SETFOCUS,),
                    'lostfocus' : (MSGEventDispatcher, WM_SETFOCUS+1,),
                    'erasebkg' : (MSGEventDispatcher, WM_ERASEBKGND),
                    }
        
    def __init__(self, parent=None, 
                       title="PocketPyGui", 
                       style="normal", 
                       visible=True, 
                       enabled=True, 
                       pos=(-1,-1,-1,-1), 
                       tab_traversal=True, 
                       **kw):
        '''\.
        Arguments:
            - parent: the parent window 
            - title: the title as appearing in the title bar.
            - style: normal or control
            - pos: a tuple (left, top, width, height) that determines the initial position of the window.
              use -1 in any tuple element for default positioning.
              It is strongly recommanded to use the Sizer classes to perform the layout.
            - tab_traversal : whether the Window implements automatic tab/jog-dial 
        '''
        
        #Fixme: clean the legacy venster code.
        windowClassExists = False
        cls = WNDCLASS() # WNDCLASS()
        if self._w32_window_class:
            if GetClassInfo(hInstance, unicode(self._w32_window_class), byref(cls)):
                windowClassExists = True
        
        #determine whether we are going to subclass an existing window class
        #or create a new windowclass
        self._issubclassed = self._w32_window_class and windowClassExists
        
        if not self._issubclassed:
            #if no _window_class_ is given, generate a new one
            className = self._w32_window_class or "pycegui_win_class_%s" % str(id(self.__class__))
            className = unicode(className)
            cls = WNDCLASS() # WNDCLASS()
            cls.cbSize = sizeof(cls)
            cls.lpszClassName = className
            cls.hInstance = hInstance
            cls.lpfnWndProc = cGlobalWndProc
            cls.style = self._w32_window_class_style
            cls.hbrBackground = 1 # Add background customisation
            cls.hIcon = 0
            cls.hCursor = 0
            
            
            ###
            if tab_traversal:
                cls.cbWndExtra = 32
            ###
            wndClasses.append(cls)
            atom = RegisterClass(byref(cls)) # RegisterClass
        else:
            #subclass existing window class.
            className = unicode(self._w32_window_class)
        
        assert style in ["normal", "control"]
        _w32_style = self._w32_window_style
 
        if not parent :
            _w32_style &= ~WS_CHILD
            
        if visible:
            _w32_style |= WS_VISIBLE
            
        
        defaultorpos = lambda pos : (pos == -1 and [CW_USEDEFAULT] or [pos])[0]
        left, top, width, height = [defaultorpos(p) for p in pos]

        parenthWnd = 0
        if parent :
            parenthWnd = parent._w32_hWnd
          
        menuHandle = 0
        if hasattr(self, '_id'):
            menuHandle = self._id
        
        createHndlMap[id(self)] = self
        self._w32_hWnd = CreateWindowEx(self._w32_window_style_ex,
                              unicode(className),
                              unicode(title),
                              _w32_style,
                              left,
                              top,
                              width,
                              height,
                              parenthWnd,
                              menuHandle,
                              hInstance,
                              id(self))

        if self._issubclassed:
            self._w32_old_wnd_proc = self.__subclass(cGlobalWndProc)
            hwndWindowMap[self._w32_hWnd] = self
        
        self.events = EventDispatchersMap()
        for eventname, dispatchinfo in self._dispatchers.items() :
            dispatchklass = dispatchinfo[0]
            dispatchargs = dispatchinfo[1:]
            self.events[eventname] = dispatchklass(self, *dispatchargs)
        del createHndlMap[id(self)]
        
        GuiObject.__init__(self, **kw)
        self.bind(destroy=self._ondestroy)
        self.enable(enabled)
        
    def bind(self, **kw):
        '''\
        bind(self, event1=callback1, event2=callbac2, ...) -->
        maps gui events to callbacks,
        callbacks are any callable fthat accept a single argument.
        ''' 
        for option, value in kw.items() :
            try:
                self.events[option].bind(value)
            except KeyError :
                raise KeyError("%r has no event '%s'" %(self, option))
        
    def call_base_proc(self, event):
        return CallWindowProc(self._w32_old_wnd_proc, self._w32_hWnd, event.nMsg, event.wParam, event.lParam)
        
    def __subclass(self, newWndProc):
        return SetWindowLong(self._w32_hWnd, GWL_WNDPROC, newWndProc)
        
    def _send_w32_msg(self, nMsg, wParam=0, lParam=0):
        return SendMessage(self._w32_hWnd, nMsg, wParam, lParam)
    
    def get_client_rect(self):
        rc = RECT()
        GetClientRect(self._w32_hWnd, byref(rc))
        return rc
    
    doc_client_rect = 'The window client rect, i.e. the inner rect of the window'
        
    def get_window_rect(self):
        rc = RECT()
        GetWindowRect(self._w32_hWnd, byref(rc))
        return rc
    
    doc_window_rect = 'The window rect in its parent container'
    
    def get_pos(self):
        rc = self.window_rect
        parent = self.parent
        if parent is not None:
            parent_rc = parent.window_rect
            return rc.left-parent_rc.left, rc.top-parent_rc.top
        return rc.left, rc.top
        
    def set_pos(self, pos):
        left, top = pos
        left = int(left)
        top = int(top) 
        rc = self.window_rect
        
        MoveWindow(self._w32_hWnd, left, top, rc.width, rc.height, 0)
    
    doc_pos = 'The relative window position in its parent container as a tuple (left, top)'
    
    def get_size(self):
        rc = self.client_rect
        return rc.width, rc.height
        
    def set_size(self, size):
        width, height = size
        width = int(width)
        height = int(height)
        left, top = self.pos
        MoveWindow(self._w32_hWnd, left, top, width, height, 0)
    
    doc_size = 'The size of the window as a tuple (width, height)'
        
    def get_parent(self):
        parentHwnd = GetParent(self._w32_hWnd)
        return hwndWindowMap.get(parentHwnd, None)
        
    doc_parent = 'The parent window instance or None for a top window'
    
    def focus(self):
        '''
        Force the focus on this window
        '''
        SetFocus(self._w32_hWnd)
    
    def set_redraw(self, redraw):
        self._send_w32_msg(WM_SETREDRAW, bool(redraw), 0)
        
    doc_redraw = '''\
    The redraw state as a bool. When setting it to
    False, the window will not be repainted, until it
    is set to True again'''

    def get_text(self):
        textLength = self._send_w32_msg(WM_GETTEXTLENGTH)# + 1
        textBuff = u' ' * textLength
        textBuff = create_unicode_buffer(textBuff)
        self._send_w32_msg(WM_GETTEXT, textLength+1, textBuff)
        return textBuff.value
        
    def set_text(self, txt):
        self._send_w32_msg(WM_SETTEXT, 0, unicode(txt))
        
    doc_text = "The text displayed by the control as a string"
        
    def show(self, val=True):
        '''\
        Show or hide the window, depending of the
        boolean value of val. 
        '''
        if val :
            ShowWindow(self._w32_hWnd, SW_SHOW)
        else :
            ShowWindow(self._w32_hWnd, SW_HIDE)
            
    def hide(self):
        '''\
        Hide the window. Equivalent to win.show(False)
        '''
        self.show(False)
            
    def enable(self, val=True):
        '''\
        Enable or disable the window, depending of the
        boolean value of val. 
        '''
        EnableWindow(self._w32_hWnd, int(val))
        
    def disable(self):
        '''\
        Disable the window
        '''
        self.enable(False)
        
    def update(self):
        '''\
        Forces the window to be repainted
        '''
        UpdateWindow(self._w32_hWnd)
        
    def move(self, left, top, width, height):
        '''\
        Moves the window to the desired rect (left, top, width, height)
        '''
        MoveWindow(self._w32_hWnd, left, top, width, height, 0)

    def close(self):
        '''
        Programmaticaly request the window to be closed
        '''
        self._send_w32_msg(WM_CLOSE)
        
    def destroy(self):
        '''
        Destroy the window and its child, releasing their resources, and break 
        reference cycle that could be induced by the event system.
        '''
        DestroyWindow(self._w32_hWnd)
    
    def _ondestroy(self, event):
        del self.events
        event.skip()
        
    def bringtofront(self):
        '''\
        Bring the window to foreground
        '''
        SetForegroundWindow(self._w32_hWnd)

class Control(Window):
    '''\
    The base class for common controls.
    It introduces the text and font properties
    '''
    
    _w32_window_style = WS_CHILD
    _defaultfont = DefaultFont
    _w32_window_class_style = 0
    
    def __init__(self, parent, title="", border=False, visible=True, enabled=True, pos=(-1,-1,-1,-1), tab_stop=True, **kw):
        style="control"
        self._id = IdGenerator.next()
        if tab_stop:
            self._w32_window_style |= WS_TABSTOP
        if border:
            self._w32_window_style |= WS_BORDER
        Window.__init__(self, parent, title, style, visible=visible, enabled=enabled, pos=pos)
        self.font = self._defaultfont
        self.set(**kw)
#        self.bind(erasebkg=self._onebkg)
#        
#    def _onebkg(self, ev):
#        return 1
#        #ev.skip()
        
    def set_font(self, font):
        self._font = font
        self._send_w32_msg(WM_SETFONT, font._hFont, 1)
    
    def get_font(self):
        #return self._send_w32_msg(WM_GETFONT)
        return self._font
        
    doc_font = "The font of the control as a font.Font instance"
        
    def __del__(self):
        #Window.__del__(self)
        IdGenerator.reuseid(self._id)
        
    def get_best_size(self):
        return None, None
        
    def _on_color(self, dc):
        if hasattr(self, '_font'):
            SetTextColor(dc, self._font._color)
        
class Frame(Window):
    '''
    Frame extends Window to provide layout facilities.
    You can bind a sizer to a Frame using the sizer property
    '''
    _w32_window_style = Window._w32_window_style | WS_CLIPCHILDREN
    _w32_window_style_ex = 0x10000
    def __init__(self, parent, title="", pos=(-1,-1,-1,-1), visible=True, enabled=True, tab_traversal=True,**kw):
        self._sizer = None
        Window.__init__(self, parent, title, style="normal", pos=pos, visible=visible, enabled=enabled, tab_traversal=tab_traversal, **kw)
        self.events['size'].bind(self._on_size)
        
    def get_sizer(self):
        return self._sizer
        
    def set_sizer(self, sizer):
        self._sizer = sizer
        self.layout()
        
    def get_best_size(self):
        if self._sizer is not None:
            return self._sizer.get_best_size()
        return None, None
        
    doc_sizer = "A sizer.Sizer, sizer.HSizer or sizer.VSizer instance responsible of the layout"
    
    def layout(self):
        '''\
        Forces the frame to lay its content out with its sizer property. 
        Note it is automatically called anytime the Frame is moved or resized, 
        or when the sizer property is set.
        '''
        if self._sizer is not None:
            rc = RECT()
            GetClientRect(self._w32_hWnd, byref(rc))
            self._sizer.size(rc.left, rc.top, rc.right, rc.bottom)
    
    def _on_size(self, event):
        self.layout()


        
# MessageLoop and Application   

class MessageLoop:
    '''
    Used internally by PPyGui. Not documented yet
    '''
    def __init__(self):
        self.m_filters = {}

    def AddFilter(self, filterFunc):
        self.m_filters[filterFunc] = 1

    def RemoveFilter(self, filterFunc):
        del self.m_filters[filterFunc]
        
    def Run(self):
        msg = MSG()
        lpmsg = byref(msg)
        while GetMessage(lpmsg, 0, 0, 0):
            if not self.PreTranslateMessage(msg):
                if IsDialogMessage(GetActiveWindow(), lpmsg):
                    continue
                TranslateMessage(lpmsg)
                DispatchMessage(lpmsg)
        global quit
        quit = True
                    
    def PreTranslateMessage(self, msg):
        for filter in self.m_filters.keys():
            if filter(msg):
                return 1
        return 0
    
theMessageLoop = MessageLoop()

def GetMessageLoop():
    return theMessageLoop

class Application(GuiObject):
    '''\
    Each ppygui application should have an instance of Application.
    An Application object has a mainframe property which is usually a 
    ce.CeFrame object, which quits the application when destroyed
    '''
    def __init__(self, mainframe=None):
        self.messageloop = MessageLoop()
        if mainframe is not None:
            self.mainframe = mainframe
            
    def run(self):
        '''\
        Start the main loop of the application.
        It get rids of the nasty busy cursor, 
        whatever PythonCE is launched
        with /nopcceshell or not.
        '''
        try:
            import _pcceshell_support
            _pcceshell_support.Busy(0)
        except ImportError :
            SetCursor(LoadCursor(0, 0))
        return self.messageloop.Run()

    def set_mainframe(self, frame): 
        self._mainframe = frame
        self._mainframe.bind(destroy=lambda event : self.quit())
        global mainframe_hwnd 
        mainframe_hwnd = frame._w32_hWnd
        
        
    def get_mainframe(self):
        return self._mainframe
        
    doc_mainframe ="""\
    The main frame of the application.
    The application will exit when frame is destroyed
    """
        
    
    def quit(self, exitcode = 0):
        """\
        Quits the application with the exit code exitcode
        """
        PostQuitMessage(exitcode)
