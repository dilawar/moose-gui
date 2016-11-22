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
import Tkinter as tk
import menus
import logging
logging.basicConfig( level = logging.DEBUG )

def main( ):
    root = tk.Tk( )
    # Handle all menues.
    menus.main(  root )
    tk.mainloop( )

if __name__ == '__main__':
    main()
