## 	   Copyright (c) 2006-2008 Alexandre Delattre
## 	   Copyright (c) 2003 Henk Punt

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

from ctypes import *

#TODO auto ie/comctl detection
WIN32_IE = 0x0550

#TODO: auto unicode selection,
#if unicode:
#  CreateWindowEx = windll.coredll.CreateWindowExW
#else:
#  CreateWindowEx = windll.coredll.CreateWindowExA
#etc, etc


DWORD = c_ulong
HANDLE = c_ulong
UINT = c_uint
BOOL = c_int
HWND = HANDLE
HINSTANCE = HANDLE
HICON = HANDLE
HDC = HANDLE
HCURSOR = HANDLE
HBRUSH = HANDLE
HMENU = HANDLE
HBITMAP = HANDLE
HIMAGELIST = HANDLE
HGDIOBJ = HANDLE
HMETAFILE = HANDLE

ULONG = DWORD
ULONG_PTR = DWORD
UINT_PTR = DWORD
LONG_PTR = DWORD
INT = c_int
LPCTSTR = c_wchar_p
LPTSTR = c_wchar_p
PSTR = c_char_p
LPCSTR = c_char_p
LPCWSTR = c_wchar_p
LPSTR = c_char_p
LPWSTR = c_wchar_p
PVOID = c_void_p
USHORT = c_ushort
WORD = c_ushort
ATOM = WORD
SHORT = c_short
LPARAM = c_ulong
WPARAM = c_uint
LPVOID = c_voidp
LONG = c_long
BYTE = c_byte
TCHAR = c_wchar #TODO depends on unicode/wide conventions
DWORD_PTR = c_ulong #TODO what is this exactly?
INT_PTR = c_ulong  #TODO what is this exactly?
COLORREF = c_ulong
CLIPFORMAT = WORD
FLOAT = c_float
CHAR = c_char
WCHAR = c_wchar

FXPT16DOT16 = c_long
FXPT2DOT30 = c_long
LCSCSTYPE = c_long
LCSGAMUTMATCH = c_long
COLOR16 = USHORT

LRESULT = LONG_PTR

#### Windows version detection ##############################
class OSVERSIONINFO(Structure):
    _fields_ = [("dwOSVersionInfoSize", DWORD),
                ("dwMajorVersion", DWORD),
                ("dwMinorVersion", DWORD),
                ("dwBuildNumber", DWORD),
                ("dwPlatformId", DWORD),
                ("szCSDVersion", TCHAR * 128)]

    def isMajorMinor(self, major, minor):
        return (self.dwMajorVersion, self.dwMinorVersion) == (major, minor)
    
GetVersion = windll.coredll.GetVersionExW
versionInfo = OSVERSIONINFO()
versionInfo.dwOSVersionInfoSize = sizeof(versionInfo)
GetVersion(byref(versionInfo))

def MAKELONG(w1, w2):
    return w1 | (w2 << 16)

MAKELPARAM = MAKELONG

def RGB(r,g,b):
    return r | (g<<8) | (b<<16)

##### Windows Callback functions ################################
WNDPROC = WINFUNCTYPE(c_int, HWND, UINT, WPARAM, LPARAM)
DialogProc = WINFUNCTYPE(c_int, HWND, UINT, WPARAM, LPARAM)

CBTProc = WINFUNCTYPE(c_int, c_int, c_int, c_int)
MessageProc = CBTProc

EnumChildProc = WINFUNCTYPE(c_int, HWND, LPARAM)

MSGBOXCALLBACK = WINFUNCTYPE(c_int, HWND, LPARAM) #TODO look up real def

class WNDCLASS(Structure):
    _fields_ = [
                ("style",  UINT),
                ("lpfnWndProc", WNDPROC),
                ("cbClsExtra", INT),
                ("cbWndExtra", INT),
                ("hInstance", HINSTANCE),
                ("hIcon", HICON),
                ("hCursor", HCURSOR),
                ("hbrBackground", HBRUSH),
                ("lpszMenuName", LPCTSTR),
                ("lpszClassName", LPCTSTR),
                ]

class POINT(Structure):
    _fields_ = [("x", LONG),
                ("y", LONG)]

    def __str__(self):
        return "POINT {x: %d, y: %d}" % (self.x, self.y)

POINTL = POINT

class POINTS(Structure):
    _fields_ = [("x", SHORT),
                ("y", SHORT)]
    

PtInRect = windll.coredll.PtInRect

class RECT(Structure):
    _fields_ = [("left", LONG),
                ("top", LONG),
                ("right", LONG),
                ("bottom", LONG)]

    def __str__(self):
        return "RECT {left: %d, top: %d, right: %d, bottom: %d}" % (self.left, self.top,
                                                                    self.right, self.bottom)

    def getHeight(self):
        return self.bottom - self.top

    height = property(getHeight, None, None, "")

    def getWidth(self):
        return self.right - self.left

    width = property(getWidth, None, None, "")

    def getSize(self):
        return self.width, self.height

    size = property(getSize, None, None, "")
    
    def ContainsPoint(self, pt):
        """determines if this RECT contains the given POINT pt
        returns True if pt is in this rect
        """
        return bool(PtInRect(byref(self), pt))
        
RECTL = RECT        

class SIZE(Structure):
    _fields_ = [('cx', LONG),
                ('cy', LONG)]
        
SIZEL = SIZE        
        
    
##class MSG(Structure):
##    _fields_ = [("hWnd", HWND),
##                ("message", UINT),
##                ("wParam", WPARAM),
##                ("lParam", LPARAM),
##                ("time", DWORD),
##                ("pt", POINT)]

##    def __str__(self):
##        return "MSG {%d %d %d %d %d %s}" % (self.hWnd, self.message, self.wParam, self.lParam,
##                                            self.time, str(self.pt))

#Hack: we need to use the same MSG type as ctypes.com.ole uses!
from ctypes.wintypes import MSG
        
class ACCEL(Structure):
    _fields_ = [("fVirt", BYTE),
                ("key", WORD),
                ("cmd", WORD)]
    
class CREATESTRUCT(Structure):
    _fields_ = [("lpCreateParams", LPVOID),
                ("hInstance", HINSTANCE),
                ("hMenu", HMENU),
                ("hwndParent", HWND),
                ("cx", INT),
                ("cy", INT),
                ("x", INT),
                ("y", INT),
                ("style", LONG),
                ("lpszName", LPCTSTR),
                ("lpszClass", LPCTSTR),
                ("dwExStyle", DWORD)]



class NMHDR(Structure):
    _fields_ = [("hwndFrom", HWND),
                ("idFrom", UINT),
                ("code", UINT)]

class PAINTSTRUCT(Structure):
    _fields_ = [("hdc", HDC),
                ("fErase", BOOL),
                ("rcPaint", RECT),
                ("fRestore", BOOL),
                ("fIncUpdate", BOOL),
                ("rgbReserved", c_char * 32)]

    
class MENUITEMINFO(Structure):
    _fields_ = [("cbSize", UINT),
                ("fMask", UINT),
                ("fType", UINT),
                ("fState", UINT),                
                ("wID", UINT),
                ("hSubMenu", HMENU),
                ("hbmpChecked", HBITMAP),
                ("hbmpUnchecked", HBITMAP),
                ("dwItemData", ULONG_PTR),
                ("dwTypeData", LPTSTR),                
                ("cch", UINT),
                ("hbmpItem", HBITMAP)]

class DLGTEMPLATE(Structure):
    _pack_ = 2
    _fields_ = [
        ("style", DWORD),
        ("exStyle", DWORD),
        ("cDlgItems", WORD),
        ("x", c_short),
        ("y", c_short),
        ("cx", c_short),
        ("cy", c_short)
    ]

class DLGITEMTEMPLATE(Structure):
    _pack_ = 2
    _fields_ = [
        ("style", DWORD),
        ("exStyle", DWORD),
        ("x", c_short),
        ("y", c_short),
        ("cx", c_short),
        ("cy", c_short),
        ("id", WORD)
    ]

class COPYDATASTRUCT(Structure):
    _fields_ = [
        ("dwData", ULONG_PTR),
        ("cbData", DWORD),
        ("lpData", PVOID)]
    
def LOWORD(dword):
    return dword & 0x0000ffff

def HIWORD(dword):
    return dword >> 16

TRUE = 1
FALSE = 0
NULL = 0

IDI_APPLICATION = 32512

SW_SHOW = 5
SW_SHOWNORMAL = 1
SW_HIDE = 0

EN_CHANGE = 768

MSGS = [('WM_NULL', 0),
        ('WM_CREATE', 1),
        ('WM_CANCELMODE', 31),
        ('WM_CAPTURECHANGED', 533),
        ('WM_CLOSE', 16),
        ('WM_COMMAND', 273),
        ('WM_DESTROY', 2),
        ('WM_ERASEBKGND', 20),
        ('WM_ENABLE', 0xa),
        ('WM_GETFONT', 49),
        ('WM_INITDIALOG', 272),
        ('WM_INITMENUPOPUP', 279),
        ('WM_KEYDOWN', 256),
        ('WM_KEYFIRST', 256),
        ('WM_KEYLAST', 264),
        ('WM_KEYUP', 257),
        ('WM_LBUTTONDBLCLK', 515),
        ('WM_LBUTTONDOWN', 513),
        ('WM_LBUTTONUP', 514),
        ('WM_MBUTTONDBLCLK', 521),
        ('WM_MBUTTONDOWN', 519),
        ('WM_MBUTTONUP', 520),
        ('WM_MENUSELECT', 287),
        ('WM_MOUSEFIRST', 512),
        ('WM_MOUSEHOVER', 673),
        ('WM_MOUSELEAVE', 675),
        ('WM_MOUSEMOVE', 512),
        ('WM_MOVE', 3),
        ('WM_NCCREATE', 129),
        ('WM_NCDESTROY', 130),
        ('WM_NOTIFY', 78),
        ('WM_PAINT', 15),
        ('WM_RBUTTONDBLCLK', 518),
        ('WM_RBUTTONDOWN', 516),
        ('WM_RBUTTONUP', 517),
        ('WM_SETCURSOR', 32),
        ('WM_SETFONT', 48),
        ('WM_SETREDRAW', 11),
        ('WM_SIZE', 5),
        ('WM_SYSKEYDOWN', 260),
        ('WM_SYSKEYUP', 261),
        ('WM_USER', 1024),
        ('WM_WINDOWPOSCHANGED', 71),
        ('WM_WINDOWPOSCHANGING', 70),
        ('WM_SETTEXT', 12),
        ('WM_GETTEXT', 13),
        ('WM_GETTEXTLENGTH', 14),
        ('WM_ACTIVATE', 6),
        ('WM_HSCROLL', 276),
        ('WM_VSCROLL', 277),
        ('WM_CTLCOLORBTN', 309),
        ('WM_CTLCOLORDLG', 310),
        ('WM_CTLCOLOREDIT', 307),
        ('WM_CTLCOLORLISTBOX', 308),
        ('WM_CTLCOLORMSGBOX', 306),
        ('WM_CTLCOLORSCROLLBAR', 311),
        ('WM_CTLCOLORSTATIC', 312),
        ('WM_TIMER', 0x0113),
        ('WM_CONTEXTMENU', 0x007B),
        ('WM_COPYDATA', 0x004A),
        ('WM_SETTINGCHANGE', 0x001A),
        ('WM_SETFOCUS', 0x7),
        ('WM_CHAR', 0x102),
        ]
        
WM_CUT = 0x300
WM_COPY = 0x301
WM_PASTE = 0x302

#insert wm_* msgs as constants in this module:
for key, val in MSGS:
    exec('%s = %d' % (key, val)) #TODO without using 'exec'?

BN_CLICKED    =     0

VK_DOWN = 40
VK_LEFT = 37
VK_RIGHT = 39
VK_DELETE  = 0x2E

CS_HREDRAW = 2
CS_VREDRAW = 1
WHITE_BRUSH = 0

MIIM_STATE= 1
MIIM_ID= 2
MIIM_SUBMENU =4
MIIM_CHECKMARKS= 8
MIIM_TYPE= 16
MIIM_DATA= 32
MIIM_STRING= 64
MIIM_BITMAP= 128
MIIM_FTYPE =256

MFT_BITMAP= 4
MFT_MENUBARBREAK =32
MFT_MENUBREAK= 64
MFT_OWNERDRAW= 256
MFT_RADIOCHECK= 512
MFT_RIGHTJUSTIFY= 0x4000
MFT_SEPARATOR =0x800
MFT_RIGHTORDER= 0x2000L
MFT_STRING = 0

MF_ENABLED    =0
MF_GRAYED     =1
MF_DISABLED   =2
MF_BITMAP     =4
MF_CHECKED    =8
MF_MENUBARBREAK= 32
MF_MENUBREAK  =64
MF_OWNERDRAW  =256
MF_POPUP      =16
MF_SEPARATOR  =0x800
MF_STRING     =0
MF_UNCHECKED  =0
MF_DEFAULT    =4096
MF_SYSMENU    =0x2000
MF_HELP       =0x4000
MF_END        =128
MF_RIGHTJUSTIFY=       0x4000
MF_MOUSESELECT =       0x8000
MF_INSERT= 0
MF_CHANGE= 128
MF_APPEND= 256
MF_DELETE= 512
MF_REMOVE= 4096
MF_USECHECKBITMAPS= 512
MF_UNHILITE= 0
MF_HILITE= 128
MF_BYCOMMAND=  0
MF_BYPOSITION= 1024
MF_UNCHECKED=  0
MF_HILITE =    128
MF_UNHILITE =  0

LOCALE_SYSTEM_DEFAULT =  0x800

MFS_GRAYED        =  0x00000003L
MFS_DISABLED      =  MFS_GRAYED
MFS_CHECKED       =  MF_CHECKED
MFS_HILITE        =  MF_HILITE
MFS_ENABLED       =  MF_ENABLED
MFS_UNCHECKED     =  MF_UNCHECKED
MFS_UNHILITE      =  MF_UNHILITE
MFS_DEFAULT       =  MF_DEFAULT

WS_BORDER	= 0x800000
WS_CAPTION	= 0xc00000
WS_CHILD	= 0x40000000
WS_CHILDWINDOW	= 0x40000000
WS_CLIPCHILDREN = 0x2000000
WS_CLIPSIBLINGS = 0x4000000
WS_DISABLED	= 0x8000000
WS_DLGFRAME	= 0x400000
WS_GROUP	= 0x20000
WS_HSCROLL	= 0x100000
WS_ICONIC	= 0x20000000
WS_MAXIMIZE	= 0x1000000
WS_MAXIMIZEBOX	= 0x10000
WS_MINIMIZE	= 0x20000000
WS_MINIMIZEBOX	= 0x20000
WS_OVERLAPPED	= 0
WS_OVERLAPPEDWINDOW = 0xcf0000
WS_POPUP	= 0x80000000l
WS_POPUPWINDOW	= 0x80880000
WS_SIZEBOX	= 0x40000
WS_SYSMENU	= 0x80000
WS_TABSTOP	= 0x10000
WS_THICKFRAME	= 0x40000
WS_TILED	= 0
WS_TILEDWINDOW	= 0xcf0000
WS_VISIBLE	= 0x10000000
WS_VSCROLL	= 0x200000

WS_EX_TOOLWINDOW = 128
WS_EX_LEFT = 0
WS_EX_LTRREADING = 0
WS_EX_RIGHTSCROLLBAR = 0
WS_EX_WINDOWEDGE = 256
WS_EX_STATICEDGE = 0x20000
WS_EX_CLIENTEDGE = 512
WS_EX_OVERLAPPEDWINDOW   =     0x300
WS_EX_APPWINDOW    =   0x40000

WA_INACTIVE = 0
WA_ACTIVE = 1
WA_CLICKACTIVE = 2

RB_SETBARINFO = WM_USER + 4
RB_GETBANDCOUNT = WM_USER +  12
RB_INSERTBANDA = WM_USER + 1
RB_INSERTBANDW = WM_USER + 10

RB_INSERTBAND = RB_INSERTBANDA

RBBIM_STYLE = 1
RBBIM_COLORS = 2
RBBIM_TEXT = 4
RBBIM_IMAGE = 8
RBBIM_CHILD = 16
RBBIM_CHILDSIZE = 32
RBBIM_SIZE = 64
RBBIM_BACKGROUND = 128
RBBIM_ID = 256
RBBIM_IDEALSIZE = 0x00000200

TPM_CENTERALIGN =4
TPM_LEFTALIGN =0
TPM_RIGHTALIGN= 8
TPM_LEFTBUTTON= 0
TPM_RIGHTBUTTON= 2
TPM_HORIZONTAL= 0
TPM_VERTICAL= 64
TPM_TOPALIGN= 0
TPM_VCENTERALIGN= 16
TPM_BOTTOMALIGN= 32
TPM_NONOTIFY= 128
TPM_RETURNCMD= 256

TBIF_TEXT = 0x00000002

DT_NOPREFIX   =      0x00000800
DT_HIDEPREFIX =      1048576

WH_CBT       =  5
WH_MSGFILTER =  (-1)

I_IMAGENONE = -2
TBSTATE_ENABLED = 4

BTNS_SHOWTEXT = 0x00000040
CW_USEDEFAULT = 0x80000000

COLOR_3DFACE = 15

BF_LEFT      = 1
BF_TOP       = 2
BF_RIGHT     = 4
BF_BOTTOM    = 8

BDR_RAISEDOUTER =      1
BDR_SUNKENOUTER =      2
BDR_RAISEDINNER =      4
BDR_SUNKENINNER =      8
BDR_OUTER    = 3
BDR_INNER    = 0xc
BDR_RAISED   = 5
BDR_SUNKEN   = 10

EDGE_RAISED  = (BDR_RAISEDOUTER|BDR_RAISEDINNER)
EDGE_SUNKEN  = (BDR_SUNKENOUTER|BDR_SUNKENINNER)
EDGE_ETCHED  = (BDR_SUNKENOUTER|BDR_RAISEDINNER)
EDGE_BUMP    = (BDR_RAISEDOUTER|BDR_SUNKENINNER)

IDC_SIZENWSE = 32642
IDC_SIZENESW = 32643
IDC_SIZEWE = 32644
IDC_SIZENS = 32645
IDC_SIZEALL = 32646
IDC_SIZE = 32640
IDC_ARROW = 32512

TCIF_TEXT    =1
TCIF_IMAGE   =2
TCIF_RTLREADING=      4
TCIF_PARAM  = 8


TCS_MULTILINE = 512

MK_LBUTTON    = 1
MK_RBUTTON    = 2
MK_SHIFT      = 4
MK_CONTROL    = 8
MK_MBUTTON    = 16

ILC_COLOR = 0
ILC_COLOR4 = 4
ILC_COLOR8 = 8
ILC_COLOR16 = 16
ILC_COLOR24 = 24
ILC_COLOR32 = 32
ILC_COLORDDB = 254
ILC_MASK = 1
ILC_PALETTE = 2048

IMAGE_BITMAP = 0
IMAGE_ICON = 1

LR_LOADFROMFILE = 16
LR_VGACOLOR = 0x0080
LR_LOADMAP3DCOLORS = 4096
LR_LOADTRANSPARENT = 32

LVSIL_NORMAL = 0
LVSIL_SMALL  = 1
LVSIL_STATE  = 2

TVSIL_NORMAL = 0
TVSIL_STATE  = 2

SRCCOPY = 0xCC0020

GWL_WNDPROC = -4

HWND_BOTTOM = 1
HWND_TOP=0
HWND_TOPMOST=-1

SWP_DRAWFRAME= 32
SWP_FRAMECHANGED= 32
SWP_HIDEWINDOW= 128
SWP_NOACTIVATE= 16
SWP_NOCOPYBITS= 256
SWP_NOMOVE= 2
SWP_NOSIZE= 1
SWP_NOREDRAW= 8
SWP_NOZORDER= 4
SWP_SHOWWINDOW= 64
SWP_NOOWNERZORDER =512
SWP_NOREPOSITION= 512
SWP_NOSENDCHANGING= 1024
SWP_DEFERERASE= 8192
SWP_ASYNCWINDOWPOS=  16384

DCX_WINDOW = 1
DCX_CACHE = 2
DCX_PARENTCLIP = 32
DCX_CLIPSIBLINGS= 16
DCX_CLIPCHILDREN= 8
DCX_NORESETATTRS= 4
DCX_LOCKWINDOWUPDATE= 0x400
DCX_EXCLUDERGN= 64
DCX_INTERSECTRGN =128
DCX_VALIDATE= 0x200000

GCL_STYLE = -26

SB_HORZ       =      0
SB_VERT       =      1
SB_CTL        =      2
SB_BOTH       =      3

SB_LINEUP           =0
SB_LINELEFT         =0
SB_LINEDOWN         =1
SB_LINERIGHT        =1
SB_PAGEUP           =2
SB_PAGELEFT         =2
SB_PAGEDOWN         =3
SB_PAGERIGHT        =3
SB_THUMBPOSITION    =4
SB_THUMBTRACK       =5
SB_TOP              =6
SB_LEFT             =6
SB_BOTTOM           =7
SB_RIGHT            =7
SB_ENDSCROLL        =8

MB_OK                    =   0x00000000
MB_OKCANCEL              =   0x00000001
MB_ABORTRETRYIGNORE      =   0x00000002
MB_YESNOCANCEL           =   0x00000003
MB_YESNO                 =   0x00000004
MB_RETRYCANCEL           =   0x00000005


MB_ICONASTERISK = 64
MB_ICONEXCLAMATION= 0x30
MB_ICONWARNING= 0x30
MB_ICONERROR= 16
MB_ICONHAND= 16
MB_ICONQUESTION= 32
MB_ICONINFORMATION= 64
MB_ICONSTOP= 16
MB_ICONMASK= 240

IDOK          =      1
IDCANCEL      =      2
IDABORT       =      3
IDRETRY       =      4
IDIGNORE      =      5
IDYES         =      6
IDNO          =      7
IDCLOSE       =  8
IDHELP        =  9

COLOR_3DDKSHADOW = 21
COLOR_3DFACE  = 15
COLOR_3DHILIGHT = 20
COLOR_3DHIGHLIGHT= 20
COLOR_3DLIGHT= 22
COLOR_BTNHILIGHT= 20
COLOR_3DSHADOW= 16
COLOR_ACTIVEBORDER =10
COLOR_ACTIVECAPTION= 2
COLOR_APPWORKSPACE= 12
COLOR_BACKGROUND= 1
COLOR_DESKTOP= 1
COLOR_BTNFACE= 15
COLOR_BTNHIGHLIGHT= 20
COLOR_BTNSHADOW= 16
COLOR_BTNTEXT= 18
COLOR_CAPTIONTEXT= 9
COLOR_GRAYTEXT= 17
COLOR_HIGHLIGHT= 13
COLOR_HIGHLIGHTTEXT= 14
COLOR_INACTIVEBORDER= 11
COLOR_INACTIVECAPTION= 3
COLOR_INACTIVECAPTIONTEXT= 19
COLOR_INFOBK= 24
COLOR_INFOTEXT= 23
COLOR_MENU= 4
COLOR_MENUTEXT= 7
COLOR_SCROLLBAR= 0
COLOR_WINDOW= 5
COLOR_WINDOWFRAME= 6
COLOR_WINDOWTEXT= 8
CTLCOLOR_MSGBOX= 0
CTLCOLOR_EDIT= 1
CTLCOLOR_LISTBOX= 2
CTLCOLOR_BTN= 3
CTLCOLOR_DLG= 4
CTLCOLOR_SCROLLBAR= 5
CTLCOLOR_STATIC= 6
CTLCOLOR_MAX= 7


GMEM_FIXED         = 0x0000
GMEM_MOVEABLE      = 0x0002
GMEM_NOCOMPACT     = 0x0010
GMEM_NODISCARD     = 0x0020
GMEM_ZEROINIT      = 0x0040
GMEM_MODIFY        = 0x0080
GMEM_DISCARDABLE   = 0x0100
GMEM_NOT_BANKED    = 0x1000
GMEM_SHARE         = 0x2000
GMEM_DDESHARE      = 0x2000
GMEM_NOTIFY        = 0x4000
GMEM_LOWER         = GMEM_NOT_BANKED
GMEM_VALID_FLAGS   = 0x7F72
GMEM_INVALID_HANDLE= 0x8000

RT_DIALOG        = "5"

CF_TEXT = 1


BS_DEFPUSHBUTTON = 0x01L
BS_GROUPBOX = 0x7

PUSHBUTTON = 0x80
EDITTEXT = 0x81
LTEXT = 0x82
LISTBOX  = 0x83
SCROLLBAR = 0x84
COMBOXBOX = 0x85
ES_MULTILINE = 4
ES_AUTOVSCROLL = 0x40L
ES_AUTOHSCROLL = 0x80L
ES_READONLY    = 0x800
CP_ACP = 0
DS_SETFONT = 0x40
DS_MODALFRAME = 0x80

SYNCHRONIZE  = (0x00100000L)
STANDARD_RIGHTS_REQUIRED = (0x000F0000L)
EVENT_ALL_ACCESS = (STANDARD_RIGHTS_REQUIRED|SYNCHRONIZE|0x3)
MAX_PATH = 260

def GET_XY_LPARAM(lParam):
    x = LOWORD(lParam)
    if x > 32768:
        x = x - 65536
    y = HIWORD(lParam)
    if y > 32768:
        y = y - 65536
        
    return x, y 

def GET_POINT_LPARAM(lParam):
    x, y = GET_XY_LPARAM(lParam)
    return POINT(x, y)

FVIRTKEY  = 0x01
FNOINVERT = 0x02
FSHIFT    = 0x04
FCONTROL  = 0x08
FALT      = 0x10

def ValidHandle(value):
    if value == 0:
        raise WinError()
    else:
        return value

def Fail(value):
    if value == -1:
        raise WinError()
    else:
        return value
    
GetModuleHandle = windll.coredll.GetModuleHandleW
PostQuitMessage= windll.coredll.PostQuitMessage
DefWindowProc = windll.coredll.DefWindowProcW
CallWindowProc = windll.coredll.CallWindowProcW
GetDCEx = windll.coredll.GetDCEx
GetDC = windll.coredll.GetDC
ReleaseDC = windll.coredll.ReleaseDC
LoadIcon = windll.coredll.LoadIconW
DestroyIcon = windll.coredll.DestroyIcon
LoadCursor = windll.coredll.LoadCursorW
#LoadCursor.restype = ValidHandle
LoadImage = windll.coredll.LoadImageW
LoadImage.restype = ValidHandle

RegisterClass = windll.coredll.RegisterClassW
SetCursor = windll.coredll.SetCursor

CreateWindowEx = windll.coredll.CreateWindowExW
CreateWindowEx.restype = ValidHandle

ShowWindow = windll.coredll.ShowWindow
UpdateWindow = windll.coredll.UpdateWindow
EnableWindow = windll.coredll.EnableWindow
GetMessage = windll.coredll.GetMessageW
TranslateMessage = windll.coredll.TranslateMessage
DispatchMessage = windll.coredll.DispatchMessageW
GetWindowRect = windll.coredll.GetWindowRect
MoveWindow = windll.coredll.MoveWindow
DestroyWindow = windll.coredll.DestroyWindow

CreateMenu = windll.coredll.CreateMenu
CreatePopupMenu = windll.coredll.CreatePopupMenu
DestroyMenu = windll.coredll.DestroyMenu
AppendMenu = windll.coredll.AppendMenuW
EnableMenuItem = windll.coredll.EnableMenuItem
CheckMenuItem = windll.coredll.CheckMenuItem
SendMessage = windll.coredll.SendMessageW
PostMessage = windll.coredll.PostMessageW
GetClientRect = windll.coredll.GetClientRect
GetWindowRect = windll.coredll.GetWindowRect
RegisterWindowMessage = windll.coredll.RegisterWindowMessageW
GetParent = windll.coredll.GetParent
GetWindowLong = cdll.coredll.GetWindowLongW
SetWindowLong = windll.coredll.SetWindowLongW
SetClassLong = windll.coredll.SetClassLongW
GetClassLong = windll.coredll.GetClassLongW
SetWindowPos = windll.coredll.SetWindowPos
InvalidateRect = windll.coredll.InvalidateRect
BeginPaint = windll.coredll.BeginPaint
EndPaint = windll.coredll.EndPaint
SetCapture = windll.coredll.SetCapture
GetCapture = windll.coredll.GetCapture
ReleaseCapture = windll.coredll.ReleaseCapture
ScreenToClient = windll.coredll.ScreenToClient
ClientToScreen = windll.coredll.ClientToScreen

IsDialogMessage = cdll.coredll.IsDialogMessageW
GetActiveWindow = cdll.coredll.GetActiveWindow
GetMessagePos = windll.coredll.GetMessagePos
BeginDeferWindowPos = windll.coredll.BeginDeferWindowPos
DeferWindowPos = windll.coredll.DeferWindowPos
EndDeferWindowPos = windll.coredll.EndDeferWindowPos
CreateAcceleratorTable = windll.coredll.CreateAcceleratorTableW
DestroyAcceleratorTable = windll.coredll.DestroyAcceleratorTable



GetModuleHandle = windll.coredll.GetModuleHandleW
GetModuleHandle.restype = ValidHandle
LoadLibrary = windll.coredll.LoadLibraryW
LoadLibrary.restype = ValidHandle
FindResource = windll.coredll.FindResourceW
FindResource.restype = ValidHandle
FindWindow = windll.coredll.FindWindowW
GetForegroundWindow = windll.coredll.GetForegroundWindow
ChildWindowFromPoint = windll.coredll.ChildWindowFromPoint

TrackPopupMenuEx = windll.coredll.TrackPopupMenuEx


GetMenuItemInfo = windll.coredll.GetMenuItemInfoW
GetMenuItemInfo.restype = ValidHandle
GetSubMenu = windll.coredll.GetSubMenu
SetMenuItemInfo = windll.coredll.SetMenuItemInfoW

SetWindowsHookEx = windll.coredll.SetWindowsHookExW
CallNextHookEx = windll.coredll.CallNextHookEx
UnhookWindowsHookEx = windll.coredll.UnhookWindowsHookEx



MessageBox = windll.coredll.MessageBoxW
SetWindowText = windll.coredll.SetWindowTextW

GetFocus = windll.coredll.GetFocus
SetFocus = windll.coredll.SetFocus

OpenClipboard = windll.coredll.OpenClipboard
EmptyClipboard = windll.coredll.EmptyClipboard
SetClipboardData = windll.coredll.SetClipboardData
GetClipboardData = windll.coredll.GetClipboardData
RegisterClipboardFormat = windll.coredll.RegisterClipboardFormatW
CloseClipboard = windll.coredll.CloseClipboard
EnumClipboardFormats = windll.coredll.EnumClipboardFormats
IsClipboardFormatAvailable = windll.coredll.IsClipboardFormatAvailable

GetDlgItem = windll.coredll.GetDlgItem
GetClassName = windll.coredll.GetClassNameW
EndDialog = windll.coredll.EndDialog

GetDesktopWindow = windll.coredll.GetDesktopWindow
MultiByteToWideChar = windll.coredll.MultiByteToWideChar
CreateDialogIndirectParam = windll.coredll.CreateDialogIndirectParamW
DialogBoxIndirectParam = windll.coredll.DialogBoxIndirectParamW



SetTimer = windll.coredll.SetTimer
KillTimer = windll.coredll.KillTimer

IsWindowVisible = windll.coredll.IsWindowVisible

GetCursorPos = windll.coredll.GetCursorPos
SetForegroundWindow = windll.coredll.SetForegroundWindow

GetClassInfo = windll.coredll.GetClassInfoW

OpenEvent = windll.coredll.OpenEventW
CreateEvent = windll.coredll.CreateEventW
GlobalAlloc = windll.coredll.LocalAlloc
GlobalFree = windll.coredll.LocalFree

Ellipse=windll.coredll.Ellipse
SetBkColor=windll.coredll.SetBkColor
GetStockObject = windll.coredll.GetStockObject
LineTo = windll.coredll.LineTo
MoveToEx = windll.coredll.MoveToEx
FillRect = windll.coredll.FillRect
DrawEdge = windll.coredll.DrawEdge
CreateCompatibleDC = windll.coredll.CreateCompatibleDC
CreateCompatibleBitmap = windll.coredll.CreateCompatibleBitmap
CreateCompatibleDC.restype = ValidHandle
SelectObject = windll.coredll.SelectObject
GetObject = windll.coredll.GetObjectW
DeleteObject = windll.coredll.DeleteObject
BitBlt = windll.coredll.BitBlt
StretchBlt = windll.coredll.StretchBlt
GetSysColorBrush = windll.coredll.GetSysColorBrush
#CreateHatchBrush = windll.coredll.CreateHatchBrush
CreatePatternBrush = windll.coredll.CreatePatternBrush
CreateSolidBrush = windll.coredll.CreateSolidBrush
CreateBitmap = windll.coredll.CreateBitmap
PatBlt = windll.coredll.PatBlt
#CreateFont = windll.coredll.CreateFontA
#EnumFontFamiliesEx = windll.coredll.EnumFontFamiliesExA
InvertRect = windll.coredll.InvertRect
DrawFocusRect = windll.coredll.DrawFocusRect
#ExtCreatePen = windll.coredll.ExtCreatePen
CreatePen = windll.coredll.CreatePen
DrawText = windll.coredll.DrawTextW
#TextOut = windll.coredll.TextOutA
CreateDIBSection = windll.coredll.CreateDIBSection
DeleteDC = windll.coredll.DeleteDC
#GetDIBits = windll.coredll.GetDIBits
CreateFontIndirect=windll.coredll.CreateFontIndirectW
Polyline = cdll.coredll.Polyline
FillRect = cdll.coredll.FillRect
SetTextColor = cdll.coredll.SetTextColor



#WinCe api
import ctypes
WM_APP = 0x8000
LineType = POINT*2
SHCMBF_EMPTYBAR = 0x0001
SHCMBF_HIDDEN = 0x0002

SHCMBF_HIDESIPBUTTON = 0x0004
SHCMBF_COLORBK = 0x0008
SHCMBF_HMENU = 0x0010
SPI_SETSIPINFO = 224
SPI_GETSIPINFO = 225

DrawMenuBar = ctypes.windll.coredll.DrawMenuBar
CommandBar_Create = ctypes.windll.commctrl.CommandBar_Create
SHCreateMenuBar = ctypes.windll.aygshell.SHCreateMenuBar
SHSipInfo = ctypes.windll.aygshell.SHSipInfo


class SIPINFO(ctypes.Structure) :

  _fields_ = [('cbSize', DWORD),('fdwFlags', DWORD),
              ('rcVisibleDesktop',RECT), ('rcSipRect', RECT),
              ('dwImDataSize', DWORD), ('pvImData', LPVOID)]

class SHMENUBARINFO(ctypes.Structure):

  _fields_ = [('cbSize', DWORD), ('hwndParent', HWND),
              ('dwFlags', DWORD), ('nToolBarId',UINT),
              ('hInstRes', HINSTANCE), ('nBmpId', INT),
              ('cBmpImages', INT), ('hwndMB', HWND),
              ('clrBk', COLORREF)]

class SHRGINFO(ctypes.Structure) :

  _fields_ = [('cbSize', DWORD), ('hwndClient', HWND),
              ('ptDown', POINT), ('dwFlags', DWORD)]

class SHACTIVATEINFO(ctypes.Structure) :
  _fields_ = [('cbSize', DWORD), ('hwndLastFocus', HWND),
              ('fSipUp', UINT,1), ('fSipOnDeactivation',UINT,1),
              ('fActive', UINT,1), ('fReserved', UINT,29)]

class SHINITDLGINFO(ctypes.Structure) :
  _fields_ = [('dwMask', DWORD), ('hDlg', HWND), ('dwFlags', DWORD) ]

SHInitDialog = ctypes.windll.aygshell.SHInitDialog
SHRecognizeGesture = ctypes.windll.aygshell.SHRecognizeGesture

SHRG_RETURNCMD = 1
GN_CONTEXTMENU = 1000
SHIDIF_DONEBUTTON = 1
SHIDIF_SIZEDLGFULLSCREEN = 4

try : 
  SHHandleWMActivate = ctypes.windll.aygshell.SHHandleWMActivate
  SHHandleWMSettingChange = ctypes.windll.aygshell.SHHandleWMSettingChange
except : # WinCe 4.20 bugfix (Thanks to Jan Ischebeck)
  SHHandleWMActivate = ctypes.windll.aygshell[84]
  SHHandleWMSettingChange = ctypes.windll.aygshell[83]
   
def InitSHActivateInfo():
  shai = SHACTIVATEINFO()
  ctypes.memset(byref(shai), 0, ctypes.sizeof(SHACTIVATEINFO))
  shai.cbSize = ctypes.sizeof(SHACTIVATEINFO)
  return shai
  
GetTextExtentExPointW = cdll.coredll.GetTextExtentExPointW

class SIZE(Structure):
    _fields_ = [('cx', LONG),
                ('cy', LONG)]
    
def GetTextExtent(hdc, string):
    n = len(string)
    size = SIZE()
    GetTextExtentExPointW(hdc, string, n, 0, 0, 0, byref(size))
    return size.cx, size.cy