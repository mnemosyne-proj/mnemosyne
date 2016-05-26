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

from .config import HIRES, HIRES_MULT

class _Wrapper:
    def __init__(self, wrapped, border):
 
        self.wrapped = wrapped
        if HIRES :
            border = tuple(2*val for val in border)
        self.border = border
        
    def size(self, l, t, r, b):
        border = self.border
        
        l += border[0]
        t += border[1]
        r -= border[2]
        b -= border[3]
        w = r-l
        h = b-t
        self.wrapped.move(l, t, w, h)
        
    def get_best_size(self):
        bx, by = self.wrapped.get_best_size()
        if bx is not None:
            if HIRES:
                bx += (self.border[0]+self.border[2])/2
            else:
                bx += self.border[0]+self.border[2]
        if by is not None:
            if HIRES:
                by += (self.border[1]+self.border[3])/2
            else:
                by += self.border[1]+self.border[3]
        return bx, by
        
class _Box:
    def __init__(self, border=(0,0,0,0), spacing=0):
        self._childs = []
        if HIRES :
            border = tuple(2*val for val in border)
            spacing *= 2
            
        self.border = border
        self.spacing = spacing
    
    def add(self, child, coeff=0, border=(0, 0, 0, 0)): 
        self._childs.append((_Wrapper(child, border), coeff))
        
    def addfixed(self, child, dim, border=(0,0,0,0)):
        self._childs.append((_Wrapper(child, border), -dim))
        
    def move(self, l, t, w, h):
        self.size(l, t, l+w, t+h)
        
class HBox(_Box):
    
    def size(self, l, t, r, b):
        fixed_size = 0
        total_coeff= 0
        childs = []
        for child, coeff in self._childs:
            bx, by = child.get_best_size()
            if HIRES:
                if bx is not None:
                    bx *= 2
                if by is not None:
                    by *= 2
                    
            if coeff == 0:
                if bx is None:
                    total_coeff += 1
                    childs.append((child, 1, 1, by))
                    continue
                
                fixed_size += bx
                childs.append((child, bx, 0, by))
            elif coeff >0:
                total_coeff += coeff
                childs.append((child, coeff, 1, by))
            else:
                if HIRES:
                    coeff *= 2
                fixed_size -= coeff
                childs.append((child, -coeff, 0, by))
        border = self.border    
        
        l += border[0]
        t += border[1]
        r -= border[2]
        b -= border[3]
        sizerw = r - l
        sizerh = b - t
        hoffset = l
        voffset = t
        fixed_size += self.spacing * (len(childs)-1)
         
        first = True
        for child, coeff, expand, by in childs:
            if not first:
                hoffset += self.spacing
            if expand :
                w = (sizerw - fixed_size) * coeff / total_coeff
            else :
                w = coeff
#            if by is None:
            h = sizerh
            dy = 0
#            else:
#                h = by
#                dy = (sizerh - by) / 2
                
            child.size(hoffset, voffset+dy, hoffset+w, voffset+dy+h)
            hoffset += w
            first = False
        
    def get_best_size(self):
        b_x = 0
        b_y = 0
        h_expand = False
        v_expand = False
        for child, coeff in self._childs:
            if h_expand and v_expand:
                break
                
            if coeff:
                h_expand = True
                
            cx, cy =  child.get_best_size()
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
        else:
            b_x += (self.border[0]+self.border[2])/HIRES_MULT
        if v_expand:
            b_y = None 
        else:
            b_y += (self.border[1]+self.border[3])/HIRES_MULT
        return b_x, b_y
        
class VBox(_Box):
    
    def size(self, l, t, r, b):
        fixed_size = 0
        total_coeff= 0
        childs = []
        for child, coeff in self._childs:
            if coeff==0:
                by = child.get_best_size()[1]
                if by is None:
                    total_coeff += 1
                    childs.append((child, 1, 1))
                    continue
                if HIRES:
                    by *= 2
                fixed_size += by
                childs.append((child, by, 0))
            elif coeff > 0:
                total_coeff += coeff
                childs.append((child, coeff, 1))
            else:
                if HIRES:
                    coeff *= 2
                fixed_size -= coeff
                childs.append((child, -coeff, 0))
        
        border = self.border    
           
        l += border[0]
        t += border[1]
        r -= border[2]
        b -= border[3]
        sizerw = r - l
        sizerh = b - t
        hoffset = l
        voffset = t
        fixed_size += self.spacing * (len(childs)-1)
        
        first = True
        for child, coeff, expand in childs:
            if not first:
                voffset += self.spacing
            w = sizerw
            if expand > 0 :
                h = (sizerh - fixed_size) * coeff / total_coeff
            else : 
                h = coeff
            child.size(hoffset, voffset, hoffset+w, voffset+h)
            voffset += h
            first = False
            
    def get_best_size(self):
        b_x = 0
        b_y = 0
        h_expand = False
        v_expand = False
        for child, coeff in self._childs:
            if h_expand and v_expand:
                break
                
            if coeff:
                v_expand = True
                
            cx, cy =  child.get_best_size()
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
        else:
            b_x += (self.border[0]+self.border[2])/HIRES_MULT
        if v_expand:
            b_y = None 
        else:
            b_y += (self.border[1]+self.border[3])/HIRES_MULT
        return b_x, b_y
        
class TBox:
    def __init__(self, rows, cols, border=(0,0,0,0),
                 spacing_x=0, spacing_y=0,
                 rows_expanded=[], cols_expanded=[]):
        self._rows = rows
        self._cols = cols
        self._childs = []
        self.border = border
        self._spacing_x = spacing_x# * HIRES_MULT
        self._spacing_y = spacing_y# * HIRES_MULT
        self.rows_expanded = set(rows_expanded)
        self.cols_expanded = set(cols_expanded)
        
    def add(self, child, border=(0,0,0,0)):
        self._childs.append(_Wrapper(child, border))
        
    def get_best_size(self):
        rows_widths = [0]*self._rows
        cols_widths = [0]*self._cols
        expand_x = bool(self.cols_expanded)
        expand_y = bool(self.rows_expanded)
        
        for n, child in enumerate(self._childs):
            i, j = n%self._cols, n/self._cols
            
            b_x, b_y = child.get_best_size()
            
            if expand_x:
                pass
            elif b_x is not None:
                if b_x > cols_widths[i]:
                    cols_widths[i] = b_x
            else: 
                expand_x = True
            
            if expand_y:
                pass
            elif b_y is not None:
                if b_y > rows_widths[j]:
                    rows_widths[j] = b_y 
            else:
                expand_y = True    
        if expand_x:
            b_x = None
        else:
            b_x = sum(cols_widths)# * HIRES_MULT
            b_x += self._spacing_x * (self._cols-1)
            b_x += self.border[0]+self.border[2]
        if expand_y:
            b_y = None
        else:
            b_y = sum(rows_widths)# * HIRES_MULT
            b_y += self._spacing_y * (self._rows-1)
            b_y += self.border[1]+self.border[3]
        return b_x, b_y
        
    def size(self, l, t, r, b):
#        rows_widths = [0]*self._rows
#        cols_widths = [0]*self._cols
        rows_expanded = self.rows_expanded  #set()
        cols_expanded = self.cols_expanded#set()
        rows_widths = [None if (i in rows_expanded) else 0 for i in range(self._rows)]
        cols_widths = [None if (i in cols_expanded) else 0 for i in range(self._cols)]
        for n, child in enumerate(self._childs):
            i, j = n%self._cols, n/self._cols
            b_x, b_y = child.get_best_size()
            
            if cols_widths[i] is None:
                pass
#            if i in cols_expanded:
#                cols_widths[i] = None
            elif b_x is None:
                cols_expanded.add(i)
                cols_widths[i] = None
            elif cols_widths[i] < b_x * HIRES_MULT:
                cols_widths[i] = b_x * HIRES_MULT
            
            if rows_widths[j] is None:
                pass    
#            if j in rows_expanded:
#                pass
            if b_y is None:
                rows_expanded.add(j)
                rows_widths[j] = None
            elif rows_widths[j] < b_y * HIRES_MULT:
                rows_widths[j] = b_y * HIRES_MULT
        
        r_fixed_size = sum(width for width in rows_widths if width is not None)
        c_fixed_size = sum(width for width in cols_widths if width is not None)
        r_fixed_size += self._spacing_y * (self._rows-1) * HIRES_MULT
        c_fixed_size += self._spacing_x * (self._cols-1) * HIRES_MULT
        
        border = self.border    
        if HIRES :
            border = tuple(2*val for val in border)
                
        l += border[0]
        t += border[1]
        r -= border[2]
        b -= border[3]
        
        n_rows_expanded = len(rows_expanded)
        n_cols_expanded = len(cols_expanded)
        if n_rows_expanded:
            h_rows_ex = (b-t-r_fixed_size)/n_rows_expanded 
        if n_cols_expanded:
            w_cols_ex = (r-l-c_fixed_size)/n_cols_expanded
        hoffset = l
        voffset = t
        first_child = True
        for n, child in enumerate(self._childs):
            i, j = n%self._cols, n/self._cols
            
            if not first_child:
                if i == 0:
                    hoffset = l
                    voffset += rows_widths[j-1]
                    voffset += self._spacing_y * HIRES_MULT   
            if i in cols_expanded:
                col_width = w_cols_ex
            else:
                col_width = cols_widths[i]
            if j in rows_expanded:
                row_width = h_rows_ex
            else:
                row_width = rows_widths[j]
            
            child.size(hoffset, voffset, hoffset+col_width, voffset+row_width)  
            hoffset += col_width + self._spacing_x * HIRES_MULT
            first_child = False
            
    def move(self, l, t, w, h):
        self.size(l, t, l+w, t+h)
        
class Spacer:
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y
        
    def move(self, l, t, w, h):
        pass
        
    def get_best_size(self):
        return self.x, self.y