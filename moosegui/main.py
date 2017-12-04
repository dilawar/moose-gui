__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2016, Dilawar Singh"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys

try:
    import Tkinter as tk
except ImportError as e:
    import tkinter as tk

import os
import traceback 

import moosegui.menus as menus
import moosegui.canvas as canvas
import moosegui.toolbar  as toolbar
import moosegui._globals as _globals
from moosegui.MooseWindow import MooseWindow 

import logging
logging.basicConfig( level = logging.DEBUG )

class Catcher: 
    def __init__(self, func, subst, widget):
        self.func = func 
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        try:
            if self.subst:
                args = self.subst(args)
            return self.func( *args)
        except SystemExit as msg:
            logging.info( "Existing ... %s" % msg )
            raise SystemExit 
        except:
            traceback.print_exc(  )

tk.CallWrapper = Catcher 

def main( ):
    root = MooseWindow( )
    root.resizable( width = False, height = False )
    _globals.root_ = root

    # Handle all menues.
    menus.main(  root )

    # Add toolbar
    toolbar.main( root )

    # All frames
    canvas.main( root )
    tk.mainloop( )


if __name__ == '__main__':
    main()
