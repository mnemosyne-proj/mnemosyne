# ***********************************************************************
#
#  Font  -function
#
#  Application ( wx.PySimpleApp )
#  CeMenu      ( wx.Menu        )
#
#   _Message ()
#      Message  -var
#   _FileDialog ()
#      FileDialog  -var
#
#  Frame            ( wx.Panel    )
#  NoteBook         ( wx.Notebook )
#  _Calendar_Dialog ( wx.Dialog   )
#  Date             ( Frame       )
#
#  _gui_extension
#     Label         ( wx.StaticText,          _gui_extension )
#     Combo         ( wx.ComboBox,            _gui_extension )
#     Edit          ( wx.TextCtrl,            _gui_extension )
#     Button        ( wx.Button, wx.CheckBox, _gui_extension )
#     RadioGroup    (                         _gui_extension )
#       RadioButton ( wx.RadioButton                         )
#     Spin          ( wx.SpinCtrl,            _gui_extension )
#     Html          ( html.HtmlWindow,        _gui_extension )
#     Slider        ( wx.Slider,              _gui_extension )
#     Progress      ( wx.Gauge,               _gui_extension )
#     Table         ( gridlib.Grid,           _gui_extension )
#
#  _Table_Columns ( object )
#  _Table_Rows    ( object )
#
#  VBox ( wx.BoxSizer )
#  HBox ( wx.BoxSizer )
#  TBox ( wx.GridSizer )
#
#?? Spacer ( x, y _
#
# ***********************************************************************
#
#  gui.Object
#    gui.RadioGroup
#    gui.Window
#      gui.Frame
#        gui.Notebook
#        gui.CEFrame
#      gui.Control
#        gui.Label
#        gui.Button
#        gui.RadioButton
#        gui.Edit
#        gui.List
#        gui.Combo
#        gui.Slider
#        gui.Progress
#        gui.Spin
#        gui.Date
#        gui.Time
#        gui.Html
#        gui.Table
#  gui.TableColumns
#  gui.TableRows
#  gui.Event
#  gui.Font
#  gui.Menu
#    gui.PopupMenu
#
# ***********************************************************************


import wx
from   inspect  import isclass
import wx.grid as gridlib
import wx.html as  html
import wx.calendar as calen

# ***********************************************************************
# User Settings on the mobile
# ***********************************************************************
User_FontSize   = 7    # ?, 8, 10, ?, ?
User_ScreenSize = ( 240 + 6, 320 )

Color_HighLight = wx.Colour ( 200, 230, 200 )
Color_CMD       = wx.Colour ( 100, 115, 100 )
# ***********************************************************************


_SIPP_List = []

# ***********************************************************************
# Font settings,
# in wxPython the color is not part of the font,
# but should be set as the ForegroundColor of the control
# So here we return a tupple of (font, color)
# ***********************************************************************
# the first def is the right one, but
# to mimick a bug in PPyGui we temporary use "size = 9"
#def Font ( size = None, color = None, bold = False ) :
def Font ( size = 9, color = None, bold = False ) :
    font = None

    if bold : weight = wx.BOLD
    else    : weight = wx.NORMAL

    if size :
      font = wx.Font ( size, wx.SWISS,
                       wx.NORMAL, weight )
    if color :
      color = wx.Color ( *color )

    return ( font, color )
# ***********************************************************************


# ***********************************************************************
# This event extension translates from PPyGui to wxPython
#   bind         ==> Bind
#   PPyGui event ==> wxPython event
#   event += event.window
# in the control's __init__,
# the binding to the correct wxPython should be done,
# e.g. for a Label :
#    self.Bind ( wx.EVT_LEFT_DOWN, self._OnChange )
# ***********************************************************************
class _gui_extension ( object ) :

  SIPP_Control = 1    # supports

  def __init__ ( self, parent = None, font = None ) :
    self.parent = parent
    self._OnChange_User = None
    self.extra_setters = {}
    self.extra_getters = {}

    if font :
      self._Set_Font ( font )

    # *********************************************************
    # Create some function, for which case of name differs
    # *********************************************************
    self.show    = self.Show
    self.hide    = self.Hide
    self.close   = self.Close
    self.destroy = self.Destroy

    # *********************************************************
    # extra setters / getters for all controls
    # *********************************************************
    self._add_attrib ( '_id',  None,           self.GetId )
    self._add_attrib ( 'font', self._Set_Font, None )

    # *********************************************************
    # *********************************************************
    if self.SIPP_Control :
      self.Bind ( wx.EVT_SET_FOCUS, self._On_Focus )

  # *********************************************************
  # *********************************************************
  def _On_Focus ( self, event ) :
    top = wx.GetTopLevelParent ( self )
    top.KB_img.Show ( self.SIPP_Control == 2 )
    top.SendSizeEvent ()
    event.Skip ()



  # *********************************************************
  # *********************************************************
  def _Set_Font ( self, font ):
    for item in font :
      if isinstance ( item, wx.Colour ) :
        self.SetForegroundColour ( item )
      elif isinstance ( item, wx.Font ) :
        self.SetFont ( item )
    self.Refresh ()

  # *********************************************************
  # *********************************************************
  def _OnChange ( self, event ) :
    if self._OnChange_User :
      ID = event.GetId ()
      event.id = ID
      event.window = self.parent.FindWindowById ( ID )
      self._OnChange_User ( event )
    print((self, isinstance ( self, wx.ComboBox )))
    #event.Skip ()

  # *********************************************************
  # *********************************************************
  def bind ( self, **kwargs ) :
    for item in kwargs :
      self._OnChange_User = kwargs [item]

  # *********************************************************
  # *********************************************************
  def focus ( self ) :
    self.SetFocus ()

  # *********************************************************
  # *********************************************************
  def _add_attrib ( self, text, setter = None, getter = None ) :
    if setter :
      self.extra_setters [ text ] = setter
    if getter :
      self.extra_getters [ text ] = getter

  # *********************************************************
  # always called instead of the normal mechanism
  # *********************************************************
  def __setattr__ ( self, attr, value ) :
    if attr in self.extra_setters :
      self.extra_setters [ attr ] ( value )
    else :
      self.__dict__[attr] = value

  # *********************************************************
  # only called when not found with the normal mechanism
  # *********************************************************
  def __getattr__ ( self, attr ) :
    try :
      if attr in self.__dict__['extra_getters'] :
        return self.extra_getters [ attr ] ( )
    except :
      return []
# ***********************************************************************


# ***********************************************************************
# PPyGUI has the possibility to create the MainFrame,
# by adding a parameter to the application constructor.
# PPyGUI has a method run, wxPython not.
# ***********************************************************************
class Application ( wx.PySimpleApp ) :
  def __init__ ( self, MainFrame = None ) :
    wx.PySimpleApp.__init__ ( self )
    if MainFrame :
      self.mainframe = MainFrame ()

  def run ( self ) :
    self.MainLoop ()
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class CeMenu ( wx.Menu ) :
  def __init__ ( self ) :
    wx.Menu.__init__ ( self )

  def append ( self, text, callback = None ) :
    item = self.Append ( -1, text )
    self.Bind ( wx.EVT_MENU, callback, item )
# ***********************************************************************


# ***********************************************************************
# Under windows you can't specify the position of the dialog
#   (always screen center)
# ***********************************************************************
class _Message ( object ) :
  # *********************************************************
  # the user dialogs
  # *********************************************************
  def ok ( self, *args, **kwargs ) :
    return self._msg ( wx.OK, *args, **kwargs )

  def okcancel ( self, *args, **kwargs ) :
    return self._msg ( wx.OK | wx.CANCEL, *args, **kwargs )

  def yesno ( self, *args, **kwargs ) :
    return self._msg ( wx.YES_NO, *args, **kwargs )

  def yesnocancel ( self, *args, **kwargs ) :
    return self._msg ( wx.YES_NO | wx.CANCEL, *args, **kwargs )

  # *********************************************************
  # base functionality for all dialogs
  # *********************************************************
  def _msg ( self,
             style ,
             caption,
             message = '',
             icon    = '',
             parent  = None ) :
    if   icon == 'info' :
      style |= wx.ICON_INFORMATION
    elif icon == 'question' :
      style |= wx.ICON_QUESTION
    elif icon == 'warning' :
      style |= wx.ICON_WARNING
    else :
      style |= wx.ICON_ERROR
    dialog = wx.MessageDialog (  parent, message, caption,
                                 style = style )
    result = dialog.ShowModal()
    dialog.Destroy ()
    if result == wx.ID_OK :
      answer = 'ok'
    elif result == wx.ID_YES :
      answer = 'yes'
    elif result == wx.ID_NO :
      answer = 'no'
    elif result == wx.ID_CANCEL :
      answer = 'cancel'
    else :
      answer = 'unknown'
      
    return answer
# ***********************************************************************

# ***********************************************************************
# Here we create a global message instance
# ***********************************************************************
Message = _Message ()
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class _FileDialog ( object ):
  # *********************************************************
  # the user dialogs
  # *********************************************************
  def open ( self ) :
    return self._dialog ( wx.FD_OPEN )
  def save ( self ) :
    return self._dialog ( wx.FD_SAVE )

  # *********************************************************
  # base functionality for all dialogs
  # *********************************************************
  def _dialog ( self, style ) :
    # NOTE: the second parameter is essential to get right header !!
    dialog = wx.FileDialog ( None, '', style = style )
    if dialog.ShowModal () == wx.ID_OK:
      File =  dialog.GetPath()
    else:
      File = None

    dialog.Destroy ()
    return File
# ***********************************************************************

# ***********************************************************************
# Here we create a global FileDialog instance
# ***********************************************************************
FileDialog = _FileDialog ()
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class SIPPref ( object ) :
  def __init__ ( self, parent ) :
    _SIPP_List.append ( parent )
    pass
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class _CB_Action ( object ) :
  def __init__ ( self , Button = None ) :
    self._Button = Button

  # *********************************************************
  # always called instead of the normal mechanism
  # *********************************************************
  def __setattr__ ( self, attr, value ) :
    if attr == 'text' :
      self._Button.SetLabel ( value )
    else :
      self.__dict__[attr] = value
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class CeFrame ( wx.MiniFrame ):
  def __init__ ( self, title,
                 action = ( '', None ),
                 menu   =   '' ) :
    wx.MiniFrame.__init__ ( self, None, -1, title,
                            size = User_ScreenSize,
                            style = wx.DEFAULT_FRAME_STYLE - wx.RESIZE_BORDER )
    # get all available fonts
    fonts = wx.FontEnumerator ()
    fonts.EnumerateFacenames ()
    fontList = fonts.GetFacenames ()#.sort()
    mobile_faces = ( 'Tahoma', 'Segoe', 'Nina')
    for face in mobile_faces :
      if face in fontList :
        break
    else :
      face = ''
    Mobile_Font = wx.Font ( User_FontSize, wx.SWISS,
                            wx.NORMAL, wx.NORMAL,
                            faceName = face )
    self.SetFont ( Mobile_Font )
    self.SetBackgroundColour ( wx.WHITE )

    # *********************************************************
    # Create the Mobile soft buttons
    # *********************************************************
    H = 25
    self.tb = wx.Panel ( self, -1, size = ( -1, H ) )
    sizer = wx.BoxSizer ( wx.HORIZONTAL )

    font = wx.Font ( 9, wx.SWISS, wx.NORMAL, wx.BOLD )

    Action_Button = wx.Button ( self.tb, -1, action [0], size = ( -1, H ) )
    Action_Button.SetFont ( font )
    Action_Button.SetBackgroundColour ( Color_CMD )
    sizer.Add ( Action_Button, 1 )
    Action_Button.Bind ( wx.EVT_BUTTON, action[1] )
    self.cb_action = _CB_Action ( Action_Button )

    self.KB = wx.Button ( self.tb, -1, 'KB', size = ( -1, H ) )
    self.KB.SetFont ( font )
    self.KB.SetBackgroundColour ( Color_CMD )
    sizer.Add ( self.KB, 1 )
    self.KB.Bind ( wx.EVT_BUTTON, self._On_KB_Toggle )

    Menu_Button = wx.Button ( self.tb, -1, menu, size = ( -1, H ) )
    Menu_Button.SetFont ( font )
    Menu_Button.SetBackgroundColour ( Color_CMD )
    sizer.Add ( Menu_Button, 1 )
    Menu_Button.Bind ( wx.EVT_BUTTON, self._On_Show_Popup )

    self.SetSizer ( sizer )

    # *********************************************************
    # Create the KB image
    # *********************************************************
    self.KB_img = wx.Panel ( self, -1, size = (-1,20) )
    import os
    p, f = os.path.split (__file__)
    image1 = wx.Image ( os.path.join (p, 'Image_kb1.png' ),
                        wx.BITMAP_TYPE_PNG).ConvertToBitmap ()
    image2 = wx.Image ( os.path.join (p, 'Image_kb2.png' ),
                        wx.BITMAP_TYPE_PNG).ConvertToBitmap ()
    self.kb1 = wx.StaticBitmap ( self.KB_img, -1, image1, (0,0),
                      ( image1.GetWidth (), image1.GetHeight () ) )
    self.kb2 = wx.StaticBitmap ( self.KB_img, -1, image2, (0,0),
                      ( image2.GetWidth (), image2.GetHeight () ) )
    self.kb1.Bind ( wx.EVT_LEFT_DOWN, self._On_KB )
    self.kb2.Bind ( wx.EVT_LEFT_DOWN, self._On_KB )
    self.kb1.Show ( True )
    self.kb2.Show ( False )
    self.KB_img.Show ( True ) #False )

    # *********************************************************
    # Create the popup menu
    # *********************************************************
    self.cb_menu = CeMenu ()

    # *********************************************************
    # Create some function, for which case of name differs
    # *********************************************************
    self.show    = self.Show
    self.hide    = self.Hide
    self.close   = self.Close
    self.destroy = self.Destroy

    self.Bind ( wx.EVT_SET_FOCUS, self._OnFocus )

    self.Show ( True )

  def _OnFocus ( self, event ) :
    pass #print 'FOCUS' #, dir ( event)

  # *********************************************************
  # A key on the soft keyboard is pressed
  # *********************************************************
  def _On_KB ( self, event ) :
    x,y = event.GetPosition ()
    if ( x < 19 ) and ( y < 19 ) :
      self.kb1.Show ( not ( self.kb1.IsShown () ) )
      self.kb2.Show ( not ( self.kb2.IsShown () ) )
    else :
      import SendKeys
      x0 = ( 19, 25, 30, 34, 22 )
      kar = ( ( '\x001234567890-=\0xx\0xx' ),
              ( '\tqwertyuiop[]]' ),
              ( '\x00asdfghjkl;\'\r\r' ),
              ( '\x00zxcvbnm,./\r\r\r' ),
              ( '\x00@`\\     \x00\x00\x00\x00\x00'))

      # determine the row and col index
      x, y = event.GetPosition ()
      row = y / 16
      xfirst = x0 [ row ]

      # top row has a little bit smaller keys
      if row == 0 :
        col = 1 + ( x - xfirst ) / 17
      else :
        col = 1 + ( x - xfirst ) / 18
      col = max ( 0, col )
      key = kar[row][col]

      # if key = 0, we need to determine a special key
      if ord ( key )  == 0 :
        if row == 4 :
          if col == 11 : key = '{LEFT}'
          
      # now send the key to windows
      SendKeys.SendKeys ( key ,
                          with_spaces = True,
                          with_tabs   = True )

  # *********************************************************
  # Toggle the visibility of the soft keyboard
  # *********************************************************
  def _On_KB_Toggle ( self, event ) :
    self.KB_img.Show ( not ( self.KB_img.IsShown () ) )
    self.SendSizeEvent ()

  # *********************************************************
  # always called instead of the normal mechanism
  # *********************************************************
  def __setattr__ ( self, attr, value ) :
    if   attr == 'sizer' :
      # add the Keyboard to the bottom of the page
      value.Add ( self.KB_img, 0 , wx.EXPAND | wx.ALL )
      #self.SetSizer ( value )

      # add the toolbar to the bottom of the page
      value.Add ( self.tb, 0 , wx.EXPAND | wx.ALL )
      self.SetSizer ( value )

      self.SendSizeEvent ()

      #self.Fit() # Resizez the frame !!
      self.Refresh()
      #self.ClearBackground()
      ##wx.MiniFrame.
      #self.SetDoubleBuffered ( True )
      #self.Restore()
      #self.UpdateWindowUI()
      #self.ClearBackground()
      #self.Update()

    else :
      self.__dict__[attr] = value

  # *********************************************************
  # *********************************************************
  def _On_Show_Popup ( self, event ) :
    # calculate size of the popup
    dc = wx.ScreenDC()
    items = self.cb_menu.MenuItems
    w = 0
    h = 53
    for item in items :
      label = self.cb_menu.GetLabel ( item.GetId () )
      w1, h1 = dc.GetTextExtent ( label )
      w = max ( w, w1 )
      h += h1 + 1
    w = User_ScreenSize [0] - w - 28
    h = User_ScreenSize [1] - h

    self.PopupMenu ( self.cb_menu , pos = (w,h))
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class Frame ( wx.Panel ):
  def __init__ ( self, parent ):
    self.parent = parent
    wx.Panel.__init__( self, parent )
    self.SetBackgroundColour ( wx.WHITE )

    # *********************************************************
    # Create some function, for which case of name differs
    # *********************************************************
    self.show    = self.Show
    self.hide    = self.Hide
    self.close   = self.Close
    self.destroy = self.Destroy

    #self.Bind ( wx.EVT_SET_FOCUS, self._OnFocus )
  # *********************************************************
  # *********************************************************
  #def _OnFocus ( self, event ) :
  #  print 'PANEL FOCUS'#, dir ( event)

  # *********************************************************
  # always called instead of the normal mechanism
  # *********************************************************
  def __setattr__ ( self, attr, value ) :
    if   attr == 'sizer' :
      self.SetSizer ( value )
      self.SendSizeEvent ()
      self.Refresh ()
    else :
      self.__dict__[attr] = value
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class NoteBook ( wx.Notebook, _gui_extension  ) :
  def __init__ ( self, parent = None ):
    wx.Notebook.__init__( self, parent, -1, style = wx.BK_BOTTOM )

    self.Selected_Page = 0
    
    # make methods available with a different name
    self.set_selection = self.SetSelection
    #self.get_selection = self.GetSelection

    _gui_extension.__init__ ( self, parent )

    # make some methods also available as property (attribute)
    self._add_attrib ( 'selection', self.SetSelection, self.GetSelection    )

    # flag for the first append to bind the _onchange
    # _onchange is taken over because there is no event !!
    self._Events_Bound = False

    """
    # used in _onchange
    class _Nothing ( object ) :
      def _resizetab ( self, tab ) :
        pass
    self._tc = _Nothing ()
    """


  def append ( self, page_name, klass ) :
    if isclass ( klass ) :
      page = klass ( self )
    else :
      page = klass
    self.AddPage ( page, page_name )
    
    # SPECIAL TRICK, BECAUSE PPyGui has no change/changed event
    # Now we only allowed to create the event binding,
    # if the completion method exists

    if not ( self._Events_Bound ) :
      self._Events_Bound = True
      try :
        self.Bind ( wx.EVT_NOTEBOOK_PAGE_CHANGED, self._Extra_OnChange )
      except :
        pass

  # *********************************************************
  # *********************************************************
  def GetSelection ( self ) :
    return self.Selected_Page

  # *********************************************************
  # DUMMY replacement for the original event handler
  # *********************************************************
  def _onchange ( self, event ) :
    pass
  
  # *********************************************************
  # *********************************************************
  def _Extra_OnChange ( self, event ) :
    self.Selected_Page = event.GetSelection()
    self._onchange ( event )
    event.Skip ()

  # *********************************************************
  # This is implemented to support the following construct
  #      icon = self.combo_2 [ self.combo_2.selection ]
  # Which could be far more better implemented by
  #      icon = self.combo_2.text
  # The __getitem__ implementation is quit tricky,
  # and much to limited to fully support combo[index] !!
  # see: http://docs.python.org/ref/sequence-types.html
  # *********************************************************
  def __getitem__ ( self, key ) :
    return self.GetPage ( key )
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class _Calendar_Dialog ( wx.Dialog ):
  def __init__ ( self, parent = None, pos = (-1,-1) ):
    style = wx.DEFAULT_FRAME_STYLE | \
                    wx.SUNKEN_BORDER | \
                    wx.CLIP_CHILDREN | \
                    wx.STAY_ON_TOP
    self.parent = parent
    wx.Dialog.__init__( self, None, title = '',
                        #size = ( width, -1 ),
                        pos = pos,
                        style = 0 ) #style )

    self.cal = calen.CalendarCtrl (
      self, -1, #wx.DateTime_Now(),
      style =   calen.CAL_MONDAY_FIRST
              | calen.CAL_SHOW_HOLIDAYS
              | calen.CAL_SEQUENTIAL_MONTH_SELECTION
              #| calen.CAL_SHOW_SURROUNDING_WEEKS
              )

    import datetime
    #datetime.datetime(2008, 5, 1, 23, 9, 45, 796000)
    self.now = datetime.date.timetuple ( datetime.datetime.today() )
    self.cur_year  = self.now [0]
    self.cur_month = self.now [1]
    self.cur_day   = self.now [2]
    self._On_Change_Month ()

    self.cal.Bind ( calen.EVT_CALENDAR_DAY, self._On_Calendar )
    self.cal.Bind ( calen.EVT_CALENDAR_MONTH, self._On_Change_Month ) #, cal)

    Sizer = wx.BoxSizer ( wx.VERTICAL )
    Sizer.Add ( self.cal, 1 )
    self.SetSizer ( Sizer )
    Sizer.Fit ( self )

    self.Bind ( wx.EVT_ACTIVATE, self._On_Loose_Focus )

  # *********************************************************
  # TOO bad, this is also triggered, when the application looses focus
  # *********************************************************
  def _On_Loose_Focus ( self, event ) :
    if not event.GetActive() :
      self.parent.CallBack ( None )

  # *********************************************************
  # *********************************************************
  def _On_Calendar ( self, event ) :
    self.parent.CallBack ( event.GetDate () )

  # *********************************************************
  # change highlighting the current date,
  #  this doesn't work perfect,
  #  it can change the setting of saterday or sunday !!
  # *********************************************************
  def _On_Change_Month ( self, event = None ):
    month = self.cal.GetDate().GetMonth() + 1   # convert wxDateTime 0-11 => 1-12
    year  = self.cal.GetDate().GetYear ()
    #print month, self.cal.GetDate().GetYear (), year, self.cur_year
    #print month,self.cur_month,self.cur_day
    if ( month == self.cur_month ) and \
       ( year  == self.cur_year  ) :
      self.cal.SetHighlightColours ( wx.WHITE, wx.BLUE )
      #attr = calen.CalendarDateAttr ( border    = calen.CAL_BORDER_SQUARE,
      #                                colBorder = "red")
      #self.cal.SetAttr ( self.cur_day, attr )
    else:
      self.cal.SetHighlightColours ( None, None )
      self.cal.ResetAttr ( self.cur_day )
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class Date ( Frame ):
  def __init__ ( self, parent, title = '' ):
    self.parent = parent
    Frame.__init__( self, parent )
    self.SetBackgroundColour ( wx.WHITE )
    
    self.label = Label ( self, '01-05-08' )
    self.button = Button ( self, '\\/', self._OnKey, pos = (-1,-1,20,-1))

    sizer = HBox ()
    sizer.add      ( self.label,  1 )
    sizer.addfixed ( self.button, 10 )
    self.sizer = sizer

  # *********************************************************
  # *********************************************************
  def _OnKey ( self, event ) :
    Frame = wx.GetTopLevelParent(self.parent)
    pos = tuple ( Frame.GetPosition() )
    pos = ( pos[0] + 5,
            pos[1] + 25 + self.GetPositionTuple ()[1] +
                          self.GetSizeTuple ()[1] )

    self.dlg = _Calendar_Dialog ( self, pos = pos )
    self.dlg.Show ()
    self.started = True

  # *********************************************************
  # when a date is selected or focus is lost,
  # this method is called
  # *********************************************************
  def CallBack ( self, date ) :
    if self.started :
      self.started = False
      self.dlg.Destroy ()
      if date:
        pass #print 'CALLBACK',date
        # HERE WE SHOULD CREATE AN update EVENT
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class Label ( wx.StaticText, _gui_extension ) :
  def __init__ ( self, parent = None,
                 title  = '',
                 align  = 'left',
                 border = False,
                 visible = True,
                 enabled = True,
                 pos = ( -1, -1, -1, -1 ),
                 font   = None ) :
    self.parent = parent

    style = 0
    if align :
      if align == 'right' :
        style |= wx.ALIGN_RIGHT + wx.ST_NO_AUTORESIZE
      elif align == 'center' :
        style |= wx.ALIGN_CENTER + wx.ST_NO_AUTORESIZE

    if border :
      style |= wx.BORDER_SIMPLE

    wx.StaticText.__init__ ( self, parent, -1, title, style = style )

    _gui_extension.__init__ ( self, parent, font )
    self.Bind ( wx.EVT_LEFT_DOWN, self._OnChange )

    # make some methods also available as property (attribute)
    self._add_attrib ( 'text', self.SetLabel, self.GetLabel )

  def hide ( self ) :
    self.Hide ()
  def show ( self ) :
    self.Show ()
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class Combo ( wx.ComboBox, _gui_extension  ) :
  def __init__ ( self, parent = None ,
                 style   = None,
                 choices = [] ) :
    wx.ComboBox.__init__ ( self, parent, -1,
                           style = wx.BORDER_NONE )
                           #wx.BORDER_SIMPLE )
    print(('CHOICES',choices))
    for item in choices :
      self.Append ( item )
    
    _gui_extension.__init__ ( self, parent )
    self.Bind ( wx.EVT_COMBOBOX, self._OnChange )

    # make some methods also available as property (attribute)
    self._add_attrib ( 'selection', self.SetSelection, self.GetSelection    )
    self._add_attrib ( 'text',      self.SetStringSelection, self.GetStringSelection )


  def TEST ( self, event ):
    print('CONMBO')
  # *********************************************************
  # *********************************************************
  def append ( self, item ) :
    self.Append ( item )

  # *********************************************************
  # This is implemented to support the following construct
  #      icon = self.combo_2 [ self.combo_2.selection ]
  # Which could be far more better implemented by
  #      icon = self.combo_2.text
  # The __getitem__ implementation is quit tricky,
  # and much to limited to fully support combo[index] !!
  # see: http://docs.python.org/ref/sequence-types.html
  # *********************************************************
  def __getitem__ ( self, key ) :
    return self.GetValue()
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class Edit ( wx.TextCtrl, _gui_extension ) :
  def __init__ ( self, parent = None,
                 text      = '',
                 align     = 'left',
                 style     = 'normal',
                 password  = False,
                 multiline = False,
                 line_wrap = False,
                 readonly  = False,
                 border    = False,
                 font      = None ) :
                   
    # TODO, numeric input, why doesn't it accept "-"
    if style == 'number' :
      pass

    style = wx.BORDER_SIMPLE #| wx.TE_NO_VSCROLL
    if multiline : style |= wx.TE_MULTILINE | wx.TE_PROCESS_ENTER
    if line_wrap : style |= wx.TE_LINEWRAP
    if password  : style |= wx.TE_PASSWORD
    if   align == 'center' : style |= wx.TE_CENTER
    elif align == 'right'  : style |= wx.TE_RIGHT
    wx.TextCtrl.__init__ ( self, parent, -1, style = style )
    self.SetLabel ( text )

    #self.SetMinSize ( ( 20,-1 ) )

    # create event bindings
    _gui_extension.__init__ ( self, parent, font )
    self.SIPP_Control = 2
    #self._OnChange_User = action
    self.Bind ( wx.EVT_TEXT, self._OnChange )

    # make some methods also available as property (attribute)
    self._add_attrib ( 'text',     self.SetLabel,    self.GetLabel    )
    self._add_attrib ( 'readonly', self.SetReadOnly, self.GetReadOnly )

    # after creating the extra properties
    self.SetReadOnly ( readonly )

  def append ( self, line ) :
    self.AppendText ( line )
    
  # *********************************************************
  # Instead of readonly-flag, TextCtrl has the Editable-flag
  # so we need to invert everything
  # *********************************************************
  def SetReadOnly ( self, ReadOnly = True ) :
    self.SetEditable ( not ( ReadOnly ) )
    if ReadOnly :
      self.SetBackgroundColour ( Color_HighLight )
    else :
      self.SetBackgroundColour ( wx.WHITE )
  def GetReadOnly ( self ) :
    return not ( self.IsEditable )
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class Button ( wx.Button, wx.CheckBox, _gui_extension  ) :
  def __init__ ( self, parent = None,
                 title  = '',
                 action = None,
                 align  = 'center',
                 style  = 'normal',
                 border = False,
                 pos    = ( -1, -1, -1, -1 ),
                 font   = None ) :

    if style == 'check' :
      wx.CheckBox.__init__ ( self, parent, -1, title )
    else :
      wx.Button.__init__ ( self, parent, -1, title,
                           style = wx.NO_BORDER, #.BORDER_NONE,
                           pos   = pos[:2],
                           size  = pos [2:] )
      self.SetMinSize ( ( -1, 10 ) )
      self.SetBestFittingSize ( ( -1, 10 ) )
      self.SetBackgroundColour ( Color_HighLight )
                           #wx.BORDER_SIMPLE )
    if not ( font ) :
      font = Font ( bold = True )
      #size = 9, color = None, bold = False ) :
      self._Set_Font ( font )

    # Define the minimum width according to the text
    dc = wx.ScreenDC()
    w  = dc.GetTextExtent ( title ) [0]
    h = pos [3]
    if h == -1 : h = 22
    self.SetMinSize ( ( w + 10, 22 ) )

    # create event bindings
    _gui_extension.__init__ ( self, parent, font )
    self._OnChange_User = action
    self.Bind ( wx.EVT_BUTTON, self._OnChange )

    # make some methods also available as property (attribute)
    self._add_attrib ( 'checked', self.SetValue, self.GetValue )
    self._add_attrib ( 'text',    self.SetLabel, self.GetLabel )
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class RadioGroup ( _gui_extension  ) :
  def __init__ ( self ) :
    self.Radio_Buttons = []
    self.parent        = None
    self.SIPP_Control = None

  def add ( self, parent, item ) :
    if not ( self.parent ) :
      self.parent = parent

      # create event bindings
      _gui_extension.__init__ ( self, parent )

      # make some methods also available as property (attribute)
      self.value = item.value

    # Because the EVT_RADIOBUTTON isn't fired,
    # when clicking on an already selected item
    # we use the Left-Down event and some preprocessing ourselfs
    item.Bind   ( wx.EVT_LEFT_DOWN,   self._OnChange_PreProcess )
    self.Radio_Buttons.append ( item )

  # *********************************************************
  # Find out which RadioButton was pressed and
  # set the value of that RB inthe groups value property
  # *********************************************************
  def _OnChange_PreProcess ( self, event ) :
    ID = event.GetId()
    for RB in self.Radio_Buttons :
      if RB.GetId () == ID :
        self.value = RB.value
    event.Skip ()
    self._OnChange ( event )
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class RadioButton ( wx.RadioButton, _gui_extension ) :
  def __init__ ( self, parent = None,
                 title    = '',
                 align    = 'center',
                 group    = None,
                 value    = None,
                 border   = False,
                 visible  = True,
                 enabled  = True,
                 selected = False,
                 pos      = ( -1, -1, -1, -1 ),

                 font     = None,
                 action   = None,
                 style    = 'normal',
                 ) :
    self.value  = value
    self.parent = parent
    
    # "style = wx.RB_GROUP", starts a new group in the current container
    # but "style" in this sense is not supported by PPyGui,
    # so we use "selected" instead, and thus
    #   - the first radiobutton of a group must have selected = True
    #   - all other buttons in the same group should have selected = False
    if selected : style = wx.RB_GROUP
    else :        style = 0
    wx.RadioButton.__init__ ( self, parent, -1,
                              title,
                              style = style )

    _gui_extension.__init__ ( self, parent, font )

    self.SetValue ( selected )
    group.add ( parent, self )
    
  def focus ( self ):
    pass
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class Spin ( wx.SpinCtrl, _gui_extension  ) :
  def __init__ ( self, parent = None,
                 range = ( 0,100 ),
                 pos   = ( -1, -1 ),
                 size  = ( -1, -1 ),

                 value = None,
                  ) :
    wx.SpinCtrl.__init__ ( self, parent, -1, '',
                                      pos  = pos,
                                      size = size,
                                      min  = range[0],
                                      max  = range[1] )
    # create event bindings
    _gui_extension.__init__ ( self, parent )
    self.Bind ( wx.EVT_SPINCTRL, self._OnChange )

    # make some methods also available as property (attribute)
    self._add_attrib ( 'value', self.SetValue, self.GetValue )
    
    if value :
      self.value = value
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class Html ( html.HtmlWindow, _gui_extension  ) :
  def __init__ ( self, parent = None,
                 range = ( 0,100 ),
                 pos   = ( -1, -1 ),
                 size  = ( -1, -1 ) ) :
    self.parent = parent
    html.HtmlWindow.__init__ ( self, parent, -1, style=wx.NO_FULL_REPAINT_ON_RESIZE)

    #html.HtmlWindow.AddFilter
    #html.HtmlWindow.
    
    # create event bindings "navigate"
    _gui_extension.__init__ ( self, parent )
    #self.Bind ( wx.EVT_SPINCTRL, self._OnChange )

    # make some methods also available as property (attribute)
    self._add_attrib ( 'value', self.SetValue, self.GetValue )
    self._add_attrib ( 'text',  self.SetValue, self.GetValue )

  def navigate ( self, url ) :
    self.LoadPage ( url )
    
  # Not available on windows
  def enableshrink ( self, shrink ) :
    pass
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class Slider ( wx.Slider, _gui_extension  ) :
  def __init__ ( self, parent = None,
                 style = 'horizontal',
                 range = ( 0, 100 ),
                 pos   = ( -1, -1, -1, -1 ) ) :
    Style = wx.SL_AUTOTICKS #| wx.SL_LABELS
    if style == 'vertical' :
      Style |= wx.SL_VERTICAL
    wx.Slider.__init__ ( self, parent,
                         pos       = pos [:2] ,
                         size      = pos [2:],
                         style     = Style,
                         minValue  = range[0],
                         maxValue  = range[1] )

    # create event bindings
    _gui_extension.__init__ ( self, parent )
    self.Bind ( wx.EVT_SLIDER, self._OnChange )

    # make some methods also available as property (attribute)
    self._add_attrib ( 'value', self.SetValue, self.GetValue )
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class Progress ( wx.Gauge, _gui_extension  ) :
  def __init__ ( self, parent = None,
                 style        = 'normal',
                 orientation  = 'horizontal',
                 range        = ( 0,100 ),
                 pos          = ( -1, -1 ),
                 size         = ( -1, -1 ) ) :
    Style = 0 #wx.GA_PROGRESSBAR
    if orientation == 'vertical' :
      Style |= wx.GA_VERTICAL
    else :
      Style |= wx.GA_HORIZONTAL
    if style == 'smooth' :
      Style |= wx.GA_SMOOTH

    wx.Gauge.__init__ ( self, parent, -1,
                        pos   = pos,
                        size  = size,
                        range = 100,
                        style = Style )

    # make some methods also available as property (attribute)
    _gui_extension.__init__ ( self, parent )
    self._add_attrib ( 'value', self.SetValue, self.GetValue )
# ***********************************************************************


# ***********************************************************************
# some sub-classes for Table
# ***********************************************************************
class _Table_Columns ( object ):
  def __init__ ( self, grid ) :
    self.grid = grid
  def append ( self, title ) :
    self.grid.AppendCols ( 1 )
    C = self.grid.GetNumberCols ()
    self.grid.SetColLabelValue ( C-1, title )
    
# ***********************************************************************
class _Table_Rows ( object ):
  def __init__ ( self, grid ) :
    self.grid = grid
    self.rows = []

  # *********************************************************
  # *********************************************************
  def append ( self, values ) :
    self.grid.AppendRows ( 1 )
    R = self.grid.GetNumberRows ()
    for C,value in enumerate ( values ) :
      self.grid.SetCellValue ( R-1, C, str ( value ) )

  # *********************************************************
  # This is implemented to support the following construct
  #      icon = self.combo_2 [ self.combo_2.selection ]
  # Which could be far more better implemented by
  #      icon = self.combo_2.text
  # The __getitem__ implementation is quit tricky,
  # and much to limited to fully support combo[index] !!
  # see: http://docs.python.org/ref/sequence-types.html
  # *********************************************************
  def __getitem__ ( self, row, col=None ) :
    if col :
      return self.grid.GetCellValue ( row, col )
    else :
      result = []
      for C in range ( self.grid.GetNumberCols () ) :
        result.append ( self.grid.GetCellValue ( row, C ) )
      return result
    
  # *********************************************************
  # *********************************************************
  def __len__ ( self ) :
    return  self.grid.GetNumberRows ()
  
  # *********************************************************
  # *********************************************************
  def _delete_all ( self ) :
    NRows = self.grid.GetNumberRows ()
    if NRows :
      self.grid.DeleteRows ( numRows = NRows )

  # *********************************************************
  # *********************************************************
  def get_selection ( self ) :
    return self.grid.prev_selection
    #return  self.grid.GetSelectedRows ()

# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class Table ( gridlib.Grid, _gui_extension  ) :
  def __init__ ( self, parent = None,
                 columns    = [],
                 autoadjust = True,
                 multiple   = False,
                 has_header = True,
                 border     = True,
                 font       = None
                  ) :
    self.parent     = parent
    self.autoadjust = autoadjust
    self.prev_selection = []
    gridlib.Grid.__init__ ( self, parent, -1 )
    self.SetLabelBackgroundColour ( Color_HighLight )
    self.CreateGrid ( 0, len ( columns ), gridlib.Grid.SelectRows )
    for i, name in enumerate ( columns ) :
      self.SetColLabelValue ( i, name )

    self.SetRowLabelSize ( 0 )
    self.SetColLabelAlignment ( wx.ALIGN_LEFT, wx.ALIGN_CENTRE )
    self.EnableGridLines ( False )
    self.SetDefaultRowSize ( 8, True )
    self.SetColLabelSize ( 20 )
    MH = 13
    self.SetRowMinimalAcceptableHeight ( MH )
    self.SetDefaultRowSize ( MH, True )
    self.EnableEditing ( False )
    self.SetCellHighlightPenWidth ( 0 )
    self.DisableDragRowSize ( )
    # doesn't work here : self.AutoSizeColumns ( True )

    # Create instances of cols, rows, to handle properties
    self.columns = _Table_Columns ( self )
    self.rows    = _Table_Rows    ( self )

    # create event bindings
    _gui_extension.__init__ ( self, parent )

    if not ( font ) :
      font = Font ( bold = True )
      self._Set_Font ( font )
    self._Set_Font ( font )
    
    # make some methods also available as property (attribute)
    self._add_attrib ( 'redraw', self._Redraw )

    self.Bind ( gridlib.EVT_GRID_CMD_SELECT_CELL, self._OnCmd )
    self.Bind ( wx.EVT_KILL_FOCUS, self._On_Leave_Focus )

  # *********************************************************
  # *********************************************************
  def _Set_Font ( self, font ):
    for item in font :
      if isinstance ( item, wx.Colour ) :
        self.SetForegroundColour ( item )
      elif isinstance ( item, wx.Font ) :
        self.SetFont ( item )
        self.SetDefaultCellFont ( item )

    # always rowadjust ?? if self.autoadjust :
    dc = wx.ScreenDC()
    h  = dc.GetTextExtent ( 'Ap' ) [1]
    self.SetDefaultRowSize ( h-2, True )

  # *********************************************************
  # *********************************************************
  def _On_Leave_Focus ( self, event ) :
    self.ClearSelection ()

  # *********************************************************
  # *********************************************************
  def delete_all ( self ) :
    self.rows._delete_all ()

  # *********************************************************
  # extend the event with some properties
  # *********************************************************
  def _OnCmd ( self, event ) :
    # Becuase we have to Clear selection on leave focus,
    # we set the selection here
    self.prev_selection = [ event.Row ]

    def _get_index () :
      return event.Row
    event.get_index = _get_index
    event.selected  = True
    self._OnChange ( event )

  # *********************************************************
  # *********************************************************
  def _Redraw ( self, value ) :
    if not ( value ) : return
    self.AutoSizeColumns ( self.autoadjust )
    self.ForceRefresh ()

  # *********************************************************
  # *********************************************************
  def adjust_all ( self ) :
    self.autoadjust = True
    self._Redraw ( True )
# ***********************************************************************


# ***********************************************************************
# class Spacer is identical to wx.Size
# ***********************************************************************
Spacer = wx.Size
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class VBox ( wx.BoxSizer ) :
  def __init__ ( self, border = None, spacing = 0 ):

    self.border =  border
    if spacing > 0 :
      self.Spacer = ( -1, spacing )
    else :
      self.Spacer = None

    if self.border :
      B = self.border

      self.sizer_core = wx.BoxSizer ( wx.VERTICAL )
      self.sizer_core.Add ( ( -1, B[1] ),    0, wx.EXPAND| wx.ALL )
      self.sizer_core.Add ( ( -1, B[3] ),    0, wx.EXPAND| wx.ALL )

      wx.BoxSizer.__init__ ( self, wx.HORIZONTAL )
      self.Add ( ( B[0], -1 ), 0, wx.EXPAND | wx.ALL )
      self.Add ( self.sizer_core, 1, wx.EXPAND | wx.ALL )
      self.Add ( ( B[2], -1 ), 0, wx.EXPAND | wx.ALL )

    else :
      wx.BoxSizer.__init__ ( self, wx.VERTICAL )

  # *********************************************************
  # *********************************************************
  def add ( self, item, proportion = 0 ) :
    if self.border :
      Nelem = len ( self.sizer_core.GetChildren () )
      if self.Spacer and ( Nelem > 2 ) :
        self.sizer_core.Insert ( Nelem-1, self.Spacer, 0, wx.EXPAND ) #| wx.ALL)
        Nelem = len ( self.sizer_core.GetChildren () )
      self.sizer_core.Insert ( Nelem-1, item, proportion, wx.EXPAND ) # | wx.ALL)
    else :
      Nelem = len ( self.GetChildren () )
      if self.Spacer and ( Nelem > 0 ) :
        self.Add ( self.Spacer, proportion, wx.EXPAND ) #| wx.ALL)
      self.Add ( item, proportion, wx.EXPAND ) #| wx.ALL)


  # *********************************************************
  # *********************************************************
  def addfixed ( self, item, size ) :
    if size == 0 :
      self.add ( item, 1 )
    else :
      item.SetMinSize ( ( size, -1 ) )
      self.add ( item, 0 )
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class HBox ( wx.BoxSizer ) :
  def __init__ ( self, border = None, spacing = 0 ):

    self.border =  border
    if spacing > 0 :
      self.Spacer = ( spacing, -1 )
    else :
      self.Spacer = None

    if self.border :
      B = self.border

      self.sizer_core = wx.BoxSizer ( wx.HORIZONTAL )
      self.sizer_core.Add ( ( B[0], -1 ),    0, wx.EXPAND| wx.ALL )
      self.sizer_core.Add ( ( B[2], -1 ),    0, wx.EXPAND| wx.ALL )

      wx.BoxSizer.__init__ ( self, wx.VERTICAL )
      self.Add ( ( -1, B[1] ), 0, wx.EXPAND | wx.ALL )
      self.Add ( self.sizer_core, 1, wx.EXPAND | wx.ALL )
      self.Add ( ( -1, B[3] ), 0, wx.EXPAND | wx.ALL )

    else :
      wx.BoxSizer.__init__ ( self, wx.HORIZONTAL )

  # *********************************************************
  # *********************************************************
  def add ( self, item, proportion = 0 ) :
    if self.border :
      Nelem = len ( self.sizer_core.GetChildren () )
      if self.Spacer and ( Nelem > 2 ) :
        self.sizer_core.Insert ( Nelem-1, self.Spacer, 0, wx.EXPAND )
        Nelem = len ( self.sizer_core.GetChildren () )
      self.sizer_core.Insert ( Nelem-1, item, proportion, wx.EXPAND )
    else :
      Nelem = len ( self.GetChildren () )
      if self.Spacer and ( Nelem > 0 ) :
        self.Add ( self.Spacer, 0, wx.EXPAND )
      self.Add ( item, proportion, wx.EXPAND )

  # *********************************************************
  # *********************************************************
  def addfixed ( self, item, size ) :
    if size == 0 :
      self.add ( item, 1 )
    else :
      item.SetMinSize ( ( size, -1 ) )
      self.add ( item, 0 )
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class TBox ( wx.GridSizer ) :
  def __init__ ( self,
                 NHor      = 0,
                 NVer      = 2,
                 spacing_x = 2,
                 spacing_y = 2 ) :
    wx.GridSizer.__init__ ( self, NVer, NHor, spacing_y, spacing_x )
    #self.border = spacing

  def add ( self, item ) :
    self.Add ( item )

  """ Necessary ?
  def addfixed ( self, item, size ) :
    item.SetSize ( ( size, -1 ) )
    self.Add ( item, 0,
               wx.EXPAND | wx.ALL,
               border = 0 ) #self.border )
  """
# ***********************************************************************




# ***********************************************************************
#  DEMO  DEMO  DEMO  DEMO  DEMO  DEMO  DEMO  DEMO  DEMO  DEMO  DEMO
# ***********************************************************************
from . import api as gui
if __name__ == '__main__' :
  app = gui.Application ()
  color_small     = ( 0, 255, 0 )
  color_base      = ( 0, 0, 200 )
  color_subheader = ( 0, 0, 200 )
  color_header    = ( 0, 255, 0 )
  font_small     = gui.Font ( size = 7,  color = color_small,     bold = True )
  font_base      = gui.Font ( size = 8,  color = color_base,      bold = True )
  font_subheader = gui.Font ( size = 10, color = color_subheader, bold = True )
  font_header    = gui.Font ( size = 14, color = color_header,    bold = True )
  BACKWARD       = 'BackWard'


# ***********************************************************************
# ***********************************************************************
class Test_wxFrame1 ( Frame ) :
  def __init__ ( self, parent ) :
    Frame.__init__ ( self, parent )
    self.ed1 = Edit(self, "Multiline centered edit", multiline=True)

    sizer = VBox ( border = ( 2, 2, 2, 2 ), spacing = 2 )
    sizer.add ( self.ed1, 1 )
    self.sizer = sizer

    self.sipp = SIPPref ( self )
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
#class Login ( gui.Frame ) :
class Test_wxFrame ( gui.Frame ) :
  def __init__ ( self, parent ) :
    gui.Frame.__init__ ( self, parent )

    font = font_subheader
    self.lb1 = Label ( self, 'Z-nummer' , font  = font )
    self.lb2 = Label ( self, 'Password' , font  = font )
    self.sp1 = Label ( self, '')

    self.ed1 = Edit ( self, "z571117", font = font                  )
    self.ed2 = Edit ( self, '',        font = font, password = True )

    self.b1  = Button ( self, "OK",    font = font )


    sizer2 = HBox ()
    sizer2.addfixed ( self.b1, 80 )

    sizer = VBox ( border = ( 20, 15, 20, 2 ), spacing = 2 )
    sizer.add ( self.lb1 )
    sizer.add ( self.ed1 )
    sizer.add ( Spacer ( -1, 35 ) )
    sizer.add ( self.lb2 )
    sizer.add ( self.ed2 )
    sizer.add ( Spacer ( -1, 15 ) )
    sizer.add ( sizer2 )

    self.sizer = sizer

    # If this omitted, the window won't show up automatically
    self.sipp = SIPPref ( self )
# ***********************************************************************

# ***********************************************************************
# ***********************************************************************
class Main_Frame ( CeFrame ):
  def __init__ ( self ) :
    CeFrame.__init__ ( self,
        title  =   'Ultimo Mobile',
        action = ( 'About',         self._On_Left_Command ),
        menu   =   'Menu' )

    # *******************************************************
    # Create the other forms here
    # *******************************************************
    test_frame = Test_wxFrame ( self )

    # *******************************************************
    # *******************************************************
    self.main_sizer = VBox ()
    self.main_sizer.add ( test_frame , 1 )
    self.sizer = self.main_sizer

    self.sipp = SIPPref ( self )

    # *******************************************************
    # if we set focus sooner, focussing doesn't work
    # *******************************************************
    #self.Login.ed2.focus ()

  # *******************************************************
  # *******************************************************
  def _On_Left_Command ( self, event ) :
    Message.ok ( 'About',
                     'PPyGui Mobile Emulator V0.1 \n(build in wxPython)',
                     'info', self)
# ***********************************************************************



# ***********************************************************************
# IN THIS SPECIFIC CASE, THE APPLICATION IS ALREADY CREATED !!
# ***********************************************************************
if __name__ == '__main__' :
  app.mainframe = Main_Frame ()
  app.run ()
# ***********************************************************************

