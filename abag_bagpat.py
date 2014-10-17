#!/usr/bin/env python
"""
abag_bagpat.py
The original Ananabag pattern generator inkscape extension
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
import re
from simplestyle import formatStyle
from simplepath import formatPath
from math import pi, degrees
from random import randint
from types import DictType, TupleType, StringType
from abag_utils import circle, ellipse_id, point_on_circle, make_dome_data,\
                        DomePiece, Piece, Path, Vector2


def svg_add_text(node, x, y, text):
    style = {
        'font-size': '12px',
        'fill-opacity': '1.0',
        'stroke': 'none',
        'font-weight': 'normal',
        'font-style': 'normal',
        'fill': '#000'
    }
    el = inkex.etree.SubElement(node, inkex.addNS('text', 'svg'))
    el.set('style', formatStyle(style))
    el.set('x', str(x))
    el.set('y', str(y))
    el.text = text


def svg_add_tspan(node, text, style):
    el = inkex.etree.SubElement(node, inkex.addNS('tspan', 'svg'))
    el.set('style', formatStyle(style))
    el.text = text


def piece_get_text_arch(p):
    r = p.outer_radius - (p.thickness / 3)
    return r, 0, p.angle


def make_zipper_data(radius, thickness, join_w, zip_h, top_h, bottom_h):
        """
        Calculate dimensions and points for each piece, top, bottom and joiner.
        @return List List of dics where keys are the name of each piece
        """
        c = 2 * pi * radius
        length = c - join_w
        data = {
            'BodyStrip': {'label': 'B1', 'd': (c, thickness)},
            'ZipTop': {'label': 'Z1', 'd': (length, top_h)},
            'ZipBottom': {'label': 'Z2', 'd': (length, bottom_h)},
            'ZipJoin': {'label': 'Z3', 'd': (join_w, top_h + zip_h + bottom_h)},
        }
        return data


class RectPattern(Piece):
    """Rectangular pattern piece class"""

    def __init__(self, width, height, label='', name=''):
        super(RectPattern, self).__init__(label, name)
        self.width = width
        self.height = height

    def _build_path(self):
        w = self.width
        h = self.height
        sx, sy = self.start_loc

        p = Path()
        p.M(sx, sy)
        p.l(w, 0.0)
        p.l(0.0, h)
        p.l(-w, 0.0)
        p.l(0.0, -h)
        p.z()

        self._path = p


class RectSeamPattern(RectPattern):

    left = 0
    right = 0
    top = 0
    bottom = 0

    def __init__(self, width, height, label='', name='', seams={}):
        super(RectSeamPattern, self).__init__(width, height, label, name)
        self._set_seams(seams)

    @classmethod
    def from_rect(cls, rect, seams={}):
        label = "%sS" % rect.label
        name = "%s Seam" % rect.name

        new = cls(rect.width, rect.height, label, name, seams)
        new.start_loc = rect.start_loc
        return new

    def _build_path(self):
        ls = self.left
        rs = self.right
        ts = self.top
        bs = self.bottom
        sx, sy = self.start_loc

        # adjest for the seams
        sx -= ls
        sy -= bs
        w = self.width + rs + ls
        h = self.height + ts + bs

        p = Path()
        p.M(sx, sy)
        p.l(w, 0.0)
        p.l(0.0, h)
        p.l(-w, 0.0)
        p.l(0.0, -h)
        p.z()

        self._path = p

    def _set_seams(self, seams):
        #inkex.debug(type(seams))
        if type(seams) is DictType:
            if 'top' in seams:
                self.top = seams['top']
            if 'right' in seams:
                self.right = seams['right']
            if 'bottom' in seams:
                self.bottom = seams['bottom']
            if 'left' in seams:
                self.left = seams['left']
        else:
            self.top = self.right = self.bottom = self.left = seams
    set_seams = _set_seams


class DomeSeamPiece(DomePiece):

    outer = 0
    inner = 0
    end = 0

    def __init__(self, _id, angle, radius, thickness, **kwargs):
        super(DomeSeamPiece, self).__init__(_id, angle, radius, thickness)
        self._set_seams(kwargs)

    @classmethod
    def from_dome_piece(cls, piece):
        pid = piece.id
        angle = piece.angle
        radius = piece.radius
        thickness = piece.thickness

        new = cls(pid, angle, radius, thickness)
        new.start_loc = piece.start_loc
        return new

    def _build_path(self):
        # Draw the dome piece including the seams, which includes the end part.
        # The end part(cap) is a rectangle appened to the end of each circular
        # segment.
        cx, cy = self.start_loc
        angle = self.angle
        r1 = self.outer_radius
        r2 = self.inner_radius
        s1 = self.outer
        s2 = self.inner
        s3 = self.end
        laf, sf, laf2, sf2 = self.get_arch_flags(self.angle)

        r1 += s1
        r2 -= s2

        sx = cx + r1
        sy = cy

        # Draw flow, start with the outer arc, first end seam, inner arch, then
        # final end seam and close the path.

        # FIXME: For some reason the top piece only gets one set of end seams

        p = Path()
        p.M(sx, sy)

        # Outer arch
        x, y = point_on_circle(r1, angle)
        ex = cx + x
        ey = cy + y
        p.A(r1, r1, 0, laf, sf, ex, ey)

        # First end seam
        x, y = point_on_circle(r2, angle)
        v = Vector2.from_points((ex, ey), (cx + x, cy + y))
        vp = v.perpendicular()
        vp.set_length(s3)

        p.l(-vp.x, -vp.y)
        p.l(v.x, v.y)
        p.l(vp.x, vp.y)

        # Inner arch
        ex = cx + r2
        ey = cy
        p.A(r2, r2, 0, laf2, sf2, ex, ey)

        # Second end seam
        v = Vector2.from_points((ex, ey), (sx, sy))
        vp = v.perpendicular()
        vp.set_length(s3)

        p.l(-vp.x, -vp.y)
        p.l(v.x, v.y)
        p.l(vp.x, vp.y)
        p.z()

        self._path = p

    def _set_seams(self, seams):
        if type(seams) is DictType:
            if 'outer' in seams:
                self.outer = seams['outer']
            if 'inner' in seams:
                self.inner = seams['inner']
            if 'end' in seams:
                self.end = seams['end']
        else:
            self.outer = self.inner = self.end = seams
    set_seams = _set_seams


class Abagpat(inkex.Effect):
    """
    Example Inkscape effect rendering to render a pattern to make a dome from
    """
    def __init__(self):
        """
        Constructor.
        Defines all the variable for the script
        """
        inkex.Effect.__init__(self)

        self._lines = []

        self.OptionParser.add_option("--tab", action="store", type="string",
            dest="tab", default="object")

        options = (
            # Common options
            ("--radius", "store", "float", "radius", "10.0",
                "What is the radius"),
            ("--segments", "store", "int", "segments", "4",
                "How many segments to make the dome"),
            ("--seams", "store", "int", "seams", "1",
                "How many seams per segment"),
            ("--showSegData", "store", "inkbool", "showSegData", "false",
                "Show segment data table?"),
            ("--showSegLabel", "store", "inkbool", "showSegLabel", "true",
                "SHow segment labels?"),
            # Zipper options
            ("--zipperTop", "store", "float", "zipperTop", "1.0",
                "Width of piece above zipper"),
            ("--zipperBottom", "store", "float", "zipperBottom", "1.0",
                "Width of piece under the zipper"),
            ("--zipperStrapJoin", "store", "float", "zipperStrapJoin", "1.0",
                "Width of the join, must be greater than the webbing"),
            ("--zipperHeight", "store", "float", "zipperHeight", "1.0",
                "Height of the zipper"),
            # Seam options
            ("--addSeamAllowence", "store", "inkbool", "addSeams", "false",
                "Add seams allowence in?"),
            ("--seamAllowenceInner", "store", "float", "seamInner", "0.0",
                "Seam allowence for the inner seam"),
            ("--seamAllowenceEnd", "store", "float", "seamEnd", "0.0",
                "Seam allowence for the ends of each segment"),
            ("--seamAllowenceOuter", "store", "float", "seamOuter", "0.0",
                "Seam allowence for the outer seam"),
            ("--seamAllowenceOther", "store", "float", "seamOther", "0.0",
                "Seam allowence for the other seams"),
            # Rendering options
            #("--topCone", "store", "inkbool", "topCone", "false",
                #"Render the top cone as a circle?"),
            ("--onlyRender", "store", "inkbool", "onlyRender", "false",
                "Render only some segments?"),
            ("--renderSegmentsFrom", "store", "int", "rendSegsFrom", "20",
                "Render segments from:"),
            ("--renderSegmentsTo", "store", "int", "rendSegsTo", "20",
                "Render segments to:")
        )

        for oLongName, oAction, oType, oDest, oDefault, oHelp in options:
            self.OptionParser.add_option(oLongName, action="store", type=oType,
                    dest=oDest, default=oDefault, help=oHelp)

    def add_info_lines(self, lines):
        t = type(lines)
        if t is TupleType:
            self._lines.extend(lines)
        elif t is StringType:
            self._lines.append(lines)

    def write_info_lines(self):
        se = inkex.etree.SubElement
        s = {'font-size': '12px', 'font-weight': 'normal'}
        fs = formatStyle(s)
        n = se(self.current_layer, inkex.addNS('text', 'svg'), {'style': fs})
        lattr = {'style': fs, inkex.addNS('role', 'sodipodi'): 'line'}

        s['font-size'] = '16px'
        s['font-weight'] = 'bold'

        hattr = {
            'style': formatStyle(s),
            inkex.addNS('role', 'sodipodi'): 'line'
        }

        for l in self._lines:
            if l.startswith('$'):
                attr = hattr
                l = l.lstrip('$')
            else:
                attr = lattr
            se(n, inkex.addNS('tspan', 'svg'), attr).text = l

    def write_dome_piece_label(self, radius, thickness, node, order):
        #thickness = self.options.thickness
        r = radius - (thickness / 3)
        startend = (0, 2 * pi)
        nid = 'text_path' + str(order) + str(randint(1, 50000))

        ellipse_id((r, r), self.view_center, node, nid, startend)
        # Create text element
        attr = {
            'style': formatStyle({'font-size': str(int(thickness / 8))})
        }
        t = inkex.etree.Element(inkex.addNS('text', 'svg'), attr)
        tp = inkex.etree.SubElement(t, inkex.addNS('textPath', 'svg'))

        tp.set(inkex.addNS('href', 'xlink'), "#" + nid)
        tp.set('startOffset', str(25 / self.options.segments) + "%")
        tp.text = "S%i - dome radius %.1fcm" % (order, self.options.radius)

        node.append(t)

    def effect(self):
        # a short hand
        so = self.options
        o = self.options

        seamInner = so.seamInner
        seamOuter = so.seamOuter
        seamEnd = so.seamEnd

        cx, cy = self.view_center
        # Put in in the centre of the current view
        #center = self.view_center
        domedata, thickness = make_dome_data(o.radius, o.segments)
        #segData = data_dict

        # change radius(cm) into pixels
        #r_px = inkex.unittouu(str(o.radius) + 'cm')
        thicknessPx = inkex.unittouu(str(thickness) + "cm")

        # change seams from cm to pixels
        seamInner = inkex.unittouu(str(o.seamInner) + "cm")
        seamOuter = inkex.unittouu(str(o.seamOuter) + "cm")
        seamEnd = inkex.unittouu(str(o.seamEnd) + "cm")
        seamOther = inkex.unittouu(str(so.seamOther) + 'cm')

        SubElement = inkex.etree.SubElement

        #inkex.debug(type(seamOther))

        # line styles and node attributes
        line_style = {
            'stroke': '#000000',
            'stroke-width': '1.0px',
            'fill': 'none'
        }

        #lineStyle = line_style
        #defaultStyle = lineStyle
        attr = {'style': formatStyle(line_style)}
        #defaultAttr = attr

        self.add_info_lines(
            ("$Pattern Info",
            "Total segments: %i" % o.segments,
            "Radius of dome: %.1fcm" % (o.radius),
            "Segment thickness: %.3fcm" % (thickness),
            "rendering line thickness: %.3f" % (inkex.uutounit(0.5, 'cm')),
            " ")
        )

        if o.addSeams:
            self.add_info_lines(
                ("$Seam Allowences",
                "inner seam: %.1fcm" % (o.seamInner),
                "Outer seam: %.1fcm" % (o.seamOuter),
                "End seam: %.1fcm" % (o.seamEnd),
                "Other seams: %.1fcm" % (o.seamOther),
                " ")
            )
        # zipper and body strip
        zipdata = make_zipper_data(o.radius, thickness,
                                    o.zipperStrapJoin, o.zipperHeight,
                                    o.zipperTop, o.zipperBottom)
        regex = re.compile("([a-z])([A-Z])")
        for key, val in zipdata.iteritems():
            w, h = val['d']
            x1, y1 = (200, 200)

            wpx = inkex.unittouu(str(w) + 'cm')
            hpx = inkex.unittouu(str(h) + 'cm')
            label = val['label']
            name = regex.sub('\g<1> \g<2>', key)

            rect = RectPattern(wpx, hpx, label, name)
            rect.set_start_loc(x1, y1)

            grp = SubElement(self.current_layer, 'g',
                {inkex.addNS('label', 'inkscape'): key})

            attr['d'] = formatPath(rect.path)
            SubElement(grp, inkex.addNS('path', 'svg'), attr)

            if o.addSeams:
                seam = RectSeamPattern.from_rect(rect)
                seam.set_seams(seamOther)

                if seam.label.startswith('Z1'):
                    seam.bottom = 0
                elif seam.label.startswith('Z2'):
                    seam.top = 0

                attr['d'] = formatPath(seam.path)
                SubElement(grp, inkex.addNS('path', 'svg'), attr)

            # add labels to rendered piece
            svg_add_text(grp, 212, y1 + (rect.height / 4),
                                    "%s (%s)" % (rect.name, rect.label))

            self.add_info_lines(
                ("$" + rect.name + " (" + rect.label + ")",
                "Width: %.3fcm" % (w),
                "Height: %.3fcm" % (h))
            )

        #return

        # loop through the data_dict making each segment in turn using the data
        # OPTIMIZE: Should use enumerate here
        for i in xrange(1, len(domedata) + 1):
            # create a group to put this pattern in
            grp = SubElement(self.current_layer, 'g',
                        {inkex.addNS('label', 'inkscape'): "Segment " + str(i)})
            #get the data we need from the dictionary
            angle, radius = domedata[i]
            angle = angle / o.seams
            r = inkex.unittouu(str(radius) + "cm")

            if i == 1:
                # adjust top cone to be a flat circle using pixel units
                r = (r * angle) / (2 * pi)
                angle = 2 * pi
                circle(r, cx, cy, grp, line_style)
                if o.addSeams:
                    circle(r + seamOuter, cx, cy, grp, line_style)
            else:
                piece = DomePiece(i, angle, r, thicknessPx)
                piece.set_start_loc(cx, cy)

                attr['d'] = formatPath(piece.path)
                SubElement(grp, inkex.addNS('path', 'svg'), attr)

                if o.addSeams:
                    # set all the seams
                    seam = DomeSeamPiece.from_dome_piece(piece)
                    seam.set_seams({
                        'outer': seamOuter,
                        'inner': seamInner,
                        'end': seamEnd
                    })
                    attr['d'] = formatPath(seam.path)
                    SubElement(grp, inkex.addNS('path', 'svg'), attr)

            if o.showSegLabel:
                self.write_dome_piece_label(r, thicknessPx, grp, i)

            self.add_info_lines(
                ('$S %i data:' % i,
                'Outer radius: %.3fcm' % radius,
                'Inner radius: %.3fcm' % (radius - thickness),
                'Angle: %.4f' % degrees(angle))
            )

        #self.addInfoLines(lines)
        if so.showSegData:
            self.writeInfoLines()


d = Abagpat()
d.affect()
