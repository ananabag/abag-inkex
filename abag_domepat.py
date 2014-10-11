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
from simplestyle import *
from simplepath import formatPath
from math import pi, cos, sin
from random import randint
from abag_utils import line, ellipse, ellipse_id, point_on_circle, Path


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


class DomePattern(inkex.Effect):
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
        r_cm = self.options.radius
        seg = self.options.segments
        seams = self.options.seams
        cx, cy = self.view_center
        #Put in in the centre of the current views
        center = self.view_center
        data_dict, thickness = get_segment_data(r_cm, seg)

        #change radius(cm) into pixels
        #r_px = inkex.unittouu(str(r_cm) + 'cm')
        thickness_px = inkex.unittouu(str(thickness) + "cm")

        # use the same style info for all lines and arcs
        lineStyle = {
            'stroke': '#000000',
            'stroke-width': '0.5px',
            'fill': 'none'
        }
        # loop through the data_dict making each segment in turn using the data
        for i in range(1, len(data_dict) + 1):
        #for angle, radius in data.items():

            # create a group to put this pattern in
            grp_name = "Segment " + str(i)
            grp_attribs = {inkex.addNS('label', 'inkscape'): grp_name}
            #the group to put everything in
            grp = inkex.etree.SubElement(self.current_layer, 'g', grp_attribs)

            #get the data we need from the dictionary
            angle, radius_cm = data_dict[i]
            radius_cm = radius
            angle = angle / seams
            radius_px = inkex.unittouu(str(radius_cm) + "cm")
            #radiusPx = radius_px
            startEnd = (0, angle)
            radius_s = radius_px - thickness_px

            # draw the 2 arcs
            ellipse((radius_px, radius_px), center, grp, lineStyle, startEnd)
            ellipse((radius_s, radius_s), center, grp, lineStyle, startEnd)

            # draw the lines between the 2 arcs making a nice segment
            x1, y1 = point_on_circle(radius_px, angle)
            start = (cx + x1, cy + y1)

            x2, y2 = point_on_circle(radius_s, angle)
            end = (cx + x2, cy + y2)
            line(start, end, "line", grp, lineStyle)

            # draw the last line
            x1, y1 = point_on_circle(radius_px, 0)
            start = (cx + x1, cy + y1)

            x2, y2 = point_on_circle(radius_s, 0)
            end = (cx + x2, cy + y2)
            line(start, end, "line", grp, lineStyle)

            # draw arc to put the text along
            # FIXME there needs to be a ranbom part to this id
            nid = "mypath" + str(i) + str(randint(1, 50000))
            radius_s = radius_px - (thickness_px / 3)
            ellipse_id((radius_s, radius_s), center, grp, nid, startEnd)

            # Info string
            info = "S:%i-[Rcm:%.1f,Sg:,%i,Se:%i, Th:%.2f]"
            info = info % (i, r_cm, seg, seams, thickness)

            # Create text element
            style = {
                'text-align': 'right',
                'font-size': str(int(thickness_px / 8))
            }
            attrs = {'style': formatStyle(style)}
            text = inkex.etree.Element(inkex.addNS('text', 'svg'), attrs)
            textpath = inkex.etree.SubElement(text,
                                            inkex.addNS('textPath', 'svg'))
            textpath.set(inkex.addNS('href', 'xlink'), "#" + nid)
            offset = 25 / seg
            textpath.set('startOffset', str(offset) + "%")
            textpath.text = info

            # append it to the main group
            grp.append(text)


class DomePatternPath(DomePattern):

    def __init__(self):
        DomePattern.__init__(self)

    def effect(self):
        o = self.options
        #r_cm = o.radius
        seg = o.segments
        seams = o.seams
        cx, cy = center = self.view_center

        # data is a dict object
        data, thickness = get_segment_data(o.radians, seg)

        #change radius(cm) into pixels
        thickness_px = inkex.unittouu(str(thickness) + "cm")

        # use the same style info for all lines and arcs
        style = {'stroke': '#000000', 'stroke-width': '0.5px', 'fill': 'none'}
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

            # Start (x, y) also the end point
            sx = cx + r1
            sy = cy

            path = Path()
            path.M(sx, sy)

            # FIXME: The large-arc-flag and the sweep-flag need to toggled
            # according to the radians turned. This should be calculated here
            # before any 'A' function calles are made.
            inkex.debug(angle)
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

            #sattr['d'] = path.to_d_string()
            sattr['d'] = formatPath(path)
            sattr['id'] = 'segment_path' + str(i) + str(randint(1, 50000))

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
            textpath.text = "S:%i-[Rcm:%.1f,Sg:,%i,Se:%i, Th:%.2f]" % \
                                            (i, o.radius, seg, seams, thickness)
            # append it to the main group
            grp.append(text)


d = DomePatternPath()
d.affect()

