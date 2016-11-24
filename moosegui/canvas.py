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
import _globals

import logging
from moosegui.MooseCanvas import MooseCanvas
from Tkinter import *

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
    logging.info( '.' )


def main( parent ):
    """
    Added few frames. 
    
    First frame is editor frame. By default take half of horizontal screen and 
    80% of vertical screen.

    """

    w, h = parent.winfo_screenwidth( ), parent.winfo_screenheight( )
    editCanvas = MooseCanvas( parent ) 
    editCanvas.canvas.focus_set( )

    # Add a statusbar 
    sbar = StatusBar( parent )
    sbar.grid( row = 3, column =  1, sticky = 'ew' )

    sbar.bind( '<Button-1>', update )

    _globals.statusbar_ = sbar
    _globals.canvas_ = editCanvas 


if __name__ == '__main__':
    main()
