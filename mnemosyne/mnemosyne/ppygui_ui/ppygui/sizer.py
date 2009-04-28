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
from config import HIRES

__all__ = ['Sizer', 'HSizer', 'VSizer']

class BlankBox:
  '''
  An empty space that you can 
  put in a BoxSizer
  '''
  def size(self, l, t, r, b):
    pass
    
class Box:
    '''
    A box that holds a window.
    It should not be used directly, but it is used 
    when you pass a window to the append 
    method of a BoxSizer.
    '''
    def __init__(self, window, border):
        self.window = window 
        self.border = border
        assert len(border) == 4
    
    def size(self, l, t, r, b):
        l += self.border[0]
        t += self.border[1]
        r -= self.border[2]
        b -= self.border[3]
        w = r-l
        h = b-t
        self.window.move(l, t, w, h)
    
    def get_best_size(self):
        return self.window.get_best_size()
  
class Sizer:
  
  '''
  The base class of the layout system.
  You can append a Window, blank space or another Sizer with a given proportion 
  or a fixed dimension.
  '''
  
  def __init__(self, orientation, border=(0, 0, 0, 0), spacing=0):
    
    '''
    Arguments:
        - orientation: must be 'vertical' or 'horizontal'
        - border: a 4 elements tuple (left, top, bottom, right)
        - spacing: the space in pixels between elements
    '''
    
    self.boxes = []
    self.totalcoeff = 0
    self.totalfixedsize = 0
    if HIRES :
      border = tuple(2*val for val in border)
    self.border = border
    
    assert orientation in ['horizontal', 'vertical']
    self.orientation = orientation
    self.spacing = spacing
    
  def add(self, box, coeff=1, border=(0, 0, 0, 0)):
    '''
    Appends a Window or another Sizer to the Sizer. 
    Arguments:
        - box: the element to add, it must be an instance of Window or Sizer.
        - coeff: represents the proportion of the sizer that will occupy the element.
        - border: a 4 elements tuple (left, top, bottom, right)
    ''' 
    
    if isinstance(box, Window):
      if HIRES :
        border = tuple(2*val for val in border)
      data = [Box(box, border), coeff]
    elif isinstance(box, (BlankBox, Sizer)):
      data = [box, coeff]
    else :
      raise TypeError("arg 1 must be an instance of Window, BlankBox or BoxSizer")
    
    
    if coeff == 0:
        b_x, b_y = box.get_best_size()
        if self.orientation == 'vertical':
            if not b_y:
                return self.add(box, 1, border)
            else:
                return self.addf(box, b_y, border)
        elif self.orientation == 'horizontal':
            if not b_x:
                return self.add(box, 1, border)
            else:
                return self.addf(box, b_x, border)
                
            
    elif coeff > 0 :
      self.totalcoeff += coeff
    else :
      if HIRES:
        coeff *= 2
        data[1] = coeff
      self.totalfixedsize -= coeff
      
    if self.boxes and self.spacing:
        space = self.spacing
        if HIRES:
            space *= 2
        self.boxes.append((BlankBox(), -space))
        self.totalfixedsize += space
        
    self.boxes.append(data)
  
  def addspace(self, coeff=1, border=(0,0,0,0)):
    '''\
    Appends a blank space to the Sizer, 
    Arguments:
        - coeff: represents the proportion of the sizer that will occupy the space.
        - border: a 4 elements tuple (left, top, bottom, right)
    '''
    self.add(BlankBox(), coeff, border)
    
  def addfixed(self, box, dim=20, border=(0,0,0,0)):
    '''
    Appends a Window, another Sizer to the Sizer, 
    Arguments :
        - box: the element to add, it must be an instance of Window or Sizer.
        - dim: represents the size in pixel that will occupy the element.
        - border: a 4 elements tuple (left, top, bottom, right)
    ''' 
    self.add(box, -dim, border)
  
  addf = addfixed
    
  def addfixedspace(self, dim=20, border=(0,0,0,0)):
    '''\
    Appends a blank space to the Sizer, 
    Arguments:
        - dim: represents the size in pixel that will occupy the space.
        - border: a 4 elements tuple (left, top, bottom, right)
    '''
    self.addspace(-dim, border)
  
  addfspace = addfixedspace
  
  def size(self, l, t, r, b):
    
    l += self.border[0]
    t += self.border[1]
    r -= self.border[2]
    b -= self.border[3]
    sizerw = r - l
    sizerh = b - t
    hoffset = l
    voffset = t
    for data in self.boxes:
      box, coeff = data
      if self.orientation == 'vertical' :
        w = sizerw
        if coeff > 0 :
          h = (sizerh - self.totalfixedsize) * coeff / self.totalcoeff
        else : 
          h = -coeff
        box.size(hoffset, voffset, hoffset+w, voffset+h)
        voffset += h
      elif self.orientation == 'horizontal' :
        if coeff > 0 :
          w = (sizerw - self.totalfixedsize) * coeff / self.totalcoeff
        else :
          w = -coeff
        h = sizerh 
        box.size(hoffset, voffset, hoffset+w, voffset+h)
        hoffset += w

class HSizer(Sizer):
  
    def __init__(self, border=(0, 0, 0, 0), spacing=0):
        Sizer.__init__(self, 'horizontal', border, spacing)
        
    def get_best_size(self):
        h_expand = False
        v_expand = False
        
        b_x = 0
        b_y = 0
        for box, coeff in self.boxes:
            cx, cy =  box.get_best_size()
            if cx is None:
                h_expand = True
            else:
                b_x += cx
            if cy is None:
                v_expand = True
            else:
                if cy > b_y:
                    b_y = cy
                    
        if h_expand:
            b_x = None
        if v_expand:
            b_y = None  
        return b_x, b_y
            
class VSizer(Sizer):
  
    def __init__(self, border=(0, 0, 0, 0), spacing=0):
        Sizer.__init__(self, 'vertical', border, spacing)
  
    def get_best_size(self):
        h_expand = False
        v_expand = False
        
        b_x = 0
        b_y = 0
        for box, coeff in self.boxes:
            
            cx, cy =  box.get_best_size()
            print cx, cy
            if cx is None:
                h_expand = True
            else:
                if cx > b_x:
                    b_x = cx
            if cy is None:
                v_expand = True
            else:
                b_y += cy
                    
        if h_expand:
            b_x = None
        if v_expand:
            b_y = None  
        return b_x, b_y