"""
Entry point.

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

import menus
import canvas
import Tkinter as tk

import logging
from moosegui.MooseWindow import MooseWindow 

logging.basicConfig( level = logging.DEBUG )

def main( ):
    root = MooseWindow( )
    root.resizable( width = False, height = False )
    # root.minsize( 800, 800 )
    # Handle all menues.
    menus.main(  root )
    # All frames
    canvas.main( root )
    tk.mainloop( )

if __name__ == '__main__':
    main()
