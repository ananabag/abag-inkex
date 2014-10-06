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
from simplepath import parsePath
from math import radians, pi, cos, sin
from random import randint
from types import *
from abag_utils import line, ellipse, ellipseId, DomeSegment, RectanglePiece


# make aliases
SubElement = inkex.etree.SubElement


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

        self._lines = []

        self.OptionParser.add_option("--tab", action="store", type="string",
            dest="tab", default="object")
            
        options = (
            # Common options
            ("--radius", "store", "float", "radius", "10.0", "What is the radius"),
            ("--segments", "store", "int", "segments", "4", "How many segments to make the dome"),
            ("--seams", "store", "int", "seams", "1", "How many seams per segment"),
            ("--showSegData", "store", "inkbool", "showSegData", "false", "Show segment data table?"),
            ("--showSegLabel", "store", "inkbool", "showSegLabel", "true", "SHow segment labels?"),
            # Zipper options
            ("--zipperTop", "store", "float", "zipperTop", "1.0", "Width of piece above zipper"),
            ("--zipperBottom", "store", "float", "zipperBottom", "1.0", "Width of piece under the zipper"),
            ("--zipperStrapJoin", "store", "float", "zipperStrapJoin", "1.0", "Width of the join, must be greater than the webbing"),
            ("--zipperHeight", "store", "float", "zipperHeight", "1.0", "Height of the zipper"),
            # Seam options
            ("--addSeamAllowence", "store", "inkbool", "addSeams", "false", "Add seams allowence in?"),
            ("--seamAllowenceInner", "store", "float", "seamInner", "0.0", "Seam allowence for the inner seam"),
            ("--seamAllowenceEnd", "store", "float", "seamEnd", "0.0", "Seam allowence for the ends of each segment"),
            ("--seamAllowenceOuter", "store", "float", "seamOuter", "0.0", "Seam allowence for the outer seam"),
            ("--seamAllowenceOther", "store", "float", "seamOther", "0.0", "Seam allowence for the other seams"),
            # Rendering options
            ("--topCone", "store", "inkbool", "topCone", "false", "Render the top cone as a circle?"),
            ("--onlyRender", "store", "inkbool", "onlyRender", "false", "Render only some segments?"),
            ("--renderSegmentsFrom", "store", "int", "rendSegsFrom", "20", "Render segments from:"),
            ("--renderSegmentsTo", "store", "int", "rendSegsTo", "20", "Render segments to:")
        )
        
        for oLongName, oAction, oType, oDest, oDefault, oHelp in options:
            self.OptionParser.add_option(oLongName, action="store", type=oType,
                    dest=oDest, default=oDefault, help=oHelp)

    def addText(self,node,x,y,text):
        style = {'font-size': '12px',
                'fill-opacity': '1.0',
                'stroke': 'none',
                'font-weight': 'normal',
                'font-style': 'normal',
                'fill': '#000'}
        elem = SubElement(node, inkex.addNS('text','svg'))
        elem.set('style', formatStyle(style))
        elem.set('x', str(x))
        elem.set('y', str(y))
        elem.text = text
        
    def addInfoLines(self, lines):
        if type(lines) is TupleType:
            self._lines.extend(lines)
        else:
            raise TypeError('$lines must be tuple')
 
    def writeInfoLines(self):
        style = {
            'font-size':'12px',
            'font-weight': 'normal'
        }
        fmtStyle = formatStyle(style)
        node = SubElement(self.current_layer, inkex.addNS('text','svg'),
            {'style': fmtStyle}
        )

        lineAttr = {
            'style': fmtStyle,
            inkex.addNS('role','sodipodi'):'line'
        }

        style['font-size'] = '16px'
        style['font-weight'] = 'bold'

        headAttr = {
            'style': formatStyle(style),
            inkex.addNS('role','sodipodi'):'line'
        }

        for line in self._lines:
            if line.startswith('$'):
                attr = headAttr
                line = line.lstrip('$')
            else:
                attr = lineAttr
            SubElement(node, inkex.addNS('tspan','svg'), attr).text = line
    
    def writeSegLabel(self, segment, node, count):
        r, s, e = segment.get_text_arch()
        ID = "mypath" + str(count) + str(randint(1,50000))
        ep = ellipseId((r, r), self.view_center, node, ID, (s, e))
        # Create text element
        attr = {
            'style': formatStyle({'font-size':str(int(segment.thickness/8))})
        }
        text = inkex.etree.Element(inkex.addNS('text','svg'), attr)
        textPath = SubElement(text, inkex.addNS('textPath', 'svg'))
        textPath.set(inkex.addNS('href', 'xlink'), "#"+ID)
        textPath.set('startOffset', str(25/self.options.segments)+"%")
        textPath.text = "S%i, for dome of radius %.1fcm" % (count, self.options.radius)
        # append it to the main group
        node.append(text)
        
    writeSegmentLabel = writeSegLabel

    @staticmethod
    def addTspan(node, text, style):
        SubElement(node, inkex.addNS('tspan','svg'), style).text = text
    
    @staticmethod
    def getSegmentData(radius, segments):
        """
        Calculate the angles and radiei needed to draw the variouse arcs.

        @param radius The radius of the constucted dome in cm
        @param segments The number of segments(resolution) to divide the dome into

        @return data This is dict of <segment number>: (angle, radius)
        """
        data = {}
        angle_a = (pi/2)/segments
        angle_b = (pi-angle_a)/2
        thickness = (cos(angle_b)*radius)*2
        #main loop to calculate the needed angle and radius for the cone pattern
        for i in range(1,segments+1):
            angle_m = angle_a * i
            cone_r = radius * sin(angle_m)
            c = 2 * pi * cone_r

            angle_c = 0
            if i == segments:
                angle_c = angle_b
            else:
                angle_c = pi - (pi/2) - angle_m
                angle_c = angle_b - angle_c
            seg_r =  cone_r / cos(angle_c)
            #find the angle for the flat pattern from the radians fomular s/r = theta
            angle_t = c / seg_r
            data[i] = (angle_t, seg_r)
        return data, thickness
    
    @staticmethod
    def getZipperData(radius, thickness, joinWidth, zipHeight, topHeight, bottomHeight):
        """
        Calculate the dimensions and points for each piece, top, bottom and joiner.
        @return List List of dics where keys are the name of each piece
        """
        cir = 2*pi*radius
        zipLength = cir - joinWidth
        data = {
            'BodyStrip' : {
                'd': (cir, thickness),
                'label': 'B1'
            },
            'ZipTop'    : {
                'd': (zipLength, topHeight),
                'label': 'Z1'
            },
            'ZipBottom' : {
                'd': (zipLength, bottomHeight),
                'label': 'Z2'
            },
            'ZipJoin'   : {
                'd': (joinWidth, topHeight + zipHeight + bottomHeight),
                'label': 'Z3'
            }
        }
        return data
    
    def effect(self):
    
        """
        This is where eveything happens, we will define a function that we will pass
        our infomation to
        """
        # a short hand
        so = self.options
        o = self.options
        
        seamInner = so.seamInner
        seamOuter = so.seamOuter
        seamEnd = so.seamEnd
        topCone = so.topCone

        cx, cy = self.view_center
        centre = self.view_center   # Put in in the centre of the current view
        data_dict, thickness = self.getSegmentData(o.radius, o.segments)
        segData = data_dict

        # change radius(cm) into pixels
        r_px = inkex.unittouu(str(o.radius)+'cm')
        radiusPx = r_px
        thicknessPx = inkex.unittouu(str(thickness) + "cm")

        # change seams from cm to pixels
        seamInner = inkex.unittouu(str(o.seamInner) + "cm")
        seamOuter = inkex.unittouu(str(o.seamOuter) + "cm")
        seamEnd = inkex.unittouu(str(o.seamEnd) + "cm")

        # use inkex.errormsg('something')

        # line styles and node attributes
        line_style = {
            'stroke': '#000000',
            'stroke-width': '0.5px',
            'fill': 'none'
        }

        lineStyle = line_style
        defaultStyle = lineStyle
        attr = {'style': formatStyle(lineStyle)}
        defaultAttr = attr

        self.addInfoLines(
            ("$Pattern Info",
            "Total segments: %i" % o.segments,
            "Radius of dome: %.1fcm" % (o.radius),
            "Segment thickness: %.3fcm" % (thickness),
            "rendering line thickness: %.3f" % (inkex.uutounit(0.5, 'cm')),
            " ")
        )
        
        if o.addSeams:
            self.addInfoLines(
                ("$Seam Allowences",
                "inner seam: %.1fcm" % (o.seamInner),
                "Outer seam: %.1fcm" % (o.seamOuter),
                "End seam: %.1fcm" % (o.seamEnd),
                "Other seams: %.1fcm" % (o.seamOther),
                " ")
            )        
        # zipper and body strip
        zip_data = self.getZipperData(o.radius, thickness,
                                    o.zipperStrapJoin, o.zipperHeight,
                                    o.zipperTop, o.zipperBottom)
        regex = re.compile("([a-z])([A-Z])")
        for key, val in zip_data.iteritems():
            w, h = val['d']
            x1, y1 = (200, 200)
            
            rect = RectanglePiece(inkex.unittouu(str(w) + 'cm'),
                                    inkex.unittouu(str(h) + 'cm'),
                                    val['label'],
                                    regex.sub("\g<1> \g<2>", key))
            rect.start_loc = (x1, y1)
                
            grp = SubElement(self.current_layer, 'g',
                {inkex.addNS('label', 'inkscape'): key})
                        
            #print(rect.get_svgd())
            #print('just here yo')
            attr['d'] = rect.get_svgd()
            SubElement(grp, inkex.addNS('path', 'svg'), attr)
            
            inkex.errormsg(parsePath(attr['d']))
            
            if o.addSeams:
                rect.set_all_seams(inkex.unittouu(str(so.seamOther) + 'cm'))

                if rect.label == 'Z1':
                    rect.bottom = 0
                elif rect.label == 'Z2':
                    rect.top = 0

                attr['d'] = rect.get_seams_svgd()
                SubElement(grp, inkex.addNS('path', 'svg'), attr)

            # add labels to rendered piece
            self.addText(grp, 212, y1 + (rect.height/4), "%s (%s)" % (rect.name, rect.label))
            self.addInfoLines(
                ("$" + rect.name + " (" + rect.label + ")",
                "Width: %.3fcm" % (w),
                "Height: %.3fcm" % (h))
            )
            
#        return

        # loop through the data_dict making each segment in turn using the data
        for i in range(1, len(data_dict)+1):
            # create a group to put this pattern in
#            grp_attribs = 
#            grpAttr = {inkex.addNS('label','inkscape'): "Segment " + str(i)}
            grp = SubElement(self.current_layer, 'g',
                        {inkex.addNS('label','inkscape'): "Segment " + str(i)})
            #get the data we need from the dictionary
            angle, radiusCm = data_dict[i]
            angle = angle / o.seams
            radiusPx = inkex.unittouu(str(radiusCm) + "cm")

            # get segment object
            if topCone and i == 1:
                # adjust top cone to be a flat circle using pixel units
                c = radiusPx * angle
                nr = c / (2 * pi)
                segment = DomeSegment(i, 2*pi, nr, thicknessPx)
                # adjustment for top cone using cm units
                c = radiusCm * angle
                nr = c / (2*pi)
                segment_cm = DomeSegment(i, 2*pi, nr, thicknessPx)
            else:
                segment = DomeSegment(i, angle, radiusPx, thicknessPx)
                segment_cm = DomeSegment(i, angle, radiusCm, thickness)

            segment.setPageCenter(cx, cy)

            self.addInfoLines(
                ('$S %i data:' % (segment_cm.segNumber),
                'Outer radius: %.3fcm' % (segment_cm.radiusOuter),
                'Inner radius: %.3fcm' % (segment_cm.radiusInner),
                'Angle: %.4f' % (segment_cm.angleD))
            )

            # always draw the outer curve
            radius, start, end = segment.get_outer_arch()
            ellipse((radius, radius), (cx, cy), grp, lineStyle, (start, end))

            if i != 1:
                # draw the inner curve only if we not in the first cone
                radius, start, end = segment.get_inner_arch()
                ellipse((radius, radius), (cx, cy), grp, lineStyle, (start, end))

            if not topCone:
                # draw the start line between the two curves
                p1, p2 = segment.get_start_cap()
                line(p1, p2, "line", grp, lineStyle)

                # draw the end line between the two curves
                p1, p2 = segment.get_end_cap()
                line(p1, p2, "line", grp, lineStyle)

            # add seams if required
            if o.addSeams:
                # set all the seams
                segment.set_all_seams(seamInner, seamOuter, seamEnd)

                # always add outer seam
                radius, start, end = segment.get_outer_seam_arch()
                ellipse((radius, radius), (cx, cy), grp, lineStyle, (start, end))

                if not topCone:
                    # add inner seam
                    radius, start, end = segment.get_inner_seam_arch()
                    ellipse((radius, radius), (cx, cy), grp, lineStyle, (start, end))

                    # add start cap seam
                    attrs = {'style': formatStyle(lineStyle)}
                    attrs['d'] = segment.get_start_seam_cap()
                    SubElement(grp, inkex.addNS('path', 'svg'), attrs)

                    # add end cap seam
                    attrs['d'] = segment.get_end_seam_cap()
                    SubElement(grp, inkex.addNS('path', 'svg'), attrs)

            # must switch this back to false after the first interation
            # so that other segments will have the thickness connectors
            if topCone:
                topCone = False

            #draw the path to put the text lable on
            if so.showSegLabel:
                self.writeSegLabel(segment, grp, i)
        
        #self.addInfoLines(lines)
        if so.showSegData:
            self.writeInfoLines()

d = DomePattern()
d.affect()
