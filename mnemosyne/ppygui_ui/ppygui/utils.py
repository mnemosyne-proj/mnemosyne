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
import sys

if sys.version_info[0:2] == (2, 4):
    pythonDll = cdll.python24
elif sys.version_info[0:2] == (2, 5):
    pythonDll = cdll.python25
    
def _as_pointer(obj):
    "Increment the refcount of obj, and return a pointer to it"
    ptr = pythonDll.Py_BuildValue("O", id(obj))
    assert ptr == id(obj)
    return ptr

def _from_pointer(ptr):
    if ptr != 0 :
        "Convert a pointer to a Python object, and decrement the refcount of the ptr"
        l = [None]
        # PyList_SetItem consumes a refcount of its 3. argument
        pythonDll.PyList_SetItem(id(l), 0, ptr)
        return l[0]
    else :
        raise ValueError