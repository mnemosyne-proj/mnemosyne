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
from boxing import VBox

__doc__ = '''\
This module contains the core high-level widgets of ppygui.
See also ppygui.html for the HTML control.
'''

class Label(Control):
    '''\
    The Label control displays a static text.
    Events:
        - clicked -> CommandEvent
    '''
    _w32_window_class = "STATIC"
    _w32_window_style = WS_CHILD 
    _dispatchers = {'clicked' : (CMDEventDispatcher, ),
                    }
    _dispatchers.update(Control._dispatchers)
    
    def __init__(self, parent, title="", align="left", border=False, visible=True, enabled=True, pos=(-1,-1,-1,-1), **kw):
        '''\
        Arguments:
            - parent: the parent window.
            - title: the text to be displayed.
            - align: the text alignment in its window, can be "left", "center" or "right".
            - border: a boolean that determines if this control should have a border.
        '''
        if align not in ["left", "center", "right"]:
            raise ValueError, 'align not in ["left", "center", "right"]'
            
        orStyle = SS_NOTIFY
        if align == "center":
            orStyle |= SS_CENTER
        elif align == "right":
            orStyle |= SS_RIGHT
        self._w32_window_style |= orStyle
        Control.__init__(self, parent, title, border, visible, enabled, pos, tab_stop=False,  **kw)
        self._best_size = None
    
    def get_text(self):
        return Control.get_text(self)
            
    def set_text(self, value):
        Control.set_text(self, value)
        self._best_size = None
        
    def get_font(self):
        return Control.get_font(self)
            
    def set_font(self, value):
        Control.set_font(self, value)
        self._best_size = None
        
    def _get_best_size(self):
        dc = GetDC(self._w32_hWnd)
        font = self._font._hFont
        SelectObject(dc, font)
        text = self.text
        cx, cy = GetTextExtent(dc, text)
        cy = cy*(1+text.count('\n'))
        return 5+cx/HIRES_MULT, 2+cy/HIRES_MULT
        
    def get_best_size(self):
        if self._best_size is None:
            best_size = self._get_best_size()
            self._best_size = best_size
            return best_size
        else:
            return self._best_size
            
class Button(Control):
    '''\
    The button control displays a command button,
    it can be a push button, a default button, or
    a check box.
    For a radio button see the RadioButton class
    Events :
        - clicked -> CommandEvent
    '''
    
    _w32_window_class = "BUTTON"
    _w32_window_style = WS_CHILD
    _dispatchers = {'clicked' : (CMDEventDispatcher, )}
    _dispatchers.update(Control._dispatchers)
    _defaultfont = ButtonDefaultFont
    
    def __init__(self, parent, title="", action=None, align="center", style="normal", border=False, visible=True, enabled=True, pos=(-1,-1,-1,-1), **kw):
        '''
        Arguments:
            - title: the text of the button.
            - action: the callback called when the button is clicked (equivalent to button.bind(clicked=callback))
            - align: the text alignment, can be "left", "center" or "right".
            - style:
                - "normal" for a classic push button
                - "default" for a default push button
                - "check" for a check box
            - border: a boolean that determines if this control should have a border.
        '''
        if align not in ["left", "center", "right"]:
            raise ValueError, 'align not in ["left", "center", "right"]'
        if style not in ["normal", "default", "check", "radio"]:
            raise ValueError, 'style not in ["normal", "default", "check", "radio"]'
        orStyle = 0
        self._check = False
        if style == "normal" :
            orStyle |= BS_PUSHBUTTON
        elif style == "default" :
            orStyle |= BS_DEFPUSHBUTTON
        elif style == "check" :
            orStyle |= BS_AUTOCHECKBOX
            self._defaultfont = DefaultFont
            self._check = True
        elif style == "radio" :
            orStyle |= BS_RADIOBUTTON
            self._defaultfont = DefaultFont
        if align == "left":
            orStyle |= BS_LEFT
        elif align == "right":
            orStyle |= BS_RIGHT
        self._w32_window_style |= orStyle
        Control.__init__(self, parent, title, border, visible, enabled, pos, **kw)
        
        if action is not None:
            self.bind(clicked=action)
        
        self._best_size = None
            
    def get_checked(self):
        '''\
        getter for property checked
        '''
        check = self._send_w32_msg(BM_GETCHECK)
        if check == BST_CHECKED :
            return True
        return False
        
    def set_checked(self, check):
        '''\
        setter for property checked
        '''
        if check :
            w32_check = BST_CHECKED
        else :
            w32_check = BST_UNCHECKED
        self._send_w32_msg(BM_SETCHECK, w32_check)
        
    doc_checked = "Returns or set the checked state of a button as a boolean (makes only sense for a button created with check or radio style)"
        
    def get_text(self):
        return Control.get_text(self)
            
    def set_text(self, value):
        Control.set_text(self, value)
        self._best_size = None
        
    def get_font(self):
        return Control.get_font(self)
            
    def set_font(self, value):
        Control.set_font(self, value)
        self._best_size = None
        
    def _get_best_size(self):
        dc = GetDC(self._w32_hWnd)
        font = self._font._hFont
        SelectObject(dc, font)
        cx, cy = GetTextExtent(dc, self.text)
        if self._check:
            return 20+cx/HIRES_MULT, 4+cy/HIRES_MULT
        return 10+cx/HIRES_MULT, 10+cy/HIRES_MULT
        
    def get_best_size(self):
        if self._best_size is None:
            best_size = self._get_best_size()
            self._best_size = best_size
            return best_size
        else:
            return self._best_size
            
class RadioButton(Button):
    '''
    The RadioButton control displays a classic radio button,
    it belongs to a RadioGroup, which owns mutually exclusive radio buttons,
    and is bound to a value (any python object) that is useful for retrieving in
    the radio group.
    '''
    def __init__(self, parent, title="", align="center", group=None, value=None, border=False, visible=True, enabled=True, selected=False, pos=(-1,-1,-1,-1), **kw):
        '''
        Arguments:
            - title: the text of the button.
            - action: the callback called when the button is clicked (equivalent to button.bind(clicked=callback))
            - align: the text alignment, can be "left", "center" or "right".
            - group: the group of the radio as a RadioGroup instance or None.
            - value: any python object bound to the RadioButton
            - border: a boolean that determines if this control should have a border.
        '''
        Button.__init__(self, parent, title=title, style="radio", action=None, align=align, pos=pos, border=border, visible=visible, enabled=enabled, **kw)
        
        if group is not None:
            if not isinstance(group, RadioGroup):
                raise TypeError("arg group must be a RadioGroup instance or None")
            group._add(self)
            if selected:
                group.selection = self
        self._value = value
    
    def _get_best_size(self):
        dc = GetDC(self._w32_hWnd)
        
        font = self._font._hFont
        SelectObject(dc, font)
        cx, cy = GetTextExtent(dc, self.text)
        return 20 + cx/HIRES_MULT, 4+cy/HIRES_MULT
            
class RadioGroup(GuiObject):
    '''\
    Represents a group of mutually exclusive RadioButton
    Events:
        - update -> NoneType: sent when one of the radio buttons is clicked.
    '''
    
    def __init__(self):
        self._radios = []
        self.updatecb = None
        self._selection = None
        
    def bind(self, update=None):
        self.updatecb = update
        
    def _add(self, button):
        assert isinstance(button, RadioButton)
        self._radios.append(button)
        button.bind(clicked=self._onbuttonclicked)
        
    def get_selection(self):
        '''\
        getter for property selection
        '''
        return self._selection
        
    def set_selection(self, button):
        '''\
        setter for property selection
        '''
        assert button in self._radios #Fixme: raise ValueError instead of assertions
        for radio in self._radios :
            if button is radio :
                radio.checked = True
                self._selection = button
            else :
                radio.checked = False
    
    doc_selection = '''\
    The current selected radio as a Button instance, 
    if the button does not belong to this group it is an error"
    '''  
        
    def get_value(self):
        '''\
        getter for property value
        '''
        if self._selection is not None :
            return self._selection._value
            
    doc_value = "The value of the selected radio button"
        
    def _onbuttonclicked(self, event):
        button = event.window
        self.selection = button
        if self.updatecb is not None:
            self.updatecb(None)
            
class Edit(Control):
    '''\
    The edit control displays an editable text field. 
    Supported events :
        - update -> CommandEvent: sent when the text is updated by the user
    '''
    _w32_window_class = "EDIT"
    _w32_window_style = WS_CHILD
    _dispatchers = {'enter' : (CustomEventDispatcher,),
                    'update' : (CMDEventDispatcher, EN_UPDATE)}
    _dispatchers.update(Control._dispatchers)
    
    
    def __init__(self, parent, text="", align="left", style="normal", password=False, multiline = False, line_wrap=False, readonly=False, border=True, visible=True, enabled=True, pos=(-1,-1,-1,-1), **kw):
        '''\
        Arguments:
            - parent : the parent window
            - text : the initial text to display
            - align : the text alignment, can be "left", "center" or "right"
            - style :
                - normal : standard text field
                - number : accept numeric input only
            - password : a boolean that determines if the user input should be masked
            - multiline : a boolean that determines if the text should contain newlines
            - readonly : a boolean that determines if the text should be viewed only
            - border: a boolean that determines if this control should have a border.
        '''
        assert align in ["left", "center", "right"] #Fixme: raise ValueError instead of assertions
        assert style in ["normal", "number"] #idem
        #orStyle = ES_AUTOHSCROLL 
        orStyle = 0
        if style == "number" :
            orStyle |= ES_NUMBER
        if align == "center":
            orStyle |= ES_CENTER
        elif align == "left" :
            orStyle |= ES_LEFT
        elif align == "right":
            orStyle |= ES_RIGHT

        if password :
            orStyle |= ES_PASSWORD
        if multiline :
            self._multiline = True
            orStyle |= WS_VSCROLL | ES_AUTOVSCROLL | ES_MULTILINE | ES_WANTRETURN
            if not line_wrap:
                orStyle |= WS_HSCROLL
        else:
            self._multiline = False
            orStyle |= ES_AUTOHSCROLL
                
        self._w32_window_style |= orStyle
        Control.__init__(self, parent, text, border, visible, enabled, pos)
        self.set(readonly=readonly, **kw)
        self._best_size = None
        
    def _get_best_size(self):
        if self._multiline:
            return None, None
        
        dc = GetDC(self._w32_hWnd)
        font = self._font._hFont
        SelectObject(dc, font)
        text = self.text
        cx, cy = GetTextExtent(dc, text)
        return None, 7+cy/HIRES_MULT
        
    def get_readonly(self):
        '''\
        getter for property readonly
        '''
        style = GetWindowLong(self._w32_hWnd, GWL_STYLE)
        return bool(style & ES_READONLY)
        
    def set_readonly(self, val):
        '''\
        setter for property readonly
        '''
        self._send_w32_msg(EM_SETREADONLY, int(val))
    
    doc_readonly = "The read-only state of the edit as a boolean"
    
    def get_selection(self):
        '''\
        getter for property selection
        '''
        start = LONG()
        stop = LONG()
        self._send_w32_msg(EM_GETSEL, byref(start), byref(stop))
        return start.value, stop.value 
        
    def set_selection(self, val):
        '''\
        setter for property selection
        '''
        start, stop = val
        self._send_w32_msg(EM_SETSEL, start, stop)
    
    doc_selection = "The zero-based index selection as a tuple (start, stop)"

    def append(self, text):
        oldselect = self.selection
        n = self._send_w32_msg(WM_GETTEXTLENGTH)
        self.selection = n, n
        self.selected_text = text
        self.selection = oldselect
        
    def select_all(self):
        self.selection = 0, -1

    def get_modified(self):
        return bool(self._send_w32_msg(EM_GETMODIFY))
        
    def set_modified(self, mod):
        return self._send_w32_msg(EM_SETMODIFY, int(mod))

    def get_selected_text(self):
        txt = self.text
        start, end = self.selection
        return txt[start:end]
        
    def set_selected_text(self, txt):
        self._send_w32_msg(EM_REPLACESEL, 1, unicode(txt))
        
    def can_undo(self):
        '''\
        Return a bool that indicates if the current content can be undone
        '''
        return bool(self._send_w32_msg(EM_CANUNDO))
        
    def undo(self):
        '''\
        Undo the current content
        '''
        self._send_w32_msg(EM_UNDO)
        
    def cut(self):
        '''\
        Cut the current selection in the clipboard
        '''
        self._send_w32_msg(WM_CUT)
        
    def copy(self):
        '''\
        Copy the current selection in the clipboard
        '''
        self._send_w32_msg(WM_COPY)
    
    def paste(self):
        '''\
        Paste the content of the clipboard at the current position
        '''
        self._send_w32_msg(WM_PASTE)
    
    # Not tested    
    def line_from_char(self, i):
        return self._send_w32_msg(EM_LINEFROMCHAR, i)
        
    def line_index(self, i):
        return self._send_w32_msg(EM_LINEINDEX, i)
        
    def line_length(self, i):
        return self._send_w32_msg(EM_LINELENGTH, i)
        
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
            
class List(Control):
    '''
    The List control displays a list of choice
    Supported events :
    - choicechanged -> CommandEvent : sent when user selection has changed
    - choiceactivated -> CommandEvent : sent when the user double-click on a choice
    '''
    _w32_window_class = "ListBox"
    _w32_window_style = WS_CHILD | LBS_NOTIFY | WS_VSCROLL | LBS_HASSTRINGS
    _dispatchers = {'selchanged' : (CMDEventDispatcher, LBN_SELCHANGE),
                    'itemactivated' : (CMDEventDispatcher, LBN_DBLCLK)}
    _dispatchers.update(Control._dispatchers)
    
    def __init__(self, parent, choices=[], sort=False, multiple=False, border=True, visible=True, enabled=True, pos=(-1,-1,-1,-1), **kw):
        '''
        - choices : the initial possible choices as a list of string
        - sort : True if the choices have to be sorted in alphabetical order
        - multiple : True if the control should allow multiple selection
        ''' 
        orStyle = 0        
        self.multiple = multiple
        if sort :
            orStyle |= LBS_SORT
        if multiple :
            orStyle |= LBS_MULTIPLESEL
        self._w32_window_style |= orStyle
        Control.__init__(self, parent, "", border, visible, enabled, pos)
        
        for choice in choices :
            self.append(choice)
    
        self.set(**kw)
        
    def get_count(self):
        '''
        Returns the number of choices in the control
        '''
        return self._send_w32_msg(LB_GETCOUNT)
        
    doc_count = "The number of choices in the control"
    
    def append(self, choice):
        '''
        Adds the string choice to the list of choices
        '''
        self._send_w32_msg(LB_ADDSTRING, 0, unicode(choice))
        
    def insert(self, i, choice):
        '''
        Inserts the string choice at index i
        '''
        self._send_w32_msg(LB_INSERTSTRING, i, unicode(choice))
           
    def __getitem__(self, i):
        '''
        Returns the choice at index i as a string
        '''
        if not 0<=i<self.count:
            raise IndexError
        textLength = self._send_w32_msg(LB_GETTEXTLEN, i)# + 1
        textBuff = create_unicode_buffer(textLength+1)
        self._send_w32_msg(LB_GETTEXT, i, textBuff)
        return textBuff.value
        
    def __setitem__(self, i, text):
        '''\
        Sets the choice at index i
        '''
        if not 0<=i<self.count:
            raise IndexError
        del self[i]
        self.insert(i, text)
    
    def __delitem__(self, i):
        '''
        Removes the choice at index i
        '''
        self._send_w32_msg(LB_DELETESTRING, i)
        
    def is_multiple(self):
        '''
        Returns True if the Choice control allows 
        multiple selections
        '''
        return self.multiple
        
    def get_selection(self):
        '''
        Returns the current selection as an index or None in a single-choice
        control , or a list of index in a multiple-choice control
        '''  
        if not self.multiple :
            sel = self._send_w32_msg(LB_GETCURSEL)
            if sel >= 0 :
                return sel
        else :
            selections = []
            for i in range(self.count):
                if self._send_w32_msg(LB_GETSEL, i) > 0 :
                    selections.append(i)
            return selections
        
    def set_selection(self, selection):
        '''
        Sets the current selection as a list of index,
        In the case of a single-choice control, it accepts
        an index or will use the first index in the list
        ''' 
        try :
            len(selection)
        except TypeError :
            selection = [selection]
        if not self.multiple :
            return self._send_w32_msg(LB_SETCURSEL, selection[0])
        else :
            self._send_w32_msg(LB_SETSEL, 0, -1)
            for i in selection :
                self._send_w32_msg(LB_SETSEL, 1, i)
        
    doc_selection = "The current selection(s) as a list of index"
    
    def __iter__(self):
        return choiceiterator(self)
    
    
def choiceiterator(choice):
    for i in range(choice.count):
        yield choice[i]

class TableColumns(GuiObject):
    '''
    TableColumns instance are used to manipulate
    the columns of the bounded Table object
    '''
    def __init__(self, list, columns):
        '''
        Do not use this constructor directly
        it is instantiated automatically by Table
        '''
        self._list = list
        self._count = 0
        for title in columns :
            self.append(title)
            
    def __len__(self):
        return self._count
        
    def append(self, title, width=-1, align="left"):
        '''
        Adds a new column to the bounded table
        - title : the text of the column
        - width : the width of the column in pixels, -1 will set the width so that it contains the title
        - align : the alignment of the column, can be "left", "center" or "right"
        Returns the index of the newly created column
        '''
        i = len(self)
        return self.insert(i, title, width, align)

        
    def insert(self, i, title, width=-1, align="left"):
        '''
        Inserts a new column to the bounded table at index i
        - title : the text of the column
        - width : the width of the column in pixels, -1 will set the width so that it contains the title
        - align : the alignment of the column, can be "left", "center" or "right"
        Returns the index of the newly created column
        '''
        if not 0 <= i <= len(self):
            raise IndexError
        assert align in ["left", "center", "right"]
        col = LVCOLUMN()
        col.text = unicode(title)
        col.width = width
        if align == "left" :
            fmt = LVCFMT_LEFT
        elif align == "right" :
            fmt = LVCFMT_RIGHT
        elif align == "center" :
            fmt = LVCFMT_CENTER
            

        col.format = fmt
        self._list._insertcolumn(i, col)
        self._count += 1
        if width == -1 :
            self.adjust(i)
        return i
        
    def set(self, i, title=None, width=None, align=None):
        '''
        Sets the column of the bounded table at index i
        - title : the text of the column
        - width : the width of the column in px
        - align : the alignment of the column, can be "left", "center" or "right" (can produce artifacts)
        '''
        if not 0<=i<len(self):
            raise IndexError
        col = LVCOLUMN()
        if title is not None :
            col.text = title
        if width is not None :
            col.width = width
        if align is not None :
            assert align in ["left", "center", "right"]
            if align == "left" :
                fmt = LVCFMT_LEFT
            elif align == "right" :
                fmt = LVCFMT_RIGHT
            elif align == "center" :
                fmt = LVCFMT_CENTER
                

            col.format = fmt
        self._list._setcolumn(i, col)
        
    def adjust(self, i):
        '''
        Adjust the column width at index i
        to fit the header and all the texts in 
        this column.
        '''        
        if not 0<=i<len(self):
            raise IndexError
        self._list._send_w32_msg(LVM_SETCOLUMNWIDTH, i, -2)
            
    #def remove(self, column):
    #    pass
    def __delitem__(self, i):
        '''
        Removes the column at index i
        '''
        if not 0<=i<len(self):
            raise IndexError
        self._list._send_w32_msg(LVM_DELETECOLUMN, i)
        self._count -= 1
        
class TableRows(GuiObject):
    
    def __init__(self, list):
        '''
        Do not use this constructor directly,
        it is instantiated automatically by Table
        '''
        self._list = list
        self._data = []
    
    def __len__(self):
        return self._list._send_w32_msg(LVM_GETITEMCOUNT)
        
    def append(self, row, data=None):
        '''
        Adds a new row at the end of the list
        - row : a list of string
        - data : any python object that you want to link to the row
        '''
        self.insert(len(self), row, data)
        
    def insert(self, i, row, data=None):
        '''
        Inserts a new row at index i
        - row : a list of string
        - data : any python object that you want to link to the row
        '''
        if not 0<=i<=len(self):
            raise IndexError
        item = LVITEM()
        item.mask = LVIF_TEXT | LVIF_PARAM
        item.iItem = i
        #item.lParam = data
        item.iSubItem = 0
        item.pszText = row[0]
        self._list._insertitem(item)
        for iSubItem in range(len(row) - 1):
            item.mask = LVIF_TEXT
            item.iSubItem = iSubItem + 1
            item.pszText = row[iSubItem + 1]
            self._list._setitem(item)
        
        if i == len(self) - 1:
            self._data.append(data)
        else :
            self._data.insert(i, data)
        
    def __setitem__(self, i, row):
        '''
        Sets the row at index i as a list of string
        '''
        if not 0<=i<len(self):
            raise IndexError
        item = LVITEM()
        item.mask = LVIF_TEXT | LVIF_PARAM
        item.iItem = i
        #item.lParam = data
        item.iSubItem = 0
        item.pszText = row[0]
        self._list._setitem(item)
        for iSubItem in range(len(row) - 1):
            item.mask = LVIF_TEXT
            item.iSubItem = iSubItem + 1
            item.pszText = row[iSubItem + 1]
            self._list._setitem(item)
            
    def setdata(self, i, data):
        '''
        Bind any python object to the row at index i
        '''
        if not 0<=i<len(self):
            raise IndexError
        self._data[i] = data
        
    def __getitem__(self, i):
        '''
        Returns the row at index i as a list of string
        '''
        if not 0<=i<len(self):
            raise IndexError
        row = []
        for j in range(len(self._list.columns)):
            item = self._list._getitem(i, j)
            row.append(item.pszText)
            
        return row
        
    def getdata(self, i):
        '''
        Returns any python object that was bound to the row or None
        '''
        if not 0<=i<len(self):
            raise IndexError
        return self._data[i]
    
    #TODO: implement image api
    def getimage(self, i):
        pass
        
    def setimage(self, i, image_index):
        pass
        
    def getselected_image(self, i):
        pass
        
    def setselected_image(self, i, image_index):
        pass
    
    def ensure_visible(self, i):
        '''
        Ensures the row at index i is visible
        '''
        if not 0<=i<len(self):
            raise IndexError
        self._send_w32_msg(LVM_ENSUREVISIBLE, i)
    
    def is_selected(self, i):
        '''
        Returns True if the row at index i is selected
        '''
        if not 0<=i<len(self):
            raise IndexError
            
        item = LVITEM()
        item.iItem = i
        item.mask = LVIF_STATE
        item.stateMask = LVIS_SELECTED
        self._list._send_w32_msg(LVM_GETITEM, 0, byref(item))
        return bool(item.state)
        
    def select(self, i):
        '''
        Selects the row at index i
        '''
        if not 0<=i<len(self):
            raise IndexError
        item = LVITEM()
        item.iItem = i
        item.mask = LVIF_STATE
        item.stateMask = LVIS_SELECTED
        item.state = 2
        self._list._send_w32_msg(LVM_SETITEM, 0, byref(item))
    
    def deselect(self, i):
        '''
        deselects the row at index i
        '''
        if not 0<=i<len(self):
            raise IndexError
        item = LVITEM()
        item.iItem = i
        item.mask = LVIF_STATE
        item.stateMask = LVIS_SELECTED
        item.state = 0
        self._list._send_w32_msg(LVM_SETITEM, 0, byref(item))
        
    def get_selection(self):
        '''
        Get the current selections as a list
        of index
        '''
        l = []
        i = -1
        list = self._list
        while 1:
            i = list._send_w32_msg(LVM_GETNEXTITEM, i, LVNI_SELECTED)
            if i != -1:
                l.append(i)
            else:
                break
        return l
        
    def get_selected_count(self):
        return self._list._send_w32_msg(LVM_GETSELECTEDCOUNT)
        
    doc_selected_count = "The number of rows selected as an int (read-only)"
    
    def set_selection(self, selections):
        '''
        Sets the current selections as a list
        of index
        '''
        try :
            len(selections)
        except TypeError:
            selections = [selections]
        for i in xrange(len(self)):
            self.unselect(i)
            
        for i in selections:
            self.select(i)
    
    doc_selection = "The current selection(s) as a list of index"
        
    def __delitem__(self, i):
        '''
        del list.rows[i] : removes the row at index i
        '''
        if not 0<=i<len(self):
            raise IndexError
        self._list._send_w32_msg(LVM_DELETEITEM, i) 
        del self._data[i]

class Combo(Control):
    _w32_window_class = "COMBOBOX"
    _w32_window_style = WS_CHILD | CBS_AUTOHSCROLL | CBS_DISABLENOSCROLL | WS_VSCROLL
    _dispatchers = {'selchanged' : (CMDEventDispatcher, CBN_SELCHANGE)}
    _dispatchers.update(Control._dispatchers)
    
    def __init__(self, parent, style="edit", sort=False, choices=[], visible=True, enabled=True, pos=(-1,)*4, **kw):
        assert style in ["edit", "list"]
        orStyle = 0
        if style == "edit":
            orStyle |=  CBS_DROPDOWN
        elif style == "list":
            orStyle |= CBS_DROPDOWNLIST
        if sort :
            orStyle |= CBS_SORT
                
        self._w32_window_style |= orStyle
        
        Control.__init__(self, parent, visible=visible, enabled=enabled, pos=pos)
        for choice in choices :
            self.append(choice)
        self.set(**kw)
        self._best_size = None
        
    def move(self, l, t, w, h):
        Control.move(self, l, t, w, h+(HIRES_MULT*150))
        
    def get_count(self):
        return self._send_w32_msg(CB_GETCOUNT)
        
    def append(self, txt):
        self._send_w32_msg(CB_ADDSTRING, 0, unicode(txt))
        self._best_size = None
        
    def insert(self, i, txt):
        if not 0<=i<self.count:
            raise IndexError
        self._send_w32_msg(CB_INSERTSTRING, i, unicode(txt))
        self._best_size = None
        
    def get_selection(self):
        cursel = self._send_w32_msg(CB_GETCURSEL)
        if cursel != -1 :
            return cursel
            
    def set_selection(self, i):
        if i is None :
            self._send_w32_msg(CB_SETCURSEL, -1)
        else :
            if not 0<=i<self.count:
                raise IndexError
            self._send_w32_msg(CB_SETCURSEL, i)
        
    def drop_down(self, show=True):
        self._send_w32_msg(CB_SHOWDROPDOWN, int(show))
    
    def __getitem__(self, i):
        '''
        Returns the item at index i as a string
        '''
        if not 0<=i<self.count:
            raise IndexError
        textLength = self._send_w32_msg(CB_GETLBTEXTLEN, i)# + 1
        textBuff = create_unicode_buffer(textLength+1)
        self._send_w32_msg(CB_GETLBTEXT, i, textBuff)
        return textBuff.value
        
    def __setitem__(self, i, text):
        '''\
        Sets the choice at index i
        '''
        if not 0<=i<self.count:
            raise IndexError
        del self[i]
        self.insert(i, text)
            
    def __delitem__(self, i):
        if not 0<=i<self.count:
            raise IndexError
        self._send_w32_msg(CB_DELETESTRING, i)    
        self._best_size = None
        
    def _get_best_size(self):
        dc = GetDC(self._w32_hWnd)
        font = self._font._hFont
        SelectObject(dc, font)
        cx, cy = GetTextExtent(dc, '')
        for i in range(self.count):
            current_cx, cy = GetTextExtent(dc, self[i])
            if current_cx > cx:
                cx = current_cx
        return cx/HIRES_MULT+20, 8+cy/HIRES_MULT

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
            
class TableEvent(NotificationEvent):
    
    def __init__(self, hWnd, nMsg, wParam, lParam):
        NotificationEvent.__init__(self, hWnd, nMsg, wParam, lParam)
        nmlistview = NMLISTVIEW.from_address(lParam)
        self._index = nmlistview.iItem
        self._colindex = nmlistview.iSubItem
        self.new_state = nmlistview.uNewState
        self.changed = nmlistview.uChanged
        self.selected = bool(self.new_state)
        
    def get_index(self):
        return self._index
        
    def get_columnindex(self):
        return self._colindex
            
class TreeEvent(NotificationEvent):
    
    def __init__(self, hWnd, nMsg, wParam, lParam):
        NotificationEvent.__init__(self, hWnd, nMsg, wParam, lParam)
        self.nmtreeview = NMTREEVIEW.from_address(lParam)
        hwnd = self.nmtreeview.hdr.hwndFrom
        self._tree = hwndWindowMap[hwnd]
        
    def get_old_item(self):
        hItem = self.nmtreeview.itemOld.hItem
        if hItem != 0:
            return TreeItem(self._tree, hItem)
        
    def get_new_item(self):
        hItem = self.nmtreeview.itemNew.hItem
        if hItem != 0:
            return TreeItem(self._tree, hItem)
            
class Table(Control):
    '''
    The Table control :
    Columns are manipulated via the TableColumns instance variable columns
    Rows are manipulated via the TableRows instance variable rows
    You can get or set the text at row i, column j by indexing list[i, j] 
    '''
    _w32_window_class = WC_LISTVIEW
    _w32_window_style = WS_CHILD | LVS_REPORT #| LVS_EDITLABELS 

    _dispatchers = {"selchanged" : (NTFEventDispatcher, LVN_ITEMCHANGED, TableEvent),
                    "itemactivated" : (NTFEventDispatcher, LVN_ITEMACTIVATE, TableEvent),
                    }
    _dispatchers.update(Control._dispatchers)
    
    def __init__(self, parent, columns=[], autoadjust=False, multiple=False, has_header=True, border=True, visible=True, enabled=True, pos=(-1,-1,-1,-1), **kw):
        '''
        - columns : a list of title of the initial columns
        - autoadjust : whether the column width should be automatically adjusted
        - multiple : whether the table should allow multiple rows selection
        - has_header : whether the table displays a header for its columns
        '''
        if not multiple :
            self._w32_window_style |= LVS_SINGLESEL
        if not has_header:
            self._w32_window_style |= LVS_NOCOLUMNHEADER
        
        Control.__init__(self, parent, border=border, visible=visible, enabled=enabled, pos=pos)
        self._set_extended_style(LVS_EX_FULLROWSELECT|LVS_EX_HEADERDRAGDROP|0x10000)
        
        self.columns = TableColumns(self, columns)
        self.rows = TableRows(self)
        self._autoadjust = autoadjust
        
        self._multiple = multiple
        self.set(**kw)
        
    def _set_extended_style(self, ex_style):
        self._send_w32_msg(LVM_SETEXTENDEDLISTVIEWSTYLE, 0, ex_style)
    
    def is_multiple(self):
        return bool(self._multiple)
    
    def _insertcolumn(self, i, col):
        return self._send_w32_msg(LVM_INSERTCOLUMN, i, byref(col))

    def _setcolumn(self, i, col):
        return self._send_w32_msg(LVM_SETCOLUMN, i, byref(col))

    def _insertitem(self, item):
        self._send_w32_msg(LVM_INSERTITEM, 0, byref(item))
        if self._autoadjust:
            self.adjust_all() 
            
    def _setitem(self, item):
        self._send_w32_msg(LVM_SETITEM, 0, byref(item))
        if self._autoadjust:
            self.adjust_all() 
            
    def _getitem(self, i, j):
        item = LVITEM()
        item.mask = LVIF_TEXT | LVIF_PARAM
        item.iItem = i
        item.iSubItem = j
        item.pszText = u" "*1024

        item.cchTextMax = 1024
        self._send_w32_msg(LVM_GETITEM, 0, byref(item))
        return item
        
    def adjust_all(self):
        '''
        Adjusts all columns in the list
        '''
        for i in range(len(self.columns)):
            self.columns.adjust(i)
    
    def __getitem__(self, pos):
        '''
        list[i, j] -> Returns the text at the row i, column j
        '''
        i, j = pos
        if not 0 <= i < len(self.rows):
            raise IndexError
        if not 0 <= j < len(self.columns):
            raise IndexError
                
        item = self._getitem(i, j)
        return item.pszText
        
    def __setitem__(self, pos, val):
        '''
        list[i, j] = txt -> Set the text at the row i, column j to txt
        '''
        i, j = pos
        if not 0 <= i < len(self.rows):
            raise IndexError
        if not 0 <= j < len(self.columns):
            raise IndexError
        
        item = LVITEM()
        item.mask = LVIF_TEXT 
        item.iItem = i
        item.iSubItem = j
        item.pszText = unicode(val)
        self._setitem(item)
        return item
        
    def delete_all(self):
        '''
        Removes all rows of the list
        '''
        del self.rows._data[:]
        self._send_w32_msg(LVM_DELETEALLITEMS)
        if self._autoadjust:
            self.adjust_all() 

        


class TreeItem(GuiObject):
    
    def __init__(self, tree, hItem):
        '''
        Do not use this constructor directly.
        Use Tree and TreeItem methods instead.
        '''
        self._tree = tree
        self._hItem = hItem
        
    def __eq__(self, other):
        return (self._tree is other._tree) \
            and (self._hItem == other._hItem)
        
    def __len__(self):
        for i, item in enumerate(self): 
            pass
        try :
            return i+1
        except NameError:
            return 0
            
    
    def append(self, text, data=None, image=0, selected_image=0):
        '''
        Adds a child item to the TreeItem. 
        '''
        
        return self._tree._insertitem(self._hItem, TVI_LAST, text, data, image, selected_image)
    
    def insert(self, i, text, data=None, image=0, selected_image=0):
        
        if i < 0 :
            raise IndexError
            
        if i == 0:
            return self._tree._insertitem(self._hItem, TVI_FIRST, text, data, image, selected_image)
        hAfter = self[i-1]
        return self._tree._insertitem(self._hItem, hAfter, text, data, image, image_selected)
    
    def get_parent(self):
        parenthItem = self._tree._send_w32_msg(TVM_GETNEXTITEM, TVGN_PARENT, self._hItem)
        if parenthItem :
            return TreeItem(self._tree, parenthItem)
    
    def expand(self):
        self._tree._send_w32_msg(TVM_EXPAND, TVE_EXPAND, self._hItem)
    
    def collapse(self):
        self._tree._send_w32_msg(TVM_EXPAND, TVE_COLLAPSE, self._hItem)
        
    def toggle(self):
        self._tree._send_w32_msg(TVM_EXPAND, TVE_TOGGLE, self._hItem)
    
#    def isexpanded(self):

#        pass
        
    def select(self):
        self._tree._send_w32_msg(TVM_SELECTITEM, TVGN_CARET, self._hItem)
    
#    def isselected(self):

#        pass
        
    def ensure_visible(self):
        self._tree._send_w32_msg(TVM_ENSUREVISIBLE, 0, self._hItem)
         
    def __getitem__(self, i):
        if i < 0:
            raise IndexError
        for j, item in enumerate(self):
            if j==i :
                return item
        raise IndexError
        
    def get_text(self):
        item = TVITEM()
        item.hItem = self._hItem
        item.mask = TVIF_TEXT
        item.pszText = u" "*1024
        item.cchTextMax = 1024
        self._tree._getitem(item)
        return item.pszText
        
    def set_text(self, txt):
        item = TVITEM()
        item.mask  = TVIF_TEXT
        item.hItem = self._hItem
        item.pszText = unicode(txt)
        return self._tree._setitem(item)
        
    doc_text = "The text of the TreeItem as a string"
    
    def get_data(self):
        item = TVITEM()
        item.hItem = self._hItem
        item.mask  = TVIF_PARAM
        self._tree._getitem(item)
        return self._tree._data[item.lParam][0]
        
    def set_data(self, data):
        olddata = self.data
        self._tree._data.decref(olddata)
        param = self._tree._data.addref(data)
        item = TVITEM()
        item.hItem = self._hItem
        item.mask  = TVIF_PARAM
        item.lParam = param
        self._tree._setitem(item)
        
    doc_data = "The data of the TreeItem as any python object"
        
    def get_image(self):
        item = TVITEM()
        item.mask  = TVIF_IMAGE
        item.hItem = self._hItem
        self._tree._getitem(item)
        return item.iImage
        
    def set_image(self, i):
        item = TVITEM()
        item.mask  = TVIF_IMAGE
        item.hItem = self._hItem
        item.iImage = i
        self._tree._setitem(item)
        
    def get_selected_image(self):
        item = TVITEM()
        item.mask  = TVIF_SELECTEDIMAGE
        item.hItem = self._hItem
        self._tree._getitem(item)
        return item.iSelectedImage
        
    def set_selected_image(self, i):
        item = TVITEM()
        item.mask  = TVIF_SELECTEDIMAGE
        item.hItem = self._hItem
        item.iSelectedImage = i
        self._tree._setitem(item)
        
    def _removedata(self):
        data = self.data
        self._tree._data.decref(data)
        for child in self:
            child._removedata()
        
    def remove(self):
        '''
        Removes the TreeItem instance and all its children from its tree. 
        '''
        self._removedata()
        self._tree._send_w32_msg(TVM_DELETEITEM, 0, self._hItem)
    
    def __iter__(self):
        return _treeitemiterator(self) 
        
    def __delitem__(self, i):
        '''
        del item[i] -> removes the child at index i
        '''
        
        self[i].remove()

    
def _treeitemiterator(treeitem):
    hitem = treeitem._tree._send_w32_msg(TVM_GETNEXTITEM, TVGN_CHILD, treeitem._hItem)
    while hitem :
        yield TreeItem(treeitem._tree, hitem)
        hitem = treeitem._tree._send_w32_msg(TVM_GETNEXTITEM, TVGN_NEXT, hitem)
        
class _TreeDataHolder(dict):
    
    def addref(self, obj):
        idobj = id(obj)
        if idobj in self:
            objj, refs = self[idobj]
            assert objj is obj
            self[idobj] = obj, refs+1
        else :
            self[idobj] = (obj, 1)
        #print dict.__str__(self)
        return idobj
    
    def decref(self, obj):
        idobj = id(obj)
        if idobj in self:
            objj, refs = self[idobj]
            assert objj is obj
            refs -= 1 
            if refs == 0 :
                del self[idobj]
            else :
                self[idobj] = obj, refs
            
            
class Tree(Control):
    '''
    The tree control :
    Insert or get roots with the insertroot and getroots method
    Subsequent changes to the tree are made with the TreeItem instances
    '''
    _w32_window_class = WC_TREEVIEW
    _w32_window_style = WS_CHILD | WS_TABSTOP
                       
    _dispatchers = {"selchanged" : (NTFEventDispatcher, TVN_SELCHANGED, TreeEvent),
                    }
    _dispatchers.update(Control._dispatchers)
    
    def __init__(self, parent, border=True, visible=True, enabled=True, pos=(-1,-1,-1,-1), has_buttons=True, has_lines=True):
        or_style = 0
        if has_buttons:
            or_style |= TVS_HASBUTTONS
        if has_lines:
            or_style |= TVS_LINESATROOT|TVS_HASLINES
            
        self._w32_window_style |= or_style
        
        Control.__init__(self, parent, border=border, visible=visible, enabled=enabled, pos=pos)
        self._roots = []
        self._data = _TreeDataHolder()
        
    def _getitem(self, item):
        self._send_w32_msg(TVM_GETITEM, 0, byref(item))
        
    def _setitem(self, item):
        self._send_w32_msg(TVM_SETITEM, 0, byref(item))
        
    def _insertitem(self, hParent, hInsertAfter, text, data, image, image_selected):
        #item.mask = TVIF_TEXT | TVIF_PARAM
        item = TVITEM(text=text, param=self._data.addref(data), image=image, selectedImage=image_selected)
        #print 'param :', item.lParam
        insertStruct = TVINSERTSTRUCT()
        insertStruct.hParent = hParent
        insertStruct.hInsertAfter = hInsertAfter
        insertStruct.item = item
        hItem = self._send_w32_msg(TVM_INSERTITEM, 0, byref(insertStruct))
        return TreeItem(self, hItem)
            
    def add_root(self, text, data=None, image=0, selected_image=0):
        '''\
        Insert a new root in the tree
        - text : the text of the root
        - data : the data bound to the root
        Returns the TreeItem instance associated to the root
        '''

        
        root = self._insertitem(TVI_ROOT, TVI_ROOT, text, data, image, selected_image)
        self._roots.append(root)
        return root
    
    def get_roots(self):
        '''\
        Returns the list of roots in the tree
        '''  
        return self._roots

    def delete_all(self):
        '''\
        Deletes all items in the tree
        '''
        for root in self._roots:
            root.remove()
        self._roots = []
    
    def get_selection(self):
        '''\
        Returns a TreeItem instance bound
        to the current selection or None
        '''
        hItem = self._send_w32_msg(TVM_GETNEXTITEM, TVGN_CARET, 0)
        if hItem > 0:
            return TreeItem(self, hItem)
        
    def set_image_list(self, il):
        self._send_w32_msg(TVM_SETIMAGELIST, 0, il._hImageList)
        
class Progress(Control):
    _w32_window_class = PROGRESS_CLASS
    
    def __init__(self, parent, style="normal", orientation="horizontal", range=(0,100), visible=True, enabled=True, pos=(-1,-1,-1,-1)):
        if style not in ["normal", "smooth"]:
            raise ValueError('style not in ["normal", "smooth"]')
        if orientation not in ['horizontal', 'vertical']:
            raise ValueError("orientation not in ['horizontal', 'vertical']")
        
        self._orientation = orientation 
        orStyle = 0
        if style == "smooth" :
            orStyle |= PBS_SMOOTH
        if orientation == "vertical" :
            orStyle |= PBS_VERTICAL
        
        self._w32_window_style |= orStyle
        Control.__init__(self, parent, visible=visible, enabled=enabled, pos=pos)
        self.range = range
            
    def set_range(self, range):
        nMinRange, nMaxRange = range
        if nMinRange > 65535 or nMaxRange > 65535:
            return self._send_w32_msg(PBM_SETRANGE32, nMinRange, nMaxRange)
        else:
            return self._send_w32_msg(PBM_SETRANGE, 0, MAKELPARAM(nMinRange, nMaxRange))
            
    def get_range(self):
        minrange = self._send_w32_msg(PBM_GETRANGE, 1)
        maxrange = self._send_w32_msg(PBM_GETRANGE, 0)
        return minrange, maxrange
    
    doc_range = "The range of the progress as a tuple (min, max)"
    
    def set_value(self, newpos):
        return self._send_w32_msg(PBM_SETPOS, newpos, 0)

    def get_value(self):
        return self._send_w32_msg(PBM_GETPOS, 0, 0)
    
    doc_value = "The position of the progress as an int"
    
    def get_best_size(self):
        if self._orientation == 'horizontal':
            return None, 20
        else:
            return 20, None
            
class ScrollEvent(Event):
    def __init__(self, hWnd, nMsg, wParam, lParam):
        Event.__init__(self, lParam, nMsg, wParam, lParam)

class Slider(Control):
    _w32_window_class = TRACKBAR_CLASS
    _w32_window_style = WS_CHILD | TBS_AUTOTICKS | TBS_TOOLTIPS

    _dispatchers = {"_hscroll" : (MSGEventDispatcher, WM_HSCROLL, ScrollEvent),
                    "_vscroll" : (MSGEventDispatcher, WM_VSCROLL, ScrollEvent),
                    "update" : (CustomEventDispatcher,)
                    }
    _dispatchers.update(Control._dispatchers)
                    
                        
    def __init__(self, parent, style="horizontal", value=0, range=(0,10), visible=True, enabled=True, pos=(-1,-1,-1,-1)):
        assert style in  ['horizontal', 'vertical']
        if style == 'horizontal' :
            self._w32_window_style |= TBS_HORZ
        else :
            self._w32_window_style |= TBS_VERT
        self._style = style
        Control.__init__(self, parent, visible=visible, enabled=enabled, pos=pos)
        
        self.bind(_hscroll=self._on_hscroll, 
                  _vscroll=self._on_vscroll)
                  
        clsStyle = GetClassLong(self._w32_hWnd, GCL_STYLE)
        clsStyle &= ~CS_HREDRAW
        clsStyle &= ~CS_VREDRAW
        SetClassLong(self._w32_hWnd, GCL_STYLE, clsStyle)
        
        self.range = range
        self.value = value
    def _on_hscroll(self, ev):
        self.events['update'].call(ev)
        
    def _on_vscroll(self, ev):
        self.events['update'].call(ev)
        
    def get_range(self):
        min = self._send_w32_msg(TBM_GETRANGEMIN)
        max = self._send_w32_msg(TBM_GETRANGEMAX)
        return min, max
        
    def set_range(self, range):
        min, max = range
        self._send_w32_msg(TBM_SETRANGE, 0, MAKELPARAM(min, max))
    
    doc_range = "The range of the slider as a tuple (min, max)"
        
    def get_value(self):
        return self._send_w32_msg(TBM_GETPOS)
        
    def set_value(self, pos):
        self._send_w32_msg(TBM_SETPOS, 1, pos)
    
    doc_value = "The position of the slider as an int"
    
#    def get_pagesize(self):
#        pass
#        
#    def set_pagesize(self, size):
#        pass

    def get_best_size(self):
        if self._style == 'horizontal':
            return None, 25
        else:
            return 25, None


class _TabControl(Control):
    _w32_window_class = WC_TABCONTROL
    #_w32_window_style_ex = 0x10000
    _w32_window_style = WS_VISIBLE | WS_CHILD | TCS_BOTTOM | WS_CLIPSIBLINGS 
    _dispatchers = {"_selchanging" : (NTFEventDispatcher, TCN_SELCHANGING),
                    "_selchange" : (NTFEventDispatcher, TCN_SELCHANGE),
                    }
    _dispatchers.update(Control._dispatchers)
                    
    def __init__(self, parent, pos=(-1,-1,-1,-1)):
        Control.__init__(self, parent, pos=pos)
        self._send_w32_msg(CCM_SETVERSION, COMCTL32_VERSION, 0)
#        self.events['_selchanging'].bind(self._onchanging)
#        self.events['_selchange'].bind(self._onchange)
#        self.events['size'].bind(self._onsize)
        
        
        SetWindowPos(self._w32_hWnd, 0, 0, 0, 0, 0, 1|2|4|20)
        self.update()
        
    def _insertitem(self, i, item):
        self._send_w32_msg(TCM_INSERTITEM, i, byref(item))

    def _getitem(self, index, mask):
        item = TCITEM()
        item.mask = mask
        if self._send_w32_msg(TCM_GETITEM, index, byref(item)):
            return item
        else:
            raise "error"
            
    def _adjustrect(self, fLarger, rc):
        lprect = byref(rc)
        self._send_w32_msg(TCM_ADJUSTRECT, fLarger, lprect) 
           
    def _resizetab(self, tab):
        if tab:
            rc = self.client_rect
            self._adjustrect(0, rc)
            tab.move(rc.left-(2*HIRES_MULT), rc.top-(2*HIRES_MULT), rc.width, rc.height)
            #tab.move(rc.left, rc.top, rc.width, rc.height)
            #SetWindowPos(tab._w32_hWnd, 0, rc.left, rc.top, rc.width, rc.height, 4)
            SetWindowPos(self._w32_hWnd, tab._w32_hWnd, rc.left, rc.top, rc.width, rc.height, 1|2)
            
class NoteBook(Frame):
    def __init__(self, parent, visible=True, enabled=True, pos=(-1,-1,-1,-1)):
        Frame.__init__(self, parent, visible=visible, enabled=enabled, pos=pos)
        self._tc = _TabControl(self)
        self._tc.bind(_selchanging=self._onchanging, 
                      _selchange=self._onchange,
                      size=self._onsize)
                      
        sizer = VBox((-2,-2,-2,0))
        sizer.add(self._tc)
        self.sizer = sizer
        
    def _onchanging(self, event):
        tab = self[self.selection]
        if tab :
            tab.hide()
        
    def _onchange(self, event):
        tab = self[self.selection]
        if tab :
            self._tc._resizetab(tab)
            tab.show(True)
    
    def _onsize(self, event):
        InvalidateRect(self._w32_hWnd)#, 0, 1)
        if self.selection is not None:
            tab = self[self.selection]
            self._tc._resizetab(tab)
        event.skip()
        
    def get_count(self):
        return self._tc._send_w32_msg(TCM_GETITEMCOUNT)
     
    doc_count = "The number of tab in the notebook"
    
    def append(self, title, tab):
        '''
        Adds a new tab to the notebook
        - title : the title of the tab
        - tab : the child window 
        '''
        self.insert(self.count, title, tab)
        
    def insert(self, i, title, tab):
        '''
        Inserts a new tab in the notebook at index i
        - title : the title of the tab
        - tab : the child window 
        '''
        if not 0<=i<=self.count:
            raise IndexError
        item = TCITEM()
        item.mask = TCIF_TEXT | TCIF_PARAM
        item.pszText = title
        item.lParam = tab._w32_hWnd
        self._tc._insertitem(i, item)
        
        self.selection = i
        return i
        
    def __getitem__(self, i):
        '''
        notebook[i] -> Returns the child window at index i
        '''
        if not 0<=i<self.count:
            raise IndexError
        item = self._tc._getitem(i, TCIF_PARAM)
        return hwndWindowMap.get(item.lParam, None)
        
    def __delitem__(self, i):
        '''
        del notebook[i] -> Removes the tab at index i
        '''
        if not 0<=i<self.count:
            raise IndexError
            
        self._tc._send_w32_msg(TCM_DELETEITEM, i)
        if i == self.count:
            i -= 1
        self._tc._send_w32_msg(TCM_SETCURSEL, i)
        self._onchange(None)
        
    def get_selection(self):
        sel = self._tc._send_w32_msg(TCM_GETCURSEL)
        if sel != -1:
            return sel
        
    def set_selection(self, i):
        if not 0<=i<self.count:
            raise IndexError
        if i == self.selection : return
        self._onchanging(None)
        self._tc._send_w32_msg(TCM_SETCURSEL, i)
        self._onchange(None)
        
    doc_selection =  "The current index of the selected tab"
    
    def set_font(self, font):
        self._tc.font = font
    
    def get_font(self, font):
        return self._tc.font
        
class UpDown(Control):
    _w32_window_class = "msctls_updown32"
    _w32_window_style = WS_VISIBLE | WS_CHILD | UDS_SETBUDDYINT | 0x20 | 8
    _dispatchers = {'deltapos' : (NTFEventDispatcher, UDN_DELTAPOS)}
    _dispatchers.update(Control._dispatchers)
    
    def __init__(self, *args, **kw):
        kw['tab_stop'] = False
        Control.__init__(self, *args, **kw)
        
    def set_buddy(self, buddy):
        self._send_w32_msg(UDM_SETBUDDY, buddy._w32_hWnd)
    
    def set_range(self, range):
        low, high = range
        self._send_w32_msg(UDM_SETRANGE32, int(low), int(high))
        
    def get_best_size(self):
        return 14, 20
        
    def _get_pos(self):
        err = c_ulong()
        ret = self._send_w32_msg(UDM_GETPOS32, 0, byref(err))
        return ret
        
    def _set_pos(self, pos):
        self._send_w32_msg(UDM_SETPOS32, 0, pos)
        
class BusyCursor(GuiObject):
    def __init__(self):
        SetCursor(LoadCursor(0, 32514))
        
    def __del__(self):
        SetCursor(0)
