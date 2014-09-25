#!/usr/bin/env python

# These two lines are only needed if you don't put the script directly into
# the installation directory
import sys
sys.path.append('/usr/share/inkscape/extensions') #path to extensions

import inkex

# The simplestyle module provides functions for style parsing.
from simplestyle import formatStyle
from math import pi

def circle(r, cx, cy, parent, style, start_end=(0,2*pi)):
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
    
def ellipseId((rx, ry), (cx, cy), parent, ID, start_end=(0,2*pi), style=False):
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