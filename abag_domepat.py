#!/usr/bin/env python
"""
abag_domepat.py
The original Ananabag dome template generator Inkscape extensions
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
from simplestyle import formatStyle
from simplepath import formatPath
from math import pi, cos, sin
from random import randint
from abag_utils import ellipse_id, point_on_circle, Path


def get_segment_data(radius, segments):
    """calculate the angles and radiei needed to draw the variouse arcs"""
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
        # fomular s/r = thata
        angle_t = c / seg_r
        data[i] = (angle_t, seg_r)
    return data, thickness


class Domepat(inkex.Effect):
    """
    Example Inkscape effect rendering to render a pattern to make a dome from
    """
    def __init__(self):
        """
        Constructor.
        Defines all the variable for the script
        """
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("-r", "--radius", action="store",
          type="float", dest="radius", default="10.0",
          help="What is the Radius")
        self.OptionParser.add_option("-s", "--segments", action="store",
          type="int", dest="segments", default="4",
          help="How many semgents to make the dome shape from")
        self.OptionParser.add_option("-e", "--seams", action="store",
          type="int", dest="seams", default="1",
          help="How many seams per segment")

    def effect(self):
        o = self.options
        #r_cm = o.radius
        seg = o.segments
        seams = o.seams
        cx, cy = center = self.view_center

        # data is a dict object
        data, thickness = get_segment_data(o.radius, seg)

        #change radius(cm) into pixels
        thickness_px = inkex.unittouu(str(thickness) + "cm")

        # use the same style info for all lines and arcs
        style = {'stroke': '#000000', 'stroke-width': '1.0px', 'fill': 'none'}
        sattr = {'style': formatStyle(style), 'd': '', 'id': ''}

        style = {'text-align': 'right', 'font-size': str(int(thickness_px / 8))}
        iattr = {'style': formatStyle(style)}

        # loop through the data making each segment in turn using the data
        #for i in range(1, len(data) + 1):
        for key in data:
            i = key
            # create a group to put this pattern in
            attrs = {inkex.addNS('label', 'inkscape'): 'segment_%d' % key}
            grp = inkex.etree.SubElement(self.current_layer, 'g', attrs)

            #get the data we need from the dictionary
            angle, radius = data[key]
            angle = angle / seams
            r1 = inkex.unittouu(str(radius) + "cm")
            r2 = r1 - thickness_px

            #piece = DomePiece(key, angle, r1, thickness_px)
            #piece.set_start_loc(cx, cy)

            # Start (x, y) also the end point
            sx = cx + r1
            sy = cy

            path = Path()
            path.M(sx, sy)

            # NOTE: The large-arc-flag and the sweep-flag need to toggled
            # according to the radians turned. This should be calculated here
            # before any 'A' function calles are made.
            if angle <= pi:
                laf = 0
                sf = 1
                laf2 = 0
                sf2 = 0
            else:
                laf = 1
                sf = 1
                laf2 = 1
                sf2 = 0

            x, y = point_on_circle(r1, angle)
            path.A(r1, r1, 0, laf, sf, cx + x, cy + y)

            x, y = point_on_circle(r2, angle)
            path.L(cx + x, cy + y)

            path.A(r2, r2, 0, laf2, sf2, cx + r2, cy)
            path.L(sx, sy)
            path.Z()

            sattr['d'] = formatPath(path)
            sattr['id'] = 'dome_piece_path' + str(i) + str(randint(1, 50000))

            inkex.etree.SubElement(grp, inkex.addNS('path', 'svg'), sattr)

            # draw arc to put the text along
            # FIXME: use a better UUID generator
            nid = "info_label_path" + str(i) + str(randint(1, 50000))

            r3 = r1 - (thickness_px / 3)
            ellipse_id((r3, r3), center, grp, nid, (0, angle))

            text = inkex.etree.Element(inkex.addNS('text', 'svg'), iattr)
            textpath = inkex.etree.SubElement(text,
                                            inkex.addNS('textPath', 'svg'))
            textpath.set(inkex.addNS('href', 'xlink'), "#" + nid)
            textpath.set('startOffset', str(25 / seg) + "%")

            s = "S:%i-[Rcm:%.1f,Sg:,%i,Se:%i, Th:%.2f]"
            s = s % (i, o.radius, seg, seams, thickness)
            textpath.text = s

            # append it to the main group
            grp.append(text)


d = Domepat()
d.affect()

