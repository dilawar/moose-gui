"""MooseWindow.py: 

MooseWindow.

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

try:
    import Tkinter as tk
except ImportError as e:
    import tkinter as tk

class MooseWindow( tk.Tk ):
    """docstring for MooseWindow"""

    def __init__( self, title = 'MOOSE' ):
        tk.Tk.__init__( self )
        self.title( title )
        self.state = None
        self.attributes( '-zoomed', True )
        self.bind( "<F11>", self.toggle_fullscreen )
        self.bind( "<Escape>", self.end_fullscreen )


    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.attributes("-fullscreen", False)
        return "break"
