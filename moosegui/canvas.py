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

import logging
from moosegui.MooseCanvas import MooseCanvas

from Tkinter import *


def main( parent ):
    """
    Added few frames. 
    
    First frame is editor frame. By default take half of horizontal screen and 
    80% of vertical screen.

    """

    w, h = parent.winfo_screenwidth( ), parent.winfo_screenheight( )
    editCanvas = MooseCanvas( parent ) 
    editCanvas.pack( fill= 'both', expand = True )
    

if __name__ == '__main__':
    main()
