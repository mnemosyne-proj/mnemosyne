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


from ctypes import cdll

GetSystemMetrics = cdll.coredll.GetSystemMetrics
SM_CXSCREEN = 0
SM_CYSCREEN = 1

def get_resolution():
    rx = GetSystemMetrics(SM_CXSCREEN)
    ry = GetSystemMetrics(SM_CYSCREEN)
    if ry > rx:
        return rx, ry
    return ry, rx
    
rx, ry = get_resolution()

if rx>320 and ry>240:
    HIRES = True
    HIRES_MULT = 2
else:
    HIRES = False
    HIRES_MULT = 1