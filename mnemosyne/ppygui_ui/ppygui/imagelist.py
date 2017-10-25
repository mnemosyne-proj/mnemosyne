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


from os.path import abspath
from ppygui.core import *
from ppygui.w32comctl import *

SHLoadDIBitmap = windll.coredll.SHLoadDIBitmap
SHLoadDIBitmap.argtypes = [LPWSTR]

class ImageList(GuiObject):
    def __init__(self, width, height, flags=1):
        self._hImageList = ImageList_Create(width, height, flags, 0, 1)
        
    def add(self, image, colormask=(255,255,255)):
        # WM >= 5.0 only
        # Pocket PC 2003 ImageList_Add function
        # handles DDB only.
        hbmp = SHLoadDIBitmap(abspath(image))
        crmask = rgb(*colormask)
        ImageList_AddMasked(self._hImageList, hbmp, UINT(crmask))
        DeleteObject(hbmp)
        
    def add_from_resource(self, resource_dll, icons, cx, cy, flags=0):
        LoadLibrary(str(resource_dll))
        hdll = GetModuleHandle(str(resource_dll))
        for i in icons:
            hIcon = LoadImage(hdll, i, IMAGE_ICON, cx, cy, flags)
            ImageList_AddIcon(self._hImageList, hIcon)
            
            
    def __del__(self):
        ImageList_Destroy(self._hImageList)    

def list_icons(dll):
    LoadLibrary(str(dll))
    hdll = GetModuleHandle(str(dll))
    for i in range(500):
        try:
            hIcon = LoadImage(hdll, i, IMAGE_ICON, 32, 32, 0)
            print(i)
        except:
            pass
