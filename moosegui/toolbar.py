"""toolbar.py:

Add toolbar

"""

__author__ = "Me"
__copyright__ = "Copyright 2016, Me"
__credits__ = ["NCBS Bangalore"]
__license__ = "GNU GPL"
__version__ = "1.0.0"
__maintainer__ = "Me"
__email__ = ""
__status__ = "Development"

import sys
import os
import Tkinter as tk
import ttk
import _globals

import logging

from PIL import Image, ImageTk

# After each section, put a separator.
toolbar = [['Cylinder', 'Cube'], ['Pool', 'BufPool'], ['Move', 'Exit']]


def iconRead(name):
    imgFilePath = os.path.join('icons', '%s.png' % name)
    img = Image.open(imgFilePath)
    img = img.resize((20, 20), Image.ANTIALIAS)
    # return tk.PhotoImage( file = imgFilePath )
    return ImageTk.PhotoImage(img)

def btnCallback( btn ):
    if btn.lower( ) == 'exit':
        raise SystemExit
    if btn.lower( ) == 'cube':
        logging.debug( "Drawing cube and changing cursor " )
        _globals.root_.config( cursor = 'wait' )
    print( btn )

class ToolBar(tk.Frame):

    def __init__(self, root):
        logging.info("Creating a toolbar")
        tk.Frame.__init__(self, root )
        i = 0
        for tools in toolbar:
            for tool in tools:
                i += 1
                btnImg = iconRead(tool)
                btn = tk.Button( self
                        , image=btnImg
                        , command = lambda x = tool : btnCallback( x )
                        )
                btn.image = btnImg
                btn.grid(row=i, column=0)
            i += 1
            sep = ttk.Separator( root , orient = tk.VERTICAL )
            sep.grid(row=i, column=0 )


def main(parent):
    toolbar = ToolBar( parent ) 
    toolbar.grid( row = 1, column = 0, sticky = 'ns' )
    _globals.toolbar_ = toolbar
