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

from .w32api import *

ATL_IDW_BAND_FIRST = 0xEB00
HTREEITEM = HANDLE
HIMAGELIST = HANDLE

UINT_MAX = (1 << 32)

LVCF_FMT     =1
LVCF_WIDTH   =2
LVCF_TEXT    =4
LVCF_SUBITEM =8
LVCF_IMAGE= 16
LVCF_ORDER= 32

TVIF_TEXT    = 1
TVIF_IMAGE   =2
TVIF_PARAM   =4
TVIF_STATE   =8
TVIF_HANDLE = 16
TVIF_SELECTEDIMAGE  = 32
TVIF_CHILDREN      =  64
TVIF_INTEGRAL      =  0x0080
TVIF_DI_SETITEM    =  0x1000

LVIF_TEXT   = 1
LVIF_IMAGE  = 2
LVIF_PARAM  = 4
LVIF_STATE  = 8
LVIF_DI_SETITEM =  0x1000

LVIS_SELECTED = 0x0002

COMCTL32_VERSION = 0x020c
CCM_FIRST = 0x2000
CCM_SETVERSION = CCM_FIRST+0x7
CCM_GETVERSION = CCM_FIRST+0x8
TCS_BOTTOM = 0x2

class MaskedStructureType(Structure.__class__):
    def __new__(cls, name, bases, dct):
        keys = []
        for key in dct['_keys_']:
            keys.append((key[0], key[1]))
            if len(key) == 4: #masked key
                dct[key[3]] = property(None,
                                         lambda self, val, key = key:
                                         self.setProperty(key[0], key[2], val))
        dct['_keys_'] = keys
        return Structure.__class__.__new__(cls, name, bases, dct)
    
class MaskedStructure(Structure, metaclass=MaskedStructureType):
    _keys_ = []

    def setProperty(self, name, mask, value):
        setattr(self, self._mask_, getattr(self, self._mask_) | mask)
        setattr(self, name, value)

    def clear(self):
        setattr(self, self._mask_, 0)
        
class NMCBEENDEDIT(Structure):
    _keys_ = [("hdr", NMHDR),
                ("fChanged", BOOL),
                ("iNewSelection", INT),
                ("szText", POINTER(TCHAR)),
                ("iWhy", INT)]

class LVCOLUMN(MaskedStructure):
    _mask_ = 'mask'
    _keys_ = [("mask", UINT),
                ("fmt", INT, LVCF_FMT, "format"),
                ("cx", INT, LVCF_WIDTH, 'width'),
                ("pszText", LPTSTR, LVCF_TEXT, 'text'),
                ("cchTextMax", INT),
                ("iSubItem", INT),
                ("iImage", INT),
                ("iOrder", INT)]

class LVITEM(Structure):
    _keys_ = [("mask", UINT),
                ("iItem", INT),
                ("iSubItem", INT),
                ("state", UINT),
                ("stateMask", UINT),
                ("pszText", LPTSTR),
                ("cchTextMax", INT),
                ("iImage", INT),
                ("lParam", LPARAM),
                ("iIndent", INT)]

class LV_DISPINFO(Structure):
    _keys_ = [("hdr", NMHDR),
                ("item", LVITEM)]
    

class TV_ITEMEX(MaskedStructure):
    _mask_ = 'mask'
    _keys_ = [("mask", UINT),
                ("hItem", HTREEITEM),
                ("state", UINT),
                ("stateMask", UINT),
                ("pszText", LPTSTR, TVIF_TEXT, 'text'),
                ("cchTextMax", INT),
                ("iImage", INT, TVIF_IMAGE, 'image'),
                ("iSelectedImage", INT, TVIF_SELECTEDIMAGE, 'selectedImage'),
                ("cChildren", INT, TVIF_CHILDREN, 'children'),
                ("lParam", LPARAM, TVIF_PARAM, 'param'),
                ("iIntegral", INT)]

class TVITEMOLD(Structure):
    _keys_ = [("mask", UINT),
                ("hItem", HTREEITEM),
                ("state", UINT),
                ("stateMask", UINT),
                ("pszText", LPTSTR),
                ("cchTextMax", INT),
                ("iImage", INT),
                ("iSelectedImage", INT),
                ("cChildren", INT),
                ("lParam", LPARAM)]

class TVITEM(MaskedStructure):
    _mask_ = 'mask'
    _keys_ = [("mask", UINT),
                ("hItem", HTREEITEM),
                ("state", UINT),
                ("stateMask", UINT),
                ("pszText", LPTSTR, TVIF_TEXT, 'text'),
                ("cchTextMax", INT),
                ("iImage", INT, TVIF_IMAGE,'image'),
                ("iSelectedImage", INT, TVIF_SELECTEDIMAGE, 'selectedImage'),
                ("cChildren", INT, TVIF_CHILDREN,'children'), 
                ("lParam", LPARAM, TVIF_PARAM,'param')]

class TBBUTTON(Structure):
    _keys_ = [("iBitmap", INT),
                ("idCommand", INT),
                ("fsState", BYTE),
                ("fsStyle", BYTE),
                #("bReserved", BYTE * 2),
                ("dwData", DWORD_PTR),
                ("iString", INT_PTR)]

class TBBUTTONINFO(Structure):
    _keys_ = [("cbSize", UINT),
                ("dwMask", DWORD),
                ("idCommand", INT),
                ("iImage", INT),
                ("fsState", BYTE),
                ("fsStyle", BYTE),
                ("cx", WORD),
                ("lParam", DWORD_PTR),
                ("pszText", LPTSTR),
                ("cchText", INT)]

class TVINSERTSTRUCT(Structure):
    _keys_ = [("hParent", HTREEITEM),
                ("hInsertAfter", HTREEITEM),
                ("item", TVITEM)]

class TCITEM(Structure):
    _keys_ = [("mask", UINT),
                ("dwState", DWORD),
                ("dwStateMask", DWORD),
                ("pszText", LPTSTR),
                ("cchTextMax", INT),
                ("iImage", INT),
                ("lParam", LPARAM)]

class NMTREEVIEW(Structure):
    _keys_ = [("hdr", NMHDR),
                ("action", UINT),
                ("itemOld", TVITEM),
                ("itemNew", TVITEM),
                ("ptDrag", POINT)]

class NMLISTVIEW(Structure):
    _keys_ = [("hrd", NMHDR),
                ("iItem", INT),
                ("iSubItem", INT),
                ("uNewState", UINT),
                ("uOldState", UINT),
                ("uChanged", UINT),
                ("ptAction", POINT),
                ("lParam", LPARAM)]
    
class INITCOMMONCONTROLSEX(Structure):
    _keys_ = [("dwSize", DWORD),
                ("dwICC", DWORD)]

class REBARINFO(Structure):
    _keys_ = [("cbSize", UINT),
                ("fMask", UINT),
                ("himl", HIMAGELIST)]

class REBARBANDINFO(Structure):
    _keys_ = [("cbSize", UINT),
                ("fMask", UINT),
                ("fStyle", UINT),
                ("clrFore", COLORREF),
                ("clrBack", COLORREF),
                ("lpText", LPTSTR),
                ("cch", UINT),
                ("iImage", INT),
                ("hwndChild", HWND),
                ("cxMinChild", UINT),
                ("cyMinChild", UINT),
                ("cx", UINT),
                ("hbmBack", HBITMAP),
                ("wID", UINT),
                ("cyChild", UINT),
                ("cyMaxChild", UINT),
                ("cyIntegral", UINT),
                ("cxIdeal", UINT),
                ("lParam", LPARAM),
                ("cxHeader", UINT)]

class NMTOOLBAR(Structure):
    _keys_ = [("hdr", NMHDR),
                ("iItem", INT),
                ("tbButton", TBBUTTON),
                ("cchText", INT),
                ("pszText", LPTSTR),
                ("rcButton", RECT)]

class NMTBHOTITEM(Structure):
    _keys_ = [("hdr", NMHDR),
                ("idOld", INT),
                ("idNew", INT),
                ("dwFlags", DWORD)]

class PBRANGE(Structure):
    _keys_ = [("iLow", INT),
                ("iHigh", INT)]
    
class NMITEMACTIVATE(Structure):
    _keys_ = [("hdr", NMHDR),
                ("iItem", c_int),
                ("iSubItem", c_int),
                ("uNewState", UINT),
                ("uOldState", UINT),
                ("uChanged", UINT),
                ("ptAction", POINT),
                ("lParam", LPARAM),
                ("uKeyFlags", UINT)]

NM_FIRST    =   UINT_MAX

SBS_BOTTOMALIGN = 4
SBS_HORZ = 0
SBS_LEFTALIGN = 2
SBS_RIGHTALIGN = 4
SBS_SIZEBOX = 8
SBS_SIZEBOXBOTTOMRIGHTALIGN = 4
SBS_SIZEBOXTOPLEFTALIGN = 2
SBS_SIZEGRIP = 16
SBS_TOPALIGN = 2
SBS_VERT = 1

CCS_NODIVIDER =	64
CCS_NOPARENTALIGN = 8
CCS_NORESIZE = 4
CCS_TOP = 1


CBS_DROPDOWN = 2

RBBS_BREAK = 1
RBBS_FIXEDSIZE = 2
RBBS_CHILDEDGE = 4
RBBS_HIDDEN = 8
RBBS_NOVERT = 16
RBBS_FIXEDBMP = 32
RBBS_VARIABLEHEIGHT = 64
RBBS_GRIPPERALWAYS = 128
RBBS_NOGRIPPER = 256

RBS_TOOLTIPS = 256
RBS_VARHEIGHT = 512
RBS_BANDBORDERS = 1024
RBS_FIXEDORDER = 2048

RBS_REGISTERDROP = 4096
RBS_AUTOSIZE = 8192
RBS_VERTICALGRIPPER = 16384
RBS_DBLCLKTOGGLE = 32768

RBN_FIRST	= ((UINT_MAX) - 831)
RBN_HEIGHTCHANGE = RBN_FIRST

TBSTYLE_FLAT = 2048
TBSTYLE_LIST = 4096
TBSTYLE_DROPDOWN = 8
TBSTYLE_TRANSPARENT = 0x8000
TBSTYLE_REGISTERDROP = 0x4000
TBSTYLE_BUTTON = 0x0000
TBSTYLE_AUTOSIZE = 0x0010
    
TB_ADDBITMAP = 0x0413
TB_ENABLEBUTTON = 0x401
TB_CHECKBUTTON = 0x402
TB_ISBUTTONCHECKED = WM_USER+10
TB_BUTTONSTRUCTSIZE = WM_USER+30
TB_ADDBUTTONS       = WM_USER+20
TB_INSERTBUTTONA    = WM_USER + 21
TB_INSERTBUTTON     = WM_USER + 21
TB_BUTTONCOUNT      = WM_USER + 24
TB_GETITEMRECT      = WM_USER + 29
TB_SETBUTTONINFOW  =  WM_USER + 64
TB_SETBUTTONINFOA  =  WM_USER + 66
TB_SETBUTTONINFO   =  TB_SETBUTTONINFOA
TB_SETIMAGELIST    =  WM_USER + 48
TB_SETDRAWTEXTFLAGS =  WM_USER + 70
TB_PRESSBUTTON       = WM_USER + 3
TB_GETRECT        =      (WM_USER + 51)
TB_SETHOTITEM   =        (WM_USER + 72)
TB_HITTEST     =         (WM_USER + 69)
TB_GETHOTITEM  =         (WM_USER + 7)
TB_SETBUTTONSIZE     =  (WM_USER + 31)
TB_AUTOSIZE          =  (WM_USER + 33)
TB_DELETEBUTTON = WM_USER + 22

TVIF_TEXT    = 1
TVIF_IMAGE   =2
TVIF_PARAM   =4
TVIF_STATE   =8
TVIF_HANDLE = 16
TVIF_SELECTEDIMAGE  = 32
TVIF_CHILDREN      =  64
TVIF_INTEGRAL      =  0x0080
TVIF_DI_SETITEM    =  0x1000
 
TVI_ROOT     = 0xFFFF0000
TVI_FIRST    = 0xFFFF0001
TVI_LAST     = 0xFFFF0002
TVI_SORT     = 0xFFFF0003

TVGN_CHILD   =  4
TVGN_NEXT    =  1
TVGN_ROOT    =  0
TVGN_CARET   =           0x0009

TVIS_FOCUSED = 1
TVIS_SELECTED =       2
TVIS_CUT    = 4
TVIS_DROPHILITED   =  8
TVIS_BOLD  =  16
TVIS_EXPANDED      =  32
TVIS_EXPANDEDONCE  =  64
TVIS_OVERLAYMASK   =  0xF00
TVIS_STATEIMAGEMASK = 0xF000
TVIS_USERMASK      =  0xF000

TV_FIRST = 0x1100
TVM_INSERTITEMA =     TV_FIRST
TVM_INSERTITEMW =    (TV_FIRST+50)
TVM_INSERTITEM = TVM_INSERTITEMW
TVM_SETIMAGELIST =    (TV_FIRST+9)
TVM_DELETEITEM   =   (TV_FIRST+1)
TVM_GETNEXTITEM   =   (TV_FIRST+10)
TVM_EXPAND =   (TV_FIRST+2)
TVM_GETITEMSTATE=        (TV_FIRST + 39)
TVM_ENSUREVISIBLE=       (TV_FIRST + 20)
TVM_SELECTITEM=          (TV_FIRST + 11)
TVM_SETITEMA=            (TV_FIRST + 13)
TVM_SETITEMW =           (TV_FIRST + 63)
TVM_SETITEM= TVM_SETITEMW
TVM_GETITEMA=            (TV_FIRST + 12)
TVM_GETITEMW =           (TV_FIRST + 62)
TVM_GETITEM = TVM_GETITEMW


TVS_HASBUTTONS =       1
TVS_HASLINES = 2
TVS_LINESATROOT =      4
TVS_EDITLABELS  =      8
TVS_DISABLEDRAGDROP =  16
TVS_SHOWSELALWAYS =   32
TVS_CHECKBOXES =  256
TVS_TOOLTIPS = 128
TVS_RTLREADING = 64
TVS_TRACKSELECT = 512
TVS_FULLROWSELECT = 4096
TVS_INFOTIP = 2048
TVS_NONEVENHEIGHT = 16384
TVS_NOSCROLL  = 8192
TVS_SINGLEEXPAND  =1024
TVS_NOHSCROLL   =     0x8000

CBEN_FIRST  =  (UINT_MAX) - 800
CBEN_ENDEDITA = CBEN_FIRST - 5
CBEN_ENDEDITW = CBEN_FIRST - 6
CBEN_ENDEDIT = CBEN_ENDEDITA

# trackbar styles
TBS_AUTOTICKS =           0x0001
TBS_VERT =                0x0002
TBS_HORZ =                0x0000
TBS_TOP =                 0x0004
TBS_BOTTOM =              0x0000
TBS_LEFT =                0x0004
TBS_RIGHT =               0x0000
TBS_BOTH =                0x0008
TBS_NOTICKS =             0x0010
TBS_ENABLESELRANGE =      0x0020
TBS_FIXEDLENGTH =         0x0040
TBS_NOTHUMB =             0x0080
TBS_TOOLTIPS =            0x0100

# trackbar messages
TBM_GETPOS =              (WM_USER)
TBM_GETRANGEMIN =         (WM_USER+1)
TBM_GETRANGEMAX =         (WM_USER+2)
TBM_GETTIC =              (WM_USER+3)
TBM_SETTIC =              (WM_USER+4)
TBM_SETPOS =              (WM_USER+5)
TBM_SETRANGE =            (WM_USER+6)
TBM_SETRANGEMIN =         (WM_USER+7)
TBM_SETRANGEMAX =         (WM_USER+8)
TBM_CLEARTICS =           (WM_USER+9)
TBM_SETSEL =              (WM_USER+10)
TBM_SETSELSTART =         (WM_USER+11)
TBM_SETSELEND =           (WM_USER+12)
TBM_GETPTICS =            (WM_USER+14)
TBM_GETTICPOS =           (WM_USER+15)
TBM_GETNUMTICS =          (WM_USER+16)
TBM_GETSELSTART =         (WM_USER+17)
TBM_GETSELEND =           (WM_USER+18)
TBM_CLEARSEL =            (WM_USER+19)
TBM_SETTICFREQ =          (WM_USER+20)
TBM_SETPAGESIZE =         (WM_USER+21)
TBM_GETPAGESIZE =         (WM_USER+22)
TBM_SETLINESIZE =         (WM_USER+23)
TBM_GETLINESIZE =         (WM_USER+24)
TBM_GETTHUMBRECT =        (WM_USER+25)
TBM_GETCHANNELRECT =      (WM_USER+26)
TBM_SETTHUMBLENGTH =      (WM_USER+27)
TBM_GETTHUMBLENGTH =      (WM_USER+28)
TBM_SETTOOLTIPS =         (WM_USER+29)
TBM_GETTOOLTIPS =         (WM_USER+30)
TBM_SETTIPSIDE =          (WM_USER+31)
TBM_SETBUDDY =            (WM_USER+32) 
TBM_GETBUDDY =            (WM_USER+33) 

# trackbar top-side flags
TBTS_TOP =                0
TBTS_LEFT =               1
TBTS_BOTTOM =             2
TBTS_RIGHT =              3


TB_LINEUP =               0
TB_LINEDOWN =             1
TB_PAGEUP =               2
TB_PAGEDOWN =             3
TB_THUMBPOSITION =        4
TB_THUMBTRACK =           5
TB_TOP =                  6
TB_BOTTOM =               7
TB_ENDTRACK =             8

# trackbar custom draw item specs
TBCD_TICS =    0x0001
TBCD_THUMB =   0x0002
TBCD_CHANNEL = 0x0003



STATUSCLASSNAME = "msctls_statusbar32"

REBARCLASSNAMEW = "ReBarWindow32"
REBARCLASSNAMEA = "ReBarWindow32"
REBARCLASSNAME = REBARCLASSNAMEA

PROGRESS_CLASSW = "msctls_progress32"
PROGRESS_CLASSA = "msctls_progress32"
PROGRESS_CLASS = PROGRESS_CLASSA

TRACKBAR_CLASSW = "msctls_trackbar32"
TRACKBAR_CLASSA = "msctls_trackbar32"
TRACKBAR_CLASS = TRACKBAR_CLASSA


EDIT = "edit"
BUTTON = "button"

WC_COMBOBOXEXW = "ComboBoxEx32"
WC_COMBOBOXEXA = "ComboBoxEx32"
WC_COMBOBOXEX = WC_COMBOBOXEXA

WC_TREEVIEWA = "SysTreeView32"
WC_TREEVIEWW = "SysTreeView32"
WC_TREEVIEW = WC_TREEVIEWA

WC_LISTVIEWA = "SysListView32"
WC_LISTVIEWW = "SysListView32"
WC_LISTVIEW = WC_LISTVIEWA

TOOLBARCLASSNAMEW = "ToolbarWindow32"
TOOLBARCLASSNAMEA = "ToolbarWindow32"
TOOLBARCLASSNAME = TOOLBARCLASSNAMEA

WC_TABCONTROLA =    "SysTabControl32"
WC_TABCONTROLW =      "SysTabControl32"
WC_TABCONTROL = WC_TABCONTROLA

LVS_ICON    = 0
LVS_REPORT   =1
LVS_SMALLICON =       2
LVS_LIST    = 3
LVS_TYPEMASK= 3
LVS_SINGLESEL=        4
LVS_SHOWSELALWAYS=    8
LVS_SORTASCENDING =   16
LVS_SORTDESCENDING =  32
LVS_SHAREIMAGELISTS = 64
LVS_NOLABELWRAP     = 128
LVS_AUTOARRANGE     = 256
LVS_EDITLABELS      = 512
LVS_NOSCROLL= 0x2000
LVS_TYPESTYLEMASK  =  0xfc00
LVS_ALIGNTOP= 0
LVS_ALIGNLEFT =       0x800
LVS_ALIGNMASK  =      0xc00
LVS_OWNERDRAWFIXED=   0x400
LVS_NOCOLUMNHEADER =  0x4000
LVS_NOSORTHEADER   =  0x8000
LVS_OWNERDATA =4096
LVS_EX_CHECKBOXES= 4
LVS_EX_FULLROWSELECT= 32
LVS_EX_GRIDLINES =1
LVS_EX_HEADERDRAGDROP= 16
LVS_EX_ONECLICKACTIVATE= 64
LVS_EX_SUBITEMIMAGES= 2
LVS_EX_TRACKSELECT= 8
LVS_EX_TWOCLICKACTIVATE= 128
LVS_EX_FLATSB       = 0x00000100
LVS_EX_REGIONAL     = 0x00000200
LVS_EX_INFOTIP      = 0x00000400
LVS_EX_UNDERLINEHOT = 0x00000800
LVS_EX_UNDERLINECOLD= 0x00001000
LVS_EX_MULTIWORKAREAS =       0x00002000
LVS_EX_LABELTIP     = 0x00004000
LVS_EX_BORDERSELECT = 0x00008000

LVIS_FOCUSED         =   0x0001
LVIS_SELECTED        =   0x0002
LVIS_CUT             =   0x0004
LVIS_DROPHILITED     =   0x0008
LVIS_ACTIVATING      =   0x0020

LVIS_OVERLAYMASK      =  0x0F00
LVIS_STATEIMAGEMASK   =  0xF000

LVM_FIRST = 0x1000
LVM_INSERTCOLUMNA = (LVM_FIRST+27)
LVM_INSERTCOLUMNW = (LVM_FIRST+97)
LVM_INSERTCOLUMN = LVM_INSERTCOLUMNW
LVM_INSERTITEMA = (LVM_FIRST+7)
LVM_SETITEMA = (LVM_FIRST+6)
LVM_INSERTITEMW = (LVM_FIRST+77)
LVM_SETITEMW = (LVM_FIRST+76)
LVM_INSERTITEM = LVM_INSERTITEMW
LVM_SETITEM = LVM_SETITEMW
LVM_DELETEALLITEMS =  (LVM_FIRST + 9)
LVM_SETITEMSTATE  =  (LVM_FIRST + 43)
LVM_GETITEMCOUNT  =  (LVM_FIRST + 4)
LVM_SETITEMCOUNT  =  (LVM_FIRST + 47)
LVM_GETITEMSTATE   =  (LVM_FIRST + 44)
LVM_GETSELECTEDCOUNT =   (LVM_FIRST + 50)
LVM_SETCOLUMNA  =        (LVM_FIRST + 26)
LVM_SETCOLUMNW  =        (LVM_FIRST + 96)
LVM_SETCOLUMN = LVM_SETCOLUMNW
LVM_SETCOLUMNWIDTH =  (LVM_FIRST + 30)
LVM_GETITEMA   =         (LVM_FIRST + 5)
LVM_GETITEMW   =         (LVM_FIRST + 75)
LVM_GETITEM = LVM_GETITEMW
LVM_SETEXTENDEDLISTVIEWSTYLE = (LVM_FIRST + 54)
LVM_GETNEXTITEM = (LVM_FIRST + 12)
LVS_SHAREIL = 0x4
LVM_SETIMAGELIST = (LVM_FIRST + 3)

LVNI_SELECTED = 0x2

LVN_FIRST = (UINT_MAX) - 100
LVN_ITEMCHANGING    =    (LVN_FIRST-0)
LVN_ITEMCHANGED     =    (LVN_FIRST-1)
LVN_INSERTITEM      =    (LVN_FIRST-2)
LVN_DELETEITEM       =   (LVN_FIRST-3)
LVN_DELETEALLITEMS    =  (LVN_FIRST-4)
LVN_BEGINLABELEDITA   =  (LVN_FIRST-5)
LVN_BEGINLABELEDITW   =  (LVN_FIRST-75)
LVN_ENDLABELEDITA     =  (LVN_FIRST-6)
LVN_ENDLABELEDITW     =  (LVN_FIRST-76)
LVN_COLUMNCLICK       =  (LVN_FIRST-8)
LVN_BEGINDRAG         =  (LVN_FIRST-9)
LVN_BEGINRDRAG        =  (LVN_FIRST-11)
LVN_GETDISPINFO = (LVN_FIRST - 77)

NM_OUTOFMEMORY    =      (NM_FIRST-1)
NM_CLICK          =      (NM_FIRST-2)   
NM_DBLCLK         =      (NM_FIRST-3)
NM_RETURN         =      (NM_FIRST-4)
NM_RCLICK         =      (NM_FIRST-5)   
NM_RDBLCLK        =      (NM_FIRST-6)
NM_SETFOCUS       =      (NM_FIRST-7)
NM_KILLFOCUS      =      (NM_FIRST-8)
NM_CUSTOMDRAW     =      (NM_FIRST-12)
NM_HOVER          =      (NM_FIRST-13)
NM_NCHITTEST      =      (NM_FIRST-14)  
NM_KEYDOWN        =      (NM_FIRST-15)  
NM_RELEASEDCAPTURE=      (NM_FIRST-16)
NM_SETCURSOR      =      (NM_FIRST-17)  
NM_CHAR           =      (NM_FIRST-18)  

LVCFMT_LEFT = 0
LVCFMT_RIGHT= 1
LVCFMT_CENTER   =     2
LVCFMT_JUSTIFYMASK =  3
LVCFMT_BITMAP_ON_RIGHT =4096
LVCFMT_COL_HAS_IMAGES = 32768
LVCFMT_IMAGE =2048


ICC_LISTVIEW_CLASSES =1
ICC_TREEVIEW_CLASSES =2
ICC_BAR_CLASSES      =4
ICC_TAB_CLASSES      =8
ICC_UPDOWN_CLASS =16
ICC_PROGRESS_CLASS =32
ICC_HOTKEY_CLASS =64
ICC_ANIMATE_CLASS= 128
ICC_WIN95_CLASSES= 255
ICC_DATE_CLASSES =256
ICC_USEREX_CLASSES =512
ICC_COOL_CLASSES =1024
ICC_INTERNET_CLASSES =2048
ICC_PAGESCROLLER_CLASS =4096
ICC_NATIVEFNTCTL_CLASS= 8192

TCN_FIRST  =  (UINT_MAX) -550
TCN_LAST   =  (UINT_MAX) -580
TCN_KEYDOWN   =  TCN_FIRST
TCN_SELCHANGE =        (TCN_FIRST-1)
TCN_SELCHANGING  =     (TCN_FIRST-2)

TVE_COLLAPSE =1
TVE_EXPAND   =2
TVE_TOGGLE   =3
TVE_COLLAPSERESET   = 0x8000

TCM_FIRST   = 0x1300
TCM_INSERTITEMA  =    (TCM_FIRST+7)
TCM_INSERTITEMW  =   (TCM_FIRST+62)
TCM_INSERTITEM = TCM_INSERTITEMW
TCM_ADJUSTRECT = (TCM_FIRST+40)
TCM_GETCURSEL   =     (TCM_FIRST+11)
TCM_SETCURSEL   =     (TCM_FIRST+12)
TCM_GETITEMA = (TCM_FIRST+5)
TCM_GETITEMW = (TCM_FIRST+60)
TCM_GETITEM = TCM_GETITEMW
TCM_DELETEITEM = (TCM_FIRST + 8)
TCM_GETITEMCOUNT = (TCM_FIRST + 4)

TVN_FIRST  =  ((UINT_MAX)-400)
TVN_LAST   =  ((UINT_MAX)-499)
TVN_ITEMEXPANDINGA =  (TVN_FIRST-5)
TVN_ITEMEXPANDINGW =  (TVN_FIRST-54)
TVN_ITEMEXPANDING = TVN_ITEMEXPANDINGW
TVN_SELCHANGEDA  =    (TVN_FIRST-2)
TVN_SELCHANGEDW  =    (TVN_FIRST-51)
TVN_SELCHANGED  =  TVN_SELCHANGEDW
TVN_DELETEITEMA  =     (TVN_FIRST-9)
TVN_DELETEITEMW  =    (TVN_FIRST-58)
TVN_DELETEITEM = TVN_DELETEITEMW


ES_LEFT = 0
ES_CENTER  = 1
ES_RIGHT    =   0x0002
ES_MULTILINE   = 0x0004
ES_UPPERCASE  =  0x0008
ES_LOWERCASE =   0x0010
ES_PASSWORD   =  0x0020
ES_AUTOVSCROLL = 0x0040
ES_AUTOHSCROLL  =0x0080
ES_NOHIDESEL   = 0x0100
ES_COMBOBOX 	=0x0200
ES_OEMCONVERT  = 0x0400
ES_READONLY    = 0x0800
ES_WANTRETURN  = 0x1000

SB_SIMPLE =   (WM_USER+9)
SB_SETTEXTA = (WM_USER+1)
SB_SETTEXTW = (WM_USER+11)
SB_SETTEXT = SB_SETTEXTW

SBT_OWNERDRAW   =     0x1000
SBT_NOBORDERS   =     256
SBT_POPOUT   = 512
SBT_RTLREADING =      1024
SBT_OWNERDRAW  =      0x1000
SBT_NOBORDERS  =      256
SBT_POPOUT   = 512
SBT_RTLREADING = 1024
SBT_TOOLTIPS = 0x0800

TBN_FIRST          =  ((UINT_MAX)-700)
TBN_DROPDOWN       =     (TBN_FIRST - 10)
TBN_HOTITEMCHANGE  =  (TBN_FIRST - 13)
TBDDRET_DEFAULT       =  0
TBDDRET_NODEFAULT     =  1
TBDDRET_TREATPRESSED  =  2

PBS_SMOOTH   = 0x01
PBS_VERTICAL = 0x04

CCM_FIRST      = 0x2000 # Common control shared messages
CCM_SETBKCOLOR = (CCM_FIRST + 1)

PBM_SETRANGE    = (WM_USER+1)
PBM_SETPOS      = (WM_USER+2)
PBM_DELTAPOS    = (WM_USER+3)
PBM_SETSTEP     = (WM_USER+4)
PBM_STEPIT      = (WM_USER+5)
PBM_SETRANGE32  = (WM_USER+6)
PBM_GETRANGE    = (WM_USER+7)
PBM_GETPOS      = (WM_USER+8)
PBM_SETBARCOLOR = (WM_USER+9)
PBM_SETBKCOLOR  = CCM_SETBKCOLOR


# ListBox Messages
LB_ADDSTRING = 384
LB_INSERTSTRING = 385
LB_DELETESTRING = 386
LB_RESETCONTENT = 388
LB_GETCOUNT = 395
LB_SETTOPINDEX = 407
LB_GETCURSEL =  0x0188

# ComboBox styles
CBS_DROPDOWN         = 0x0002
CBS_DROPDOWNLIST      =0x0003
CBS_AUTOHSCROLL       =0x0040
CBS_OEMCONVERT      =  0x0080
CBS_SORT             = 0x0100
CBS_HASSTRINGS       = 0x0200
CBS_NOINTEGRALHEIGHT = 0x0400
CBS_DISABLENOSCROLL  = 0x0800
CBS_UPPERCASE         =  0x2000
CBS_LOWERCASE          = 0x4000

ImageList_Create = windll.coredll.ImageList_Create
ImageList_Destroy = windll.coredll.ImageList_Destroy
ImageList_Add = windll.coredll.ImageList_Add
ImageList_AddMasked = windll.coredll.ImageList_AddMasked
#ImageList_AddIcon = windll.coredll.ImageList_AddIcon
ImageList_SetBkColor = windll.coredll.ImageList_SetBkColor
ImageList_ReplaceIcon = windll.coredll.ImageList_ReplaceIcon

def ImageList_AddIcon(a, b):
    return ImageList_ReplaceIcon(a, -1, b)

InitCommonControlsEx = windll.commctrl.InitCommonControlsEx

# Nouveautes

# Static control 

SS_LEFT = 0x00000000
SS_CENTER = 0x00000001
SS_RIGHT = 0x00000002
SS_ICON = 0x00000003
SS_LEFTNOWORDWRAP = 0x0000000C
SS_BITMAP = 0x0000000E
SS_NOPREFIX = 0x00000080
SS_CENTERIMAGE = 0x00000200
SS_NOTIFY = 0x00000100
STN_CLICKED = 0
STN_ENABLE = 2
STN_DISABLE = 3
STM_SETIMAGE = 0x0172
STM_GETIMAGE = 0x0173

# Button control

BS_PUSHBUTTON = 0x00000000
BS_DEFPUSHBUTTON = 0x00000001
BS_CHECKBOX = 0x00000002
BS_AUTOCHECKBOX = 0x00000003
BS_RADIOBUTTON = 0x00000004
BS_3STATE = 0x00000005
BS_AUTO3STATE = 0x00000006
BS_GROUPBOX = 0x00000007
BS_AUTORADIOBUTTON = 0x00000009
BS_OWNERDRAW = 0x0000000B
BS_LEFTTEXT = 0x00000020
BS_TEXT = 0x00000000
BS_LEFT = 0x00000100
BS_RIGHT = 0x00000200
BS_CENTER = 0x00000300
BS_TOP = 0x00000400
BN_CLICKED = 0
BN_PAINT = 1
BN_DBLCLK = 5
BN_SETFOCUS = 6
BN_KILLFOCUS = 7
BM_GETCHECK = 0x00F0
BM_SETCHECK = 0x00F1
BM_GETSTATE = 0x00F2
BM_SETSTATE = 0x00F3
BM_SETSTYLE = 0x00F4
BM_CLICK = 0x00F5
BST_UNCHECKED = 0x0000
BST_CHECKED = 0x0001
BST_INDETERMINATE = 0x0002
BST_PUSHED = 0x0004
BST_FOCUS = 0x0008

# Edit control

ES_LEFT = 0x0000
ES_CENTER = 0x0001
ES_RIGHT = 0x0002
ES_MULTILINE = 0x0004
ES_UPPERCASE = 0x0008
ES_LOWERCASE = 0x0010
ES_PASSWORD = 0x0020
ES_AUTOVSCROLL = 0x0040
ES_AUTOHSCROLL = 0x0080
ES_NOHIDESEL = 0x0100
ES_COMBOBOX = 0x0200
ES_OEMCONVERT = 0x0400
ES_READONLY = 0x0800
ES_WANTRETURN = 0x1000
ES_NUMBER = 0x2000
EN_SETFOCUS = 0x0100
EN_KILLFOCUS = 0x0200
EN_CHANGE = 0x0300
EN_UPDATE = 0x0400
EN_ERRSPACE = 0x0500
EN_MAXTEXT = 0x0501
EN_HSCROLL = 0x0601
EN_VSCROLL = 0x0602
EC_LEFTMARGIN = 0x0001
EC_RIGHTMARGIN = 0x0002
EC_USEFONTINFO = 0xffff
EM_GETSEL = 0x00B0
EM_SETSEL = 0x00B1
EM_GETRECT = 0x00B2
EM_SETRECT = 0x00B3
EM_SETRECTNP = 0x00B4
EM_SCROLL = 0x00B5
EM_LINESCROLL = 0x00B6
EM_SCROLLCARET = 0x00B7
EM_GETMODIFY = 0x00B8
EM_SETMODIFY = 0x00B9
EM_GETLINECOUNT = 0x00BA
EM_LINEINDEX = 0x00BB
EM_LINELENGTH = 0x00C1
EM_REPLACESEL = 0x00C2
EM_GETLINE = 0x00C4
EM_LIMITTEXT = 0x00C5
EM_CANUNDO = 0x00C6
EM_UNDO = 0x00C7
EM_FMTLINES = 0x00C8
EM_LINEFROMCHAR = 0x00C9
EM_SETTABSTOPS = 0x00CB
EM_SETPASSWORDCHAR = 0x00CC
EM_EMPTYUNDOBUFFER = 0x00CD
EM_GETFIRSTVISIBLELINE = 0x00CE
EM_SETREADONLY = 0x00CF
EM_GETPASSWORDCHAR = 0x00D2
EM_SETMARGINS = 0x00D3
EM_GETMARGINS = 0x00D4
EM_SETLIMITTEXT = EM_LIMITTEXT
EM_GETLIMITTEXT = 0x00D5
EM_POSFROMCHAR = 0x00D6
EM_CHARFROMPOS = 0x00D7

# List Box control

LB_OKAY = 0
LB_ERR = (-1)
LB_ERRSPACE = (-2)
LBN_ERRSPACE = (-2)
LBN_SELCHANGE = 1
LBN_DBLCLK = 2
LBN_SELCANCEL = 3
LBN_SETFOCUS = 4
LBN_KILLFOCUS = 5
LB_ADDSTRING = 0x0180
LB_INSERTSTRING = 0x0181
LB_DELETESTRING = 0x0182
LB_SELITEMRANGEEX = 0x0183
LB_RESETCONTENT = 0x0184
LB_SETSEL = 0x0185
LB_SETCURSEL = 0x0186
LB_GETSEL = 0x0187
LB_GETCURSEL = 0x0188
LB_GETTEXT = 0x0189
LB_GETTEXTLEN = 0x018A
LB_GETCOUNT = 0x018B
LB_SELECTSTRING = 0x018C
LB_GETTOPINDEX = 0x018E
LB_FINDSTRING = 0x018F
LB_GETSELCOUNT = 0x0190
LB_GETSELITEMS = 0x0191
LB_SETTABSTOPS = 0x0192
LB_GETHORIZONTALEXTENT = 0x0193
LB_SETHORIZONTALEXTENT = 0x0194
LB_SETCOLUMNWIDTH = 0x0195
LB_SETTOPINDEX = 0x0197
LB_GETITEMRECT = 0x0198
LB_GETITEMDATA = 0x0199
LB_SETITEMDATA = 0x019A
LB_SELITEMRANGE = 0x019B
LB_SETANCHORINDEX = 0x019C
LB_GETANCHORINDEX = 0x019D
LB_SETCARETINDEX = 0x019E
LB_GETCARETINDEX = 0x019F
LB_SETITEMHEIGHT = 0x01A0
LB_GETITEMHEIGHT = 0x01A1
LB_FINDSTRINGEXACT = 0x01A2
LB_SETLOCALE = 0x01A5
LB_GETLOCALE = 0x01A6
LB_INITSTORAGE = 0x01A8
LB_ITEMFROMPOINT = 0x01A9
LB_RESERVED0x01C0 = 0x01C0
LB_RESERVED0x01C1 = 0x01C1
LB_MSGMAX = 0x01C9
LB_MSGMAX = 0x01A8
LBS_NOTIFY = 0x0001
LBS_SORT = 0x0002
LBS_NOREDRAW = 0x0004
LBS_MULTIPLESEL = 0x0008
LBS_HASSTRINGS = 0x0040
LBS_USETABSTOPS = 0x0080
LBS_NOINTEGRALHEIGHT = 0x0100
LBS_MULTICOLUMN = 0x0200
LBS_WANTKEYBOARDINPUT = 0x0400
LBS_EXTENDEDSEL = 0x0800
LBS_DISABLENOSCROLL = 0x1000
LBS_NODATA = 0x2000
LBS_NOSEL = 0x4000
LBS_STANDARD = (LBS_NOTIFY | LBS_SORT | WS_VSCROLL | WS_BORDER)
LBS_EX_CONSTSTRINGDATA = 0x00000002

LVM_DELETECOLUMN = (LVM_FIRST + 28) 

CB_OKAY = 0
CB_ERR = (-1)
CB_ERRSPACE = (-2)
CBN_ERRSPACE = (-1)
CBN_SELCHANGE = 1
CBN_DBLCLK = 2
CBN_SETFOCUS = 3
CBN_KILLFOCUS = 4
CBN_EDITCHANGE = 5
CBN_EDITUPDATE = 6
CBN_DROPDOWN = 7
CBN_CLOSEUP = 8
CBN_SELENDOK = 9
CBN_SELENDCANCEL = 10
CBS_DROPDOWN = 0x0002
CBS_DROPDOWNLIST = 0x0003
CBS_AUTOHSCROLL = 0x0040
CBS_OEMCONVERT = 0x0080
CBS_SORT = 0x0100
CBS_HASSTRINGS = 0x0200
CBS_NOINTEGRALHEIGHT = 0x0400
CBS_DISABLENOSCROLL = 0x0800
CBS_UPPERCASE = 0x2000
CBS_LOWERCASE = 0x4000
CBS_EX_CONSTSTRINGDATA = 0x00000002
CB_GETEDITSEL = 0x0140
CB_LIMITTEXT = 0x0141
CB_SETEDITSEL = 0x0142
CB_ADDSTRING = 0x0143
CB_DELETESTRING = 0x0144
CB_GETCOUNT = 0x0146
CB_GETCURSEL = 0x0147
CB_GETLBTEXT = 0x0148
CB_GETLBTEXTLEN = 0x0149
CB_INSERTSTRING = 0x014A
CB_RESETCONTENT = 0x014B
CB_FINDSTRING = 0x014C
CB_SELECTSTRING = 0x014D
CB_SETCURSEL = 0x014E
CB_SHOWDROPDOWN = 0x014F
CB_GETITEMDATA = 0x0150
CB_SETITEMDATA = 0x0151
CB_GETDROPPEDCONTROLRECT = 0x0152
CB_SETITEMHEIGHT = 0x0153
CB_GETITEMHEIGHT = 0x0154
CB_SETEXTENDEDUI = 0x0155
CB_GETEXTENDEDUI = 0x0156
CB_GETDROPPEDSTATE = 0x0157
CB_FINDSTRINGEXACT = 0x0158
CB_SETLOCALE = 0x0159
CB_GETLOCALE = 0x015A
CB_GETTOPINDEX = 0x015b
CB_SETTOPINDEX = 0x015c
CB_GETHORIZONTALEXTENT = 0x015d
CB_SETHORIZONTALEXTENT = 0x015e
CB_GETDROPPEDWIDTH = 0x015f
CB_SETDROPPEDWIDTH = 0x0160
CB_INITSTORAGE = 0x0161
CB_GETCOMBOBOXINFO = 0x0162
CB_MSGMAX = 0x0163
CB_MSGMAX = 0x015B

LVCFMT_LEFT = 0x0000

LVCFMT_RIGHT = 0x0001

LVCFMT_CENTER = 0x0002

LVS_SINGLESEL = 0x0004
LVM_DELETEITEM = (LVM_FIRST + 8)
LVM_ENSUREVISIBLE = (LVM_FIRST + 19)
LVN_ITEMACTIVATE = LVN_FIRST - 14

TVGN_PARENT = 0x3
TVGN_PREVIOUS = 0x2

TBS_HORZ = 0x0
TBS_VERT = 0x2

COMCTL32_VERSION = 0x020c
CCM_FIRST = 0x2000
CCM_SETVERSION = CCM_FIRST+0x7
CCM_GETVERSION = CCM_FIRST+0x8
TCS_BOTTOM = 0x2 


UDS_SETBUDDYINT = 2
UDM_SETBUDDY = WM_USER + 105
UDM_GETBUDDY = WM_USER + 106
UDM_SETRANGE32 = WM_USER + 111
UDM_GETRANGE32 = WM_USER + 112
UDM_SETPOS32 = WM_USER + 113
UDM_GETPOS32 = WM_USER + 114

UDN_DELTAPOS = 4294966574
