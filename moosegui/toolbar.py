"""toolbar.py: 

Add toolbar

"""
    
__author__           = "Me"
__copyright__        = "Copyright 2016, Me"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Me"
__email__            = ""
__status__           = "Development"

import sys
import os
import Tkinter as tk
import logging
from PIL import Image, ImageTk

toolbar = [ 'Cylinder', 'Cube', 'Pool', 'BufPool', 'Move', 'Exit' ]

def iconRead( name ):
    imgFilePath = os.path.join( 'icons', '%s.png' % name )
    img = Image.open( imgFilePath )
    img = img.resize( (20, 20), Image.ANTIALIAS )
    # return tk.PhotoImage( file = imgFilePath )
    return ImageTk.PhotoImage( img )

class ToolBar( tk.Frame ):

    def __init__( self, root ):
        logging.info( "Creating a toolbar" )
        tk.Frame.__init__( self, root, bd = 1, relief = tk.RAISED )
        for i, tool in enumerate( toolbar ):
            btnImg = iconRead( tool )
            btn = tk.Button( self, image = btnImg, relief = tk.FLAT )
            btn.image = btnImg
            btn.grid( row = 0, column = i )


def main( parent ):
    toolbar = ToolBar( parent ) # toolbarFrame )
    toolbar.pack( side = 'top', fill = 'x', expand = True )
