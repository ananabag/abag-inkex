#!/usr/bin/env python
"""
abag_utils.py
A helper module for abag-inkex extensions
Copyright (C) 2014 Samuel Hodges <octerman@gmail.com>

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import inkex
import math
from math import pi, cos, sin
from random import randint
from simplestyle import formatStyle

DEFAULT_STYLE = {
    'stroke': '#ffffff',
    'stroke-width': '0.5px',
    'fill': 'none'
}


def point_on_circle(radius, angle):
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    return (x, y)


def format_number(n, accuracy=6):
    """Formats a number in a friendly manner
    (removes trailing zeros and unneccesary point."""

    fs = "%." + str(accuracy) + "f"
    str_n = fs % float(n)
    if '.' in str_n:
        str_n = str_n.rstrip('0').rstrip('.')
    if str_n == "-0":
        str_n = "0"
    #str_n = str_n.replace("-0", "0")
    return str_n


def circle(r, cx, cy, parent, style, start_end=(0, 2 * math.pi)):
    # add in an id variable to the attributs so I can pass it to the text
    # to put it along the path
    if not style:
        style = DEFAULT_STYLE

    attrs = {
        'style': formatStyle(style),
        inkex.addNS('cx', 'sodipodi'): str(cx),
        inkex.addNS('cy', 'sodipodi'): str(cy),
        inkex.addNS('rx', 'sodipodi'): str(r),
        inkex.addNS('ry', 'sodipodi'): str(r),
        inkex.addNS('start', 'sodipodi'): str(start_end[0]),
        inkex.addNS('end', 'sodipodi'): str(start_end[1]),
        # Ellipse extors will be drawn open
        inkex.addNS('open', 'sodipodi'): 'True',
        inkex.addNS('type', 'sodipodi'): 'arc',
        'transform': ''
    }
    return inkex.etree.SubElement(parent, inkex.addNS('path', 'svg'), attrs)


def ellipse((rx, ry), (cx, cy), parent, style=False, startEnd=(0, 2 * math.pi)):
    # add in an id variable to the attributs so I can pass it to the text
    # to put it along the path
    if not style:
        style = DEFAULT_STYLE

    attrs = {
        'style': formatStyle(style),
        inkex.addNS('cx', 'sodipodi'): str(cx),
        inkex.addNS('cy', 'sodipodi'): str(cy),
        inkex.addNS('rx', 'sodipodi'): str(rx),
        inkex.addNS('ry', 'sodipodi'): str(ry),
        inkex.addNS('start', 'sodipodi'): str(startEnd[0]),
        inkex.addNS('end', 'sodipodi'): str(startEnd[1]),
        # Ellipse sectors drawn open
        inkex.addNS('open', 'sodipodi'): 'True',
        inkex.addNS('type', 'sodipodi'): 'arc',
        'transform': ''
    }
    return inkex.etree.SubElement(parent, inkex.addNS('path', 'svg'), attrs)


def ellipse_id((rx, ry), (cx, cy), parent, nid, startEnd=(0, 2 * math.pi),
                                                                style=False):
    # add in an id variable to the attributs so I can pass it to the text
    # to put it along the path
    if not style:
        style = DEFAULT_STYLE

    attrs = {
        'style': formatStyle(style),
        'id': str(nid),
        inkex.addNS('cx', 'sodipodi'): str(cx),
        inkex.addNS('cy', 'sodipodi'): str(cy),
        inkex.addNS('rx', 'sodipodi'): str(rx),
        inkex.addNS('ry', 'sodipodi'): str(ry),
        inkex.addNS('start', 'sodipodi'): str(startEnd[0]),
        inkex.addNS('end', 'sodipodi'): str(startEnd[1]),
        # Ellipse sectors will be drawn open
        inkex.addNS('open', 'sodipodi'): 'True',
        inkex.addNS('type', 'sodipodi'): 'arc',
        'transform': ''
    }
    return inkex.etree.SubElement(parent, inkex.addNS('path', 'svg'), attrs)


def line((x1, y1), (x2, y2), name, parent, style):
    """draw an SVG line segment between the given (raw) points"""
    if not style:
        style = DEFAULT_STYLE

    attrs = {
        'style': formatStyle(style),
        inkex.addNS('label', 'inkscape'): name,
        'd': 'M ' + str(x1) + ',' + str(y1) + ' L ' + str(x2) + ',' + str(y2)
    }
    inkex.etree.SubElement(parent, inkex.addNS('path', 'svg'), attrs)


def make_segment_data(radius, segments):
    """
    Calculate the angles and radiei needed to draw the variouse arcs.

    @param radius Radius of the constucted dome in cm
    @param segments Number of segments(resolution) to divide the dome into

    @return data A dictionary of <segment number>: (angle, radius)
    """
    data = {}
    angle_a = (pi / 2) / segments
    angle_b = (pi - angle_a) / 2
    thickness = (cos(angle_b) * radius) * 2
    #main loop to calculate the needed angle and radius for the cone pattern
    for i in range(1, segments + 1):
        angle_m = angle_a * i
        cone_r = radius * sin(angle_m)
        c = 2 * pi * cone_r

        angle_c = 0
        if i == segments:
            angle_c = angle_b
        else:
            angle_c = pi - (pi / 2) - angle_m
            angle_c = angle_b - angle_c
        seg_r = cone_r / cos(angle_c)
        #find the angle for the flat pattern from the radians
        # fomular s/r = theta
        angle_t = c / seg_r
        data[i] = (angle_t, seg_r)
    return data, thickness

make_dome_data = make_segment_data


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
        return math.sqrt(x * x + y * y)

    def _set_length(self, length):
        v = self._v
        try:
            x, y = v
            l = length / math.sqrt(x * x + y * y)
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
        n = iter(iterable).next
        vec = cls.__new__(cls, object)
        vec._v = [float(n()), float(n())]
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
        v._v = [float(xx - x), float(yy - y)]
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
            msg = "There are 2 values in this object, index should be 0 or 1"
            raise IndexError(msg)

    def __setitem__(self, index, value):
        """Sets a component as though the vector were a list."""

        try:
            self._v[index] = 1.0 * value
        except IndexError:
            msg = "There are 2 values in this object, index should be 0 or 1!"
            raise IndexError(msg)
        except TypeError:
            raise TypeError("Must be a number")

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
        return Vector2.from_floats(x + xx, y + yy)

    def __iadd__(self, rhs):
        xx, yy = rhs
        v = self._v
        v[0] += xx
        v[1] += yy
        return self

    def __radd__(self, lhs):
        x, y = self._v
        xx, yy = lhs
        return self.from_floats(x + xx, y + yy)

    def __sub__(self, rhs):
        x, y = self._v
        xx, yy = rhs
        return Vector2.from_floats(x - xx, y - yy)

    def __rsub__(self, lhs):
        x, y = self._v
        xx, yy = lhs
        return self.from_floats(xx - x, yy - y)

    def _isub__(self, rhs):

        xx, yy = rhs
        v = self._v
        v[0] -= xx
        v[1] -= yy
        return self

    def __mul__(self, rhs):
        """
        Return the result of multiplying this vector with a scalar or a
        vector-list object.
        """
        x, y = self._v
        if hasattr(rhs, "__getitem__"):
            xx, yy = rhs
            return Vector2.from_floats(x * xx, y * yy)
        else:
            return Vector2.from_floats(x * rhs, y * rhs)

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
        return self.from_floats(x * xx, y * yy)

    def __div__(self, rhs):
        """
        Return the result of dividing this vector by a scalar or a
        vector-list object.
        """
        x, y = self._v
        if hasattr(rhs, "__getitem__"):
            xx, yy, = rhs
            return Vector2.from_floats(x / xx, y / yy)
        else:
            return Vector2.from_floats(x / rhs, y / rhs)

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
        return self.from_floats(xx / x, yy / x)

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
        return tuple(v[ord(c) - ord_x] for c in keys)

    def as_tuple(self):
        """Converts this vector to a tuple.

        @rtype: Tuple
        @return: Tuple containing the vector components
        """
        return tuple(self._v)

    def get_length(self):
        """Returns the length of this vector."""
        x, y = self._v
        return math.sqrt(x * x + y * y)
    get_magnitude = get_length

    def normalise(self):
        """Normalises this vector."""
        v = self._v
        x, y = v
        l = math.sqrt(x * x + y * y)
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

    def get_angle(self, degrees=False):
        """Get the angle made agains the x axis"""
        x, y = self._v
        if degrees:
            return math.degrees(math.atan2(y, x))
        else:
            return math.atan2(y, x)

    def get_normalised(self):
        x, y = self._v
        l = math.sqrt(x * x + y * y)
        return Vector2.from_floats(x / l, y / l)
    get_normalized = get_normalised

    def get_distance_to(self, p):
        """Returns the distance to a point.

        @param: A Vector2 or list-like object with at least 2 values.
        @return: distance
        """
        x, y = self._v
        xx, yy = p
        dx = xx - x
        dy = yy - y
        return math.sqrt(dx * dx + dy * dy)


class Path(object):
    """SVG path data class"""

    __slots__ = ('_d',)

    def __init__(self):
        self._d = []

    @property
    def d(self):
        """Get the data array for this path"""
        return self._d

    def __iter__(self):
        for i in self._d:
            yield i

    def __len__(self):
        return len(self._d)

    def __repr__(self):
        return "<abag_utils.Path %s>" % self._d

    def __str__(self):
        return self.__repr__()

    def command(func):
        def wrapper(self, *args):
            # Check function called with correct number of arguments.
            func(self, *args)
            self._d.append([func.__name__, list(args)])
        return wrapper

    @command
    def M(self, x, y):
        pass

    @command
    def m(self, x, y):
        pass

    @command
    def Z(self):
        pass

    @command
    def z(self):
        pass

    @command
    def L(self, x, y):
        pass

    @command
    def l(self, x, y):
        pass

    @command
    def H(self, x):
        pass

    @command
    def h(self, x):
        pass

    @command
    def V(self, y):
        pass

    @command
    def v(self, y):
        pass

    @command
    def C(self, x1, y1, x2, y2, x, y):
        pass

    @command
    def c(self, x1, y1, x2, y2, x, y):
        pass

    @command
    def S(self, x2, y2, x, y):
        pass

    @command
    def s(self, x2, y2, x, y):
        pass

    @command
    def Q(self, x1, y1, x, y):
        pass

    @command
    def q(self, x1, y1, x, y):
        pass

    @command
    def T(self, x, y):
        pass

    @command
    def t(self, x, y):
        pass

    @command
    def A(self, rx, ry, xar, laf, sf, x, y):
        pass

    @command
    def a(self, rx, ry, xar, laf, sw, x, y):
        pass


class Piece(object):
    """
    Base class for all pattern pieces
    """

    def __init__(self, label='', name=''):
        self.label = label
        self.name = name
        self._d = Path()
        self._path = Path()
        self.start_loc = (0, 0)

    def _build_path(self):
        pass

    @property
    def path(self):
        if len(self._path) == 0:
            self._build_path()
        return self._path

    @property
    def svg_id(self):
        ret = self.label
        if ret == '':
            ret = 'piece_'
        return ret + str(randint(1, 50000))

    # TODO: Made this into a property with getters and setters
    def set_start_loc(self, x, y):
        self.start_loc = (x, y)
        self._build_path()


class DomePiece(Piece):

    def __init__(self, _id, angle, radius, thickness):
        super(DomePiece, self).__init__()
        self.id = _id
        # Angle in radians
        self.angle = angle
        self.outer_radius = radius
        self.inner_radius = radius - thickness
        self.thickness = thickness

    @property
    def radius(self):
        return self.outer_radius

    @staticmethod
    def get_arch_flags(angle):
        if angle <= pi:
            laf1 = 0
            sf1 = 1
            laf2 = 0
            sf2 = 0
        else:
            laf1 = 1
            sf1 = 1
            laf2 = 1
            sf2 = 0
        return laf1, sf1, laf2, sf2

    def _build_path(self):
        cx, cy = self.start_loc
        angle = self.angle
        r1 = self.outer_radius
        r2 = self.inner_radius
        sx = cx + r1
        sy = cy

        laf, sf, laf2, sf2 = self.get_arch_flags(angle)

        p = Path()
        p.M(sx, sy)

        x, y = point_on_circle(r1, angle)
        p.A(r1, r1, 0, laf, sf, cx + x, cy + y)

        x, y = point_on_circle(r2, angle)
        p.L(cx + x, cy + y)

        p.A(r2, r2, 0, laf2, sf2, cx + r2, cy)
        p.L(sx, sy)
        p.Z()

        self._path = p