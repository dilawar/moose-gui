"""
Add canvas

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2016, Dilawar Singh"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os
try:
    from Tkinter import *
except ImportError as e:
    from tkinter import *

import moosegui._globals as _globals
from moosegui.MooseCanvas import MooseCanvas

from moosegui.config import _logger
import moosegui.helper as helper
import moose


def draw_model( ):
    _logger.debug( "Drawing pathway" )
    g = helper.toNXGraph( )
    layout = helper.compute_layout( g )

    cvs = _globals.canvas_.canvas
    # Get canvas size 
    H, W = 800, 800

    for n in g.nodes( ):
        x, y = layout[ n ]
        x, y = x * H, y * W
        cvs.create_oval( (x,y), (x+10, y+10) )


class StatusBar(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd = 1, relief = SUNKEN, anchor = W)
        self.label.config( text = 'LABEL' )
        self.label.grid( row = 2, column = 0, sticky = 'ew' )

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

def update( ):
    _logger.info( '.' )


def main( parent ):
    """
    Added few frames. 
    
    First frame is editor frame. By default take half of horizontal screen and 
    80% of vertical screen.

    """

    w, h = parent.winfo_screenwidth( ), parent.winfo_screenheight( )
    editCanvas = MooseCanvas( parent ) 

    editCanvas.canvas.focus_set( )
    editCanvas.canvas.grid( row = 1, column =  3, rowspan = 100, columnspan = 100 )

    ## Add a statusbar 
    sbar = StatusBar( parent )
    sbar.grid( row = 101, column =  80, rowspan = 1, columnspan = 20 )
    sbar.bind( '<Button-1>', update )
    _globals.statusbar_ = sbar
    _globals.canvas_ = editCanvas 

if __name__ == '__main__':
    main()
