"""mgui.py: 

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
logging.basicConfig( level = logging.DEBUG )

def main( ):
    root = tk.Tk( )
    root.resizable( width = False, height = False )
    # Handle all menues.
    menus.main(  root )
    # All frames
    canvas.main( root )
    tk.mainloop( )

if __name__ == '__main__':
    main()
