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
from ctypes import *

LPOFNHOOKPROC = c_voidp #TODO

class OPENFILENAME(Structure):
    _keys_ = [("lStructSize", DWORD),
                ("hwndOwner", HWND),
                ("hInstance", HINSTANCE),
                ("lpstrFilter", LPCTSTR),
                ("lpstrCustomFilter", LPTSTR),
                ("nMaxCustFilter", DWORD),
                ("nFilterIndex", DWORD),
                ("lpstrFile", LPTSTR),
                ("nMaxFile", DWORD),
                ("lpstrFileTitle", LPTSTR),
                ("nMaxFileTitle", DWORD),
                ("lpstrInitialDir", LPCTSTR),
                ("lpstrTitle", LPCTSTR),
                ("Flags", DWORD),
                ("nFileOffset", WORD),
                ("nFileExtension", WORD),
                ("lpstrDefExt", LPCTSTR),
                ("lCustData", LPARAM),
                ("lpfnHook", LPOFNHOOKPROC),
                ("lpTemplateName", LPCTSTR),
                ]

try:
    # Detect if tGetFile.dll is present
    tGetFile = cdll.tgetfile.tGetFile
    def GetOpenFileName(ofn):
        tGetFile(True, ofn)
    def GetSaveFileName(ofn):
        tGetFile(False, ofn)
except:
    # Else use standard wince function
    GetOpenFileName = windll.coredll.GetOpenFileNameW
    GetSaveFileName = windll.coredll.GetSaveFileNameW

OFN_ALLOWMULTISELECT = 512
OFN_CREATEPROMPT= 0x2000
OFN_ENABLEHOOK =32
OFN_ENABLETEMPLATE= 64
OFN_ENABLETEMPLATEHANDLE= 128
OFN_EXPLORER= 0x80000
OFN_EXTENSIONDIFFERENT= 0x400
OFN_FILEMUSTEXIST =0x1000
OFN_HIDEREADONLY= 4
OFN_LONGNAMES =0x200000
OFN_NOCHANGEDIR= 8
OFN_NODEREFERENCELINKS= 0x100000
OFN_NOLONGNAMES= 0x40000
OFN_NONETWORKBUTTON =0x20000
OFN_NOREADONLYRETURN= 0x8000
OFN_NOTESTFILECREATE= 0x10000
OFN_NOVALIDATE= 256
OFN_OVERWRITEPROMPT= 2
OFN_PATHMUSTEXIST= 0x800
OFN_READONLY= 1
OFN_SHAREAWARE= 0x4000
OFN_SHOWHELP= 16
OFN_SHAREFALLTHROUGH= 2
OFN_SHARENOWARN= 1
OFN_SHAREWARN= 0
OFN_NODEREFERENCELINKS = 0x100000
OFN_PROJECT = 0x400000
OPENFILENAME_SIZE_VERSION_400 = 76

class FileDialog(object):
    
    @classmethod
    def _do_modal(cls, parent, title, wildcards, filename, f, folder=False):
        szPath = u'\0' * 1024
        if parent is None :
            hparent = 0
        else :
            hparent = parent._w32_hWnd
            
        filter = "".join("%s|%s|" %item for item in wildcards.items())
        filter = filter.replace('|', '\0') + '\0\0'

        ofn = OPENFILENAME()
        if folder:
            ofn.Flags = OFN_PROJECT
        if versionInfo.isMajorMinor(4, 0): #fix for NT4.0
            ofn.lStructSize = OPENFILENAME_SIZE_VERSION_400
        else:
            ofn.lStructSize = sizeof(OPENFILENAME)
        #ofn.lpstrFile = szPath
        filename = unicode(filename)
        filename += u"\0"*(1024-len(filename))
        ofn.lpstrFile = filename
        #ofn.lpstrFileTitle = unicode(filename)
        #ofn.nMaxFileTitle = 1024
        ofn.nMaxFile = 1024
        ofn.hwndOwner = hparent
        ofn.lpstrTitle = unicode(title)
        ofn.lpstrFilter = filter
    
        try:
            #the windows file dialogs change the current working dir of the app
            #if the user selects a file from a different dir
            #this prevents that from happening (it causes al sorts of problems with
            #hardcoded relative paths)
            import os
            cwd = os.getcwd()
            if f(byref(ofn))!= 0:
                return filename[:filename.find('\0')].strip()
            else:
                return None
        finally:
            os.chdir(cwd) 
            
    @classmethod
    def open(cls, title="Open", filename="", wildcards={"All (*.*)":"*.*"}, parent=None):
        return cls._do_modal(parent, title, wildcards, filename, GetOpenFileName)
    
    @classmethod
    def openfolder(cls, title="Open", filename="", wildcards={"All (*.*)":"*.*"}, parent=None):
        return cls._do_modal(parent, title, wildcards, filename, GetOpenFileName, folder=True)
         
            
    @classmethod    
    def save(cls, title="Save", filename="", wildcards={"All (*.*)":"*.*"}, parent=None):
        return cls._do_modal(parent, title, wildcards, filename, GetSaveFileName)
