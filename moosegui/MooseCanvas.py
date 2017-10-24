"""MooseCanvas.py:


Here is my Canvas.

"""

__author__ = "Dilawar Singh"
__copyright__ = "Copyright 2016, Dilawar Singh"
__credits__ = ["NCBS Bangalore"]
__license__ = "GNU GPL"
__version__ = "1.0.0"
__maintainer__ = "Dilawar Singh"
__email__ = "dilawars@ncbs.res.in"
__status__ = "Development"

import sys
import random
import os

try:
    import Tkinter as tk
except ImportError as e:
    import tkinter as tk

import logging

class MooseCanvas( tk.Frame ):

    def __init__(self, root = None):


        self.canvas = tk.Canvas( root , width=800, height=800 )
        self.xsb = tk.Scrollbar( self.canvas,
            orient="horizontal", command=self.canvas.xview
            )

        self.ysb = tk.Scrollbar( self.canvas, orient="vertical",
            command=self.canvas.yview
            )
        self.canvas.configure(
            yscrollcommand=self.ysb.set,
            xscrollcommand=self.xsb.set
            )

        #self.xsb.grid(row=1, column=0, sticky="ew")
        #self.ysb.grid(row=0, column=1, sticky="ns")
        # self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=1)

        # This is what enables using the mouse:
        self.canvas.bind("<ButtonPress-1>", self.move_start)
        self.canvas.bind("<B1-Motion>", self.move_move)
        # linux scroll
        self.canvas.bind("<Button-4>", self.zoomerP)
        self.canvas.bind("<Button-5>", self.zoomerM)
        # windows scroll
        self.canvas.bind("<MouseWheel>", self.zoomer)
        # self.canvas.bind( "<Key>", self.keyboard )
        self.canvas.bind( "Move", self.keyboard )
        self.canvas.bind( "<Button-1>", self.mouseCallback )
        self.canvas.grid( row = 0, column = 0, sticky = 'news' )
        # self.canvas.pack( )

    # move
    def move_start(self, event):
        print( event )
        self.canvas.scan_mark(event.x, event.y)

    def move_move(self, event):
        print( event )
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    # windows zoom
    def zoomer(self, event):
        if (event.delta > 0):
            self.canvas.scale("all", event.x, event.y, 1.1, 1.1)
        elif (event.delta < 0):
            self.canvas.scale("all", event.x, event.y, 0.9, 0.9)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # linux zoom
    def zoomerP(self, event):
        self.canvas.scale("all", event.x, event.y, 1.1, 1.1)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def zoomerM(self, event):
        self.canvas.scale("all", event.x, event.y, 0.9, 0.9)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def mouseCallback(self, event, data = None ):
        print( event )
        #logging.info( 'Button pressed %s %s' % ( event.x, event.y ) )

    def keyboard(self, event, data = None ):
        print( event )
        #logging.info( 'Key pressed %s' % ( event.char ) )

if __name__ == "__main__":
    root = tk.Tk()
    a = MooseCanvas( root )
    # a.plot_random_rects( )
    a.pack(fill="both", expand=True)
    root.mainloop()
