#!/usr/bin/env python

# These two lines are only needed if you don't put the script directly into
# the installation directory
try:
    import inkex
except ImportError as e:
    import sys
    sys.path.append('/usr/share/inkscape/extensions')
    import inkex

# The simplestyle module provides functions for style parsing.
import re
from simplestyle import *
from math import radians, pi, cos, sin
from random import randint
from types import *
import abag_utils as utils

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

        self.OptionParser.add_option("--tab",
            action="store", type="string",
            dest="tab", default="object")

        # common options
        self.OptionParser.add_option("--radius", action="store",
            type="float", dest="radius", default="10.0",
            help="What is the Radius")
        self.OptionParser.add_option("--segments", action="store",
            type="int", dest="segments", default="4",
            help="How many semgents to make the dome shape from")
        self.OptionParser.add_option("--seams", action="store",
            type="int", dest="seams", default="1",
            help="How many seams per segment")
        self.OptionParser.add_option("--showSegData", action="store",
            type="inkbool", dest="showSegData", default="false",
            help="Show segments data table?")
        self.OptionParser.add_option("--showSegLabel", action="store",
            type="inkbool", dest="showSegLabel", default="true",
            help="Show segments labels?")

        # zipper options
        self.OptionParser.add_option("--zipperTop", action="store",
            type="float", dest="zipperTop", default="1.0",
            help="Width of piece above zipper")
        self.OptionParser.add_option("--zipperBottom", action="store",
            type="float", dest="zipperBottom", default="1.0",
            help="Width of piece under the zipper")
        self.OptionParser.add_option("--zipperStrapJoin", action="store",
            type="float", dest="zipperStrapJoin", default="1.0",
            help="Width of the join, must be greater than the webbing")
        self.OptionParser.add_option("--zipperHeight", action="store",
            type="float", dest="zipperHeight", default="1.0",
            help="Height of the zipper")

        # seam allowence options
        self.OptionParser.add_option("--addSeamAllowence", action="store",
            type="inkbool", dest="addSeams", default="false",
            help="Add seams allowence in?")
        self.OptionParser.add_option("--seamAllowenceInner", action="store",
          type="float", dest="seamInner", default="0.0",
          help="Seam allowence for the inner seam")
        self.OptionParser.add_option("--seamAllowenceEnd", action="store",
          type="float", dest="seamEnd", default="0.0",
          help="Seam allowence for the ends of each segment")
        self.OptionParser.add_option("--seamAllowenceOuter", action="store",
          type="float", dest="seamOuter", default="0.0",
          help="Seam allowence for the outer seam")
        self.OptionParser.add_option("--seamAllowenceOther", action="store",
          type="float", dest="seamOther", default="0.0",
          help="Seam allowence for the other seams")

        # render options
        self.OptionParser.add_option("--topCone", action="store",
            type="inkbool", dest="topCone", default="false",
            help="Render the top cone as a circle?")
        self.OptionParser.add_option("--onlyRender", action="store",
            type="inkbool", dest="onlyRender", default="false",
            help="Render only some segments?")
        self.OptionParser.add_option("--renderSegmentsFrom", action="store",
            type="int", dest="rendSegsFrom", default="20",
            help="Render segments from:")
        self.OptionParser.add_option("--renderSegmentsTo", action="store",
            type="int", dest="rendSegsTo", default="20",
            help="Render segments to:")
            
        self.lines = ()

    def addText(self,node,x,y,text):
        s = {'font-size': '12px', 'fill-opacity': '1.0', 'stroke': 'none',
            'font-weight': 'normal', 'font-style': 'normal', 'fill': '#000'}       
        new = inkex.etree.SubElement(node,inkex.addNS('text','svg'))
        new.set('style', formatStyle(s))
        new.set('x', str(x))
        new.set('y', str(y))
        new.text = text
        
    def addInfoLines(self, lines):
        if type(lines) is TupleType:
            self.lines += lines
        else:
            raise TypeError('$lines must be tuple')
 
    def writeInfoLines(self):
        node = inkex.etree.SubElement(
                    self.current_layer,
                    inkex.addNS('text','svg'),
                    {'style': formatStyle({'text-align': 'left', 'font-size': '12px'})}
        )
        line_style = {'text-align':'right', 'font-size':'12px', 'font-weight': 'normal'}
        head_style = {'text-align':'right', 'font-size':'16px', 'font-weight': 'bold'}

        line_attr = {'style': formatStyle(line_style), inkex.addNS('role','sodipodi'):'line'}
        head_attr = {'style': formatStyle(head_style), inkex.addNS('role','sodipodi'):'line'}
        
        for i in self.lines:
            if i.startswith('$'):
                inkex.etree.SubElement(node, inkex.addNS('tspan','svg'), head_attr).text = i.lstrip('$')
            else:
                inkex.etree.SubElement(node, inkex.addNS('tspan','svg'), line_attr).text = i
    
    def writeSegLabel(self, segment, node, count):
        r, s, e = segment.get_text_arch()
        ID = "mypath" + str(count) + str(randint(1,50000))
        ep = utils.ellipseId((r, r), self.view_center, node, ID, (s, e))
        # Create text element
        attr = {'style': formatStyle({'text-align':'right', 'font-size':str(int(segment.thickness / 8))})}
        text = inkex.etree.Element(inkex.addNS('text','svg'), attr)
        textpath = inkex.etree.SubElement(text, inkex.addNS('textPath', 'svg'))
        textpath.set(inkex.addNS('href', 'xlink'), "#"+ID)
        textpath.set('startOffset', str(25/self.options.segments)+"%")
        textpath.text = "S%i, for dome of radius %.1fcm" % (count, self.options.radius)
        # append it to the main group
        node.append(text)

    @staticmethod
    def addTspan(node, text, style):
        inkex.etree.SubElement(node, inkex.addNS('tspan','svg'), style).text = text
    
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
        return {'BodyStrip' : {'d': (cir, thickness), 'label': 'B1'},
                'ZipTop'    : {'d': (zipLength, topHeight), 'label': 'Z1'},
                'ZipBottom' : {'d': (zipLength, bottomHeight), 'label': 'Z2'},
                'ZipJoin'   : {'d': (joinWidth, topHeight + zipHeight + bottomHeight), 'label': 'Z3'}}
    
    def effect(self):
    
        """
        This is where eveything happens, we will define a function that we will pass
        our infomation to
        """
        # a short hand
        so = self.options
        
        seamInner = so.seamInner
        seamOuter = so.seamOuter
        seamEnd = so.seamEnd
        topCone = so.topCone

        cx, cy = self.view_center
        centre = self.view_center   # Put in in the centre of the current view
        data_dict, thickness = self.getSegmentData(so.radius, so.segments)

        # change radius(cm) into pixels
        r_px = inkex.unittouu(str(so.radius)+'cm')
        thickness_px = inkex.unittouu(str(thickness) + "cm")

        # change seams from cm to pixels
        seamInner = inkex.unittouu(str(so.seamInner) + "cm")
        seamOuter = inkex.unittouu(str(so.seamOuter) + "cm")
        seamEnd = inkex.unittouu(str(so.seamEnd) + "cm")

        # setup stderr so that we can print to it for debugging
        #saveout = sys.stdout
        #sys.stdout = sys.stderr

        # line styles and node attributes
        line_style = {'stroke': '#000000', 'stroke-width': '0.5px', 'fill': 'none'}
        attr = {'style': formatStyle(line_style)}

        self.addInfoLines(
            ("$Pattern Info",
            "Total segments: %i" % so.segments,
            "Radius of dome: %.1fcm" % (so.radius),
            "Segment thickness: %.3fcm" % (thickness),
            "rendering line thickness: %.3f" % (inkex.uutounit(0.5, 'cm')),
            " ")
        )
        if so.addSeams:
            self.addInfoLines(
                ("$Seam Allowences",
                "inner seam: %.1fcm" % (so.seamInner),
                "Outer seam: %.1fcm" % (so.seamOuter),
                "End seam: %.1fcm" % (so.seamEnd),
                "Other seams: %.1fcm" % (so.seamOther),
                " ")
            )        
        # zipper and body strip
        zip_data = self.getZipperData(so.radius, thickness,
                                    so.zipperStrapJoin, so.zipperHeight,
                                    so.zipperTop, so.zipperBottom)
        regex = re.compile("([a-z])([A-Z])")
        for key, val in zip_data.iteritems():
            w, h = val['d']
            x1, y1 = (200, 200)
            
            rect = utils.RectanglePiece(inkex.unittouu(str(w) + 'cm'),
                                    inkex.unittouu(str(h) + 'cm'),
                                    val['label'],
                                    regex.sub("\g<1> \g<2>", key))
            rect.start_loc = (x1, y1)
            if so.addSeams:
                rect.set_all_seams(inkex.unittouu(str(so.seamOther) + 'cm'))
                if rect.label == 'Z1':
                    rect.bottom = 0
                elif rect.label == 'Z2':
                    rect.top = 0
                
            tgrp = inkex.etree.SubElement(self.current_layer, 'g',
                        {inkex.addNS('label', 'inkscape'):key})
                
            for i in rect.get_all_svgd():
                attr['d'] = i
                inkex.etree.SubElement(tgrp, inkex.addNS('path', 'svg'), attr)
            # add labels to rendered piece
            self.addText(tgrp, 212, y1 + (rect.height/4), "%s (%s)" % (rect.name, rect.label))
            self.addInfoLines(
                ("$" + rect.name + " (" + rect.label + ")",
                "Width: %.3fcm" % (w),
                "Height: %.3fcm" % (h))
            )

        # loop through the data_dict making each segment in turn using the data
        for i in range(1, len(data_dict)+1):
            # create a group to put this pattern in
            grp_attribs = {inkex.addNS('label','inkscape'): "Segment " + str(i)}
            grp = inkex.etree.SubElement(self.current_layer, 'g', grp_attribs)

            #get the data we need from the dictionary
            angle, radius_cm = data_dict[i]
            angle = angle/so.seams
            radius_px = inkex.unittouu(str(radius_cm) + "cm")

            # get segment object
            if topCone and i == 1:
                # adjust top cone to be a flat circle using pixel units
                c = radius_px * angle
                nr = c / (2*pi)
                segment = utils.DomeSegment(i, 2*pi, nr, thickness_px)
                # adjustment for top cone using cm units
                c = radius_cm * angle
                nr = c / (2*pi)
                segment_cm = utils.DomeSegment(i, 2*pi, nr, thickness_px)
            else:
                segment = utils.DomeSegment(i, angle, radius_px, thickness_px)
                segment_cm = utils.DomeSegment(i, angle, radius_cm, thickness)
            segment.setPageCenter(cx, cy)

            self.addInfoLines(
                ('$S %i data:' % (segment_cm.segNumber),
                'Outer radius: %.3fcm' % (segment_cm.radiusOuter),
                'Inner radius: %.3fcm' % (segment_cm.radiusInner),
                'Angle: %.4f' % (segment_cm.angleD))
            )

            # always draw the outer curve
            r, s, e = segment.get_outer_arch()
            utils.ellipse((r, r), (cx, cy), grp, line_style, (s, e))

            if i != 1:
                # draw the inner curve only if we not in the first cone
                r, s, e = segment.get_inner_arch()
                # FIXME should be using ellipseId() and use i as ID
                utils.ellipse((r, r), (cx, cy), grp, line_style, (s, e))
            if not topCone:
                # draw the start line between the two curves
                p1, p2 = segment.get_start_cap()
                utils.line(p1, p2, "line", grp, line_style)

                # draw the end line between the two curves
                p1, p2 = segment.get_end_cap()
                utils.line(p1, p2, "line", grp, line_style)

            # add seams if required
            if so.addSeams:
                # set all the seams
                segment.set_all_seams(seamInner, seamOuter, seamEnd)

                # always add outer seam
                r, s, e = segment.get_outer_seam_arch()
                utils.ellipse((r, r), (cx, cy), grp, line_style, (s, e))

                if not topCone:
                    # add inner seam
                    r, s, e = segment.get_inner_seam_arch()
                    utils.ellipse((r, r), (cx, cy), grp, line_style, (s, e))

                    # add start cap seam
                    path = segment.get_start_seam_cap()
                    attribs = {'style': formatStyle(line_style), 'd': path}
                    inkex.etree.SubElement(grp, inkex.addNS('path', 'svg'), attribs)

                    # add end cap seam
                    attribs['d'] = segment.get_end_seam_cap()
                    inkex.etree.SubElement(grp, inkex.addNS('path', 'svg'), attribs)

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
