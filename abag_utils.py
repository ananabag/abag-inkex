#!/usr/bin/env python

import math

# These two lines are only needed if you don't put the script directly into
# the installation directory
# TODO fix these lines
import sys
sys.path.append('/usr/share/inkscape/extensions') #path to extensions
import inkex
from simplestyle import formatStyle

def format_number(n, accuracy=6):
    """Formats a number in a friendly manner
    (removes trailing zeros and unneccesary point."""

    fs = "%."+str(accuracy)+"f"
    str_n = fs%float(n)
    if '.' in str_n:
        str_n = str_n.rstrip('0').rstrip('.')
    if str_n == "-0":
        str_n = "0"
    #str_n = str_n.replace("-0", "0")
    return str_n
    
def circle(r, cx, cy, parent, style, start_end=(0,2*math.pi)):
    # add in an id variable to the attributs so I can pass it to the text 
    # to put it along the path
    if not style:
        style = {'stroke': '#000000', 'stroke-width': '0.5px', 'fill': 'none'}
        
    attribs = {'style': formatStyle(style),
        inkex.addNS('cx','sodipodi')        :str(cx),
        inkex.addNS('cy','sodipodi')        :str(cy),
        inkex.addNS('rx','sodipodi')        :str(r),
        inkex.addNS('ry','sodipodi')        :str(r),
        inkex.addNS('start','sodipodi')     :str(start_end[0]),
        inkex.addNS('end','sodipodi')       :str(start_end[1]),
        inkex.addNS('open','sodipodi')      :'True',    #all ellipse sectors we will draw are open
        inkex.addNS('type','sodipodi')      :'arc',
        'transform'                         :''}
    el = inkex.etree.SubElement(parent, inkex.addNS('path','svg'), ell_attribs)
    return el
    
def ellipse((rx, ry), (cx, cy), parent, style=False, start_end=(0,2*math.pi)):
    # add in an id variable to the attributs so I can pass it to the text 
    # to put it along the path
    if not style:
        style = {'stroke': '#ffffff', 'stroke-width': '0.5px', 'fill': 'none'}
        
    ell_attribs = {'style': formatStyle(style),
        inkex.addNS('cx','sodipodi')        :str(cx),
        inkex.addNS('cy','sodipodi')        :str(cy),
        inkex.addNS('rx','sodipodi')        :str(rx),
        inkex.addNS('ry','sodipodi')        :str(ry),
        inkex.addNS('start','sodipodi')     :str(start_end[0]),
        inkex.addNS('end','sodipodi')       :str(start_end[1]),
        inkex.addNS('open','sodipodi')      :'True',    #all ellipse sectors we will draw are open
        inkex.addNS('type','sodipodi')      :'arc',
        'transform'                         :''}
    ell = inkex.etree.SubElement(parent, inkex.addNS('path','svg'), ell_attribs )
    return ell
    
def ellipseId((rx, ry), (cx, cy), parent, ID, start_end=(0,2*math.pi), style=False):
    # add in an id variable to the attributs so I can pass it to the text 
    # to put it along the path
    if not style:
        style = {'stroke': '#ffffff', 'stroke-width': '0.5px', 'fill': 'none'}
        
    ell_attribs = {'style': formatStyle(style),
        'id'                                :str(ID),
        inkex.addNS('cx','sodipodi')        :str(cx),
        inkex.addNS('cy','sodipodi')        :str(cy),
        inkex.addNS('rx','sodipodi')        :str(rx),
        inkex.addNS('ry','sodipodi')        :str(ry),
        inkex.addNS('start','sodipodi')     :str(start_end[0]),
        inkex.addNS('end','sodipodi')       :str(start_end[1]),
        inkex.addNS('open','sodipodi')      :'True',    #all ellipse sectors we will draw are open
        inkex.addNS('type','sodipodi')      :'arc',
        'transform'                         :''}
    ell = inkex.etree.SubElement(parent, inkex.addNS('path','svg'), ell_attribs )
    return ell

#draw an SVG line segment between the given (raw) points
def line( (x1, y1), (x2, y2), name, parent, style):
    if not style:
        style = {'stroke': '#ffffff', 'stroke-width': '0.5px'}
        
    line_attribs = {'style' : formatStyle(style),
                    inkex.addNS('label','inkscape') : name,
                    'd' : 'M '+str(x1)+','+str(y1)+' L '+str(x2)+','+str(y2)}

    line = inkex.etree.SubElement(parent, inkex.addNS('path','svg'), line_attribs )

class Vector2(object):

    __slots__ = ('_v',)

    _gameobjects_vector = 2


    def __init__(self, x=0., y=0.):
        """Initialise a vector

        @type x: number
        @param x: The x value (defaults to 0.), or a container of 2 values
        @type x: number
        @param y: The y value (defaults to 0.)

        """
        if hasattr(x, "__getitem__"):
            x, y = x
            self._v = [float(x), float(y)]
        else:
            self._v = [float(x), float(y)]

    def _get_length(self):
        x, y = self._v
        return math.sqrt(x*x + y*y)
    def _set_length(self, length):
        v = self._v
        try:
            x, y = v
            l = length / math.sqrt(x*x +y*y)
        except ZeroDivisionError:
            v[0] = 0.0
            v[1] = 0.0
            return self
        v[0] *= l
        v[1] *= l
    length = property(_get_length, _set_length, None, "Length of the vector")


    @classmethod
    def from_floats(cls, x, y):
        vec = cls.__new__(cls, object)
        vec._v = [x, y]
        return vec


    @classmethod
    def from_iter(cls, iterable):
        """Creates a Vector2 object from an iterable.

        @param iterable: An iterable of at least 2 numeric values

        """
        next = iter(iterable).next
        vec = cls.__new__(cls, object)
        vec._v = [float(next()), float(next())]
        return vec


    @classmethod
    def from_points(cls, p1, p2):
        """Creates a Vector2 object between two points.
        @param p1: First point
        @param p2: Second point

        """
        v = cls.__new__(cls, object)
        x, y = p1
        xx, yy = p2
        v._v = [float(xx-x), float(yy-y)]
        return v

    @classmethod
    def _from_float_sequence(cls, sequence):
        v = cls.__new__(cls, object)
        v._v = list(sequence[:2])
        return v


    def copy(self):
        """Returns a copy of this object."""
        vec = self.__new__(self.__class__, object)
        vec._v = self._v[:]
        return vec

    def get_x(self):
        return self._v[0]
    def set_x(self, x):
        try:
            self._v[0] = 1.0 * x
        except:
            raise TypeError("Must be a number")
    x = property(get_x, set_x, None, "x component.")

    def get_y(self):
        return self._v[1]
    def set_y(self, y):
        try:
            self._v[1] = 1.0 * y
        except:
            raise TypeError("Must be a number")
    y = property(get_y, set_y, None, "y component.")

    #u = property(get_x, set_y, None, "u component (alias for x).")
    #v = property(get_y, set_y, None, "v component (alias for y).")

    def __str__(self):

        x, y = self._v
        return "(%s, %s)" % (format_number(x), format_number(y))

    def __repr__(self):

        x, y = self._v
        return "Vector2(%s, %s)" % (x, y)

    def __iter__(self):

        return iter(self._v[:])

    def __len__(self):

        return 2


    def __getitem__(self, index):
        """Gets a component as though the vector were a list."""
        try:
            return self._v[index]
        except IndexError:
            raise IndexError, "There are 2 values in this object, index should be 0 or 1"

    def __setitem__(self, index, value):
        """Sets a component as though the vector were a list."""

        try:
            self._v[index] = 1.0 * value
        except IndexError:
            raise IndexError, "There are 2 values in this object, index should be 0 or 1!"
        except TypeError:
            raise TypeError, "Must be a number"


    def __eq__(self, rhs):
        x, y = self._v
        xx, yy = rhs
        return x == xx and y == yy

    def __ne__(self, rhs):
        x, y = self._v
        xx, yy, = rhs
        return x != xx or y != yy

    def __hash__(self):

        return hash(self._v)

    def __add__(self, rhs):
        x, y = self._v
        xx, yy = rhs
        return Vector2.from_floats(x+xx, y+yy)


    def __iadd__(self, rhs):
        xx, yy = rhs
        v = self._v
        v[0] += xx
        v[1] += yy
        return self

    def __radd__(self, lhs):
        x, y = self._v
        xx, yy = lhs
        return self.from_floats(x+xx, y+yy)

    def __sub__(self, rhs):
        x, y = self._v
        xx, yy = rhs
        return Vector2.from_floats(x-xx, y-yy)

    def __rsub__(self, lhs):
        x, y = self._v
        xx, yy = lhs
        return self.from_floats(xx-x, yy-y)

    def _isub__(self, rhs):

        xx, yy = rhs
        v = self._v
        v[0] -= xx
        v[1] -= yy
        return self

    def __mul__(self, rhs):
        """Return the result of multiplying this vector with a scalar or a vector-list object."""
        x, y = self._v
        if hasattr(rhs, "__getitem__"):
            xx, yy = rhs
            return Vector2.from_floats(x*xx, y*yy)
        else:
            return Vector2.from_floats(x*rhs, y*rhs)

    def __imul__(self, rhs):
        """Multiplys this vector with a scalar or a vector-list object."""
        if hasattr(rhs, "__getitem__"):
            xx, yy = rhs
            v = self._v
            v[0] *= xx
            v[1] *= yy
        else:
            v = self._v
            v[0] *= rhs
            v[1] *= rhs
        return self

    def __rmul__(self, lhs):

        x, y = self._v
        if hasattr(lhs, "__getitem__"):
            xx, yy = lhs
        else:
            xx = lhs
            yy = lhs
        return self.from_floats(x*xx, y*yy)

    def __div__(self, rhs):
        """Return the result of dividing this vector by a scalar or a vector-list object."""
        x, y = self._v
        if hasattr(rhs, "__getitem__"):
            xx, yy, = rhs
            return Vector2.from_floats(x/xx, y/yy)
        else:
            return Vector2.from_floats(x/rhs, y/rhs)


    def __idiv__(self, rhs):
        """Divides this vector with a scalar or a vector-list object."""
        if hasattr(rhs, "__getitem__"):
            xx, yy = rhs
            v = self._v
            v[0] /= xx
            v[1] /= yy
        else:
            v = self._v
            v[0] /= rhs
            v[1] /= rhs
        return self

    def __rdiv__(self, lhs):

        x, y = self._v
        if hasattr(lhs, "__getitem__"):
            xx, yy = lhs
        else:
            xx = lhs
            yy = lhs
        return self.from_floats(xx/x, yy/x)

    def __neg__(self):
        """Return the negation of this vector."""
        x, y = self._v
        return Vector2.from_floats(-x, -y)

    def __pos__(self):

        return self.copy()

    def __nonzero__(self):

        x, y = self._v
        return bool(x or y)

    def __call__(self, keys):

        """Used to swizzle a vector.

        @type keys: string
        @param keys: A string containing a list of component names
        >>> vec = Vector(1, 2)
        >>> vec('yx')
        (1, 2)

        """

        ord_x = ord('x')
        v = self._v
        return tuple( v[ord(c) - ord_x] for c in keys )


    def as_tuple(self):
        """Converts this vector to a tuple.

        @rtype: Tuple
        @return: Tuple containing the vector components
        """
        return tuple(self._v)


    def get_length(self):
        """Returns the length of this vector."""
        x, y = self._v
        return math.sqrt(x*x + y*y)
    get_magnitude = get_length


    def normalise(self):
        """Normalises this vector."""
        v = self._v
        x, y = v
        l = math.sqrt(x*x +y*y)
        try:
            v[0] /= l
            v[1] /= l
        except ZeroDivisionError:
            v[0] = 0.
            v[1] = 0.
        return self
    normalize = normalise

    def perpendicular(self):
        """Compute the perpendicular."""
        x, y = self._v
        return Vector2(-y, x)
    
    def set_length(self, length):
        """Sets the magnitude for the vector."""
        angle = self.get_angle()
        x = length * math.cos(angle)
        y = length * math.sin(angle)
        self.set_x(x)
        self.set_y(y)      
        
    set_magnitude = set_length
    
    def get_angle(self, degrees = False):
        """Get the angle made agains the x axis"""
        x, y = self._v
        if degrees:
            return math.degrees(math.atan2(y,x))
        else:
            return math.atan2(y, x)

    def get_normalised(self):
        x, y = self._v
        l = math.sqrt(x*x +y*y)
        return Vector2.from_floats(x/l, y/l)
    get_normalized = get_normalised

    def get_distance_to(self, p):
        """Returns the distance to a point.

        @param: A Vector2 or list-like object with at least 2 values.
        @return: distance
        """
        x, y = self._v
        xx, yy = p
        dx = xx-x
        dy = yy-y
        return math.sqrt( dx*dx + dy*dy )

class Path(object):
    """SVG path class"""

    __slots__ = ('_d',)

    def __init__(self):
        pass
        
    def moveTo(self):
        pass
        
    def absMoveTo(self):
        pass
        
    def get_path_array(self):
        return this._d


class Piece(object):
    """
    Base class for all pattern pieces
    """

    def __init__(self, label = '', name = ''):
        self.label = label
        self.name = name
        self.seams = False
        
        self._seams = self.seams
        self._d = Path()
        

class RectanglePiece(Piece):
    """
    The RectanglePiece class. The main aim of this class is to make drawing and 
    rendering svg rectangles easy
    """
    def __init__(self, width, height, label = '', name = ''):
        Piece.__init__(self, label, name)
        self.width = width
        self.height = height
        self.start_loc = (0,0)
        
        # set the path data
        self.path_data = ((self.width, 0.0),
                        (0.0, self.height),
                        (-self.width, 0.0),
                        (0.0, -self.height))
        
    def get_svgd(self):
        """
        @return Tuple Returns a Tuple suitable for use in an SVG 'd' path string
        """
        d = "m%f, %f " % self.start_loc
        for i in self.path_data:
            d += "%f, %f " % i
        d += "z"
        return d
       
    def get_seams_svgd(self):
        """
        @return String Returns a string suitable for use as an SVG 'd' path
        but with adjustments for seams
        """
        if not self.seams:
            raise RuntimeError('Seams are not set yet')
        
        new_width = self.width + self.right + self.left
        new_height = self.height + self.top + self.bottom
        seam_data = ((new_width, 0.0),
                (0.0, new_height),
                (-new_width, 0.0),
                (0.0, -new_height))
        d = "m%f, %f " % (self.start_loc[0] - self.left, self.start_loc[1] - self.top)
        for i in seam_data:
            d += "%f, %f " % i
        d += "z"
        return d
    
    def get_all_svgd(self):
        if self.seams:
            return (self.get_svgd(), self.get_seams_svgd())
        else:
            return (self.get_svgd())
        
    def get_seam_offset(self, sx, sy):
        return (sx - self.left, sy - self.top)
        
    def scale(self, x, y = False):
        """
        Scale the dimensions by the factor
        """
        if y is False:
            y = x
        self.width *= x
        self.height *= y        
    
    def set_seams(self, top, right = 0, bottom = 0, left = 0):
        self.seams = True
        self.top = top
        self.bottom = bottom
        self.right = right
        self.left = left
    
    def set_all_seams(self, value):
        self.seams = True
        self.top, self.right, self.bottom, self.left = value, value, value, value
    
    def get_width(self):
        return self.width
    
    def set_width(self, w):
        self.width = w
        
    def get_height(self):
        return self.height
    
    def set_height(self, h):
        self.height = h
        
    def get_start_loc(self):
        return self.start_loc
    
    def set_start_loc(self, x, y):
        self.start_loc = (x, y)


class Dome(object):
    """
    Class to hold all segments and the information to generate the dome
    """
    def __init__(self, radius, segments, innerSeam, outerSeam, endSeam):
        self.r = radius
        self.segs = segments
        self.inseam = innerSeam
        self.outseam = outerSeam
        self.endseam = endSeam
        self.segment = {}

class DomeSegment(object):     
    """
    Class to hold all information needed to draw a dome segment. Including a few
    helper methods to render seam allowences and stuff
    """
    def __init__(self, segNumber, angle, segRadius, thickness):
        self.segNumber = segNumber
        self.angle = angle
        # this is for the outer radius
        self.radiusOuter = segRadius
        self.thickness = thickness
        
        # set some of the other variables for calculation
        self.radiusInner = segRadius - thickness
        self.angleD = math.degrees(angle)
        self.pcx = 0
        self.pcy = 0
        
    @staticmethod
    def point_on_circle(radius, angle):
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        return (x, y)
        
    def __get_cap(self, angle):
        return self.__get_raw_cap(angle, self.radiusInner, self.radiusOuter)
    
    def __get_raw_cap(self, angle, rin, rout):
        x1, y1 = self.point_on_circle(rin, angle)
        x1 = self.pcx + x1
        y1 = self.pcy + y1        
        x2, y2 = self.point_on_circle(rout, angle)
        x2 = self.pcx + x2
        y2 = self.pcy + y2
        return ((x1, y1), (x2, y2))
        
    def get_inner_arch(self):
        return (self.radiusInner, 0, self.angle)
        
    def get_outer_arch(self):
        return (self.radiusOuter, 0, self.angle)
    
    def get_text_arch(self):
        radius = self.radiusOuter - (self.thickness / 3)
        return (radius, 0, self.angle)

    def get_inner_seam_arch(self):
        radius = self.radiusInner - self.inseam
        return (radius, 0, self.angle)

    def get_outer_seam_arch(self):
        radius = self.radiusOuter + self.outseam
        return (radius, 0, self.angle)
    
    def get_end_seam_cap(self):
        # get the full end cap
        rin = self.radiusInner - self.inseam
        rout = self.radiusOuter + self.outseam
        p1, p2 = self.__get_raw_cap(self.angle, rin, rout)

        # create a vecotr from points
        v = Vector2.from_points(p1, p2)
        # get perpendicular from is
        perp = v.perpendicular()
        perp.set_length(self.endseam)
        px = perp.get_x()
        py = perp.get_y()
        
        # get extra points
        p3 = (p1[0] + px, p1[1] + py)
        p4 = (p2[0] + px, p2[1] + py)
        
        # create the d path
        svgd = 'M%.8f, %.8f' % p2
        svgd += 'L%.8f, %.8f' % p4
        svgd += 'L%.8f, %.8f' % p3
        svgd += 'L%.8f, %.8f' % p1
  
        return svgd
    
    def get_start_seam_cap(self):
        # get the full end cap
        rin = self.radiusInner - self.inseam
        rout = self.radiusOuter + self.outseam        
        p1, p2 = self.__get_raw_cap(0, rin, rout)

        # create a vecotr from points
        v = Vector2.from_points(p1, p2)
        # get perpendicular from is
        perp = v.perpendicular()
        perp.set_length(self.endseam)
        px = perp.get_x()
        py = perp.get_y()
        
        # get extra points
        p3 = (p1[0] - px, p1[1] - py)
        p4 = (p2[0] - px, p2[1] - py)
        
        # create the d path
        svgd = 'M%.8f, %.8f' % p2
        svgd += 'L%.8f, %.8f' % p4
        svgd += 'L%.8f, %.8f' % p3
        svgd += 'L%.8f, %.8f' % p1
  
        return svgd

    def get_start_cap(self):
        return self.__get_cap(0)
        
    def get_end_cap(self):
        return self.__get_cap(self.angle)
    
    def set_all_seams(self, inner, outer, end):
        self.inseam = inner
        self.outseam = outer
        self.endseam = end
        
    def set_inner_seam(self, s):
        self.inseam = s
    
    def set_outer_seam(self, s):
        self.outseam = s
        
    def set_end_seam(self, s):
        self.endseam = s
        
    def setPageCenter(self, x, y):
        self.pcx = x
        self.pcy = y


