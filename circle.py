#!/usr/bin/env python

# These two lines are only needed if you don't put the script directly into
# the installation directory
import sys
sys.path.append('/usr/share/inkscape/extensions') #path to extensions

# The simplestyle module provides functions for style parsing.
import inkex
from simplestyle import *
from math import radians, pi, cos, sin
from random import randint

def point_on_circle(radius, angle):
    x = radius * cos(angle)
    y = radius * sin(angle)
    return (x, y)
    
def get_segment_data(radius, segments):
    """calculate the angles and radiei needed to draw the variouse arcs"""
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
        #find the angle for the flat pattern from the radians fomular s/r = thata
        angle_t = c / seg_r
        data[i] = (angle_t, seg_r)
    return data, thickness

def draw_SVG_ellipse((rx, ry), (cx, cy), parent, style, start_end=(0,2*pi)):
    # add in an id variable to the attributs so I can pass it to the text 
    # to put it along the path
    #style = {'stroke': '#000000', 'stroke-width': '0.5px', 'fill': 'none'}
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
    
def draw_SVG_ellipse_id((rx, ry), (cx, cy), parent, ID, start_end=(0,2*pi)):
    # add in an id variable to the attributs so I can pass it to the text 
    # to put it along the path
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
def draw_SVG_line( (x1, y1), (x2, y2), name, parent, style):
    line_attribs = {'style' : formatStyle(style),
                    inkex.addNS('label','inkscape') : name,
                    'd' : 'M '+str(x1)+','+str(y1)+' L '+str(x2)+','+str(y2)}

    line = inkex.etree.SubElement(parent, inkex.addNS('path','svg'), line_attribs )

class Dome_Pattern(inkex.Effect):
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
        """
        This is where eveything happens, we will define a function that we will pass
        our infomation to
        """
        r_cm = self.options.radius
        seg = self.options.segments
        seams = self.options.seams
        cx, cy = self.view_center
        centre = self.view_center   #Put in in the centre of the current view
        data_dict, thickness = get_segment_data(r_cm, seg)
        
        #change radius(cm) into pixels
        r_px = inkex.unittouu(str(r_cm)+'cm')
        thickness_px = inkex.unittouu(str(thickness) + "cm")
        
        # setup stderr so that we can print to it for debugging        
        #saveout = sys.stdout
        #sys.stdout = sys.stderr

        # use the same style info for all lines and arcs
        line_style = {'stroke': '#000000', 'stroke-width': '0.5px', 'fill': 'none'}
        # loop through the data_dict making each segment in turn using the data
        for i in range(1, len(data_dict)+1):
            
            # create a group to put this pattern in
            grp_name = "Segment " + str(i)
            grp_attribs = {inkex.addNS('label','inkscape'):grp_name}
            #the group to put everything in
            grp = inkex.etree.SubElement(self.current_layer, 'g', grp_attribs)
            

            #get the data we need from the dictionary
            angle, radius_cm = data_dict[i]
            angle = angle/seams
            radius_px = inkex.unittouu(str(radius_cm) + "cm")
            start_end = (0, angle)
            radius_s = radius_px - thickness_px
            
            # draw the 2 arcs
            draw_SVG_ellipse((radius_px, radius_px), (cx, cy), grp, line_style, start_end)
            draw_SVG_ellipse((radius_s,radius_s), (cx, cy), grp, line_style, start_end)
            
            # draw the lines between the 2 arcs making a nice segment
            x1, y1 = point_on_circle(radius_px, angle)
            y1 = cy + y1
            x1 = cx + x1
            x2, y2 = point_on_circle(radius_s, angle)
            y2 = cy + y2
            x2 = cx + x2
            draw_SVG_line((x1, y1), (x2, y2), "line", grp, line_style)
            # draw the last line
            x1, y1 = point_on_circle(radius_px, 0)
            y1 = cy + y1
            x1 = cx + x1
            x2, y2 = point_on_circle(radius_s, 0)
            y2 = cy + y2
            x2 = cx + x2
            draw_SVG_line((x1, y1), (x2, y2), "line", grp, line_style)
            
            # draw arc to put the text along
            # FIXME there needs to be a ranbom part to this id
            ID = "mypath"+str(i)+str(randint(1,50000))
            radius_s = radius_px - (thickness_px/3)
            ep = draw_SVG_ellipse_id((radius_s, radius_s), (cx, cy), grp, ID, start_end)
            # string with infomation in it
            s = "S:%i-[Rcm:%.1f,Sg:,%i,Se:%i, Th:%.2f]" % (i, r_cm, seg, seams, thickness)
            
            # Create text element
            style = {'text-align' : 'right', 'font-size' : str(int(thickness_px / 8))}
            t_attribs = {'style': formatStyle(style)}
            text = inkex.etree.Element(inkex.addNS('text','svg'), t_attribs)
            textpath = inkex.etree.SubElement( text, inkex.addNS('textPath', 'svg'))
            textpath.set(inkex.addNS('href', 'xlink'), "#"+ID)
            offset = 25/seg
            textpath.set('startOffset', str(offset)+"%")
            textpath.text = s
            # append it to the main group
            grp.append(text)

d = Dome_Pattern()
d.affect()
        
