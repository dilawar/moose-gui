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

import Tkinter as tk

class MooseCanvas( tk.Canvas ):

    def __init__(self,parent,**kwargs):
        tk.Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        return None 
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas 
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale( "all", 0, 0, wscale, hscale)

    def drawGrid( self, step ):
        for x in range(0, self.width, step):
            for y in range( 0, self.height, step):
                self.create_rectangle( (x, y, x+1, y+1) ) 


def main( parent ):
    """
    Added few frames. 
    
    First frame is editor frame. By default take half of horizontal screen and 
    80% of vertical screen.

    """

    w, h = parent.winfo_screenwidth( ), parent.winfo_screenheight( )
    editCanvas = MooseCanvas( parent )
    editCanvas.drawGrid( 10 )
    editCanvas.pack( fill=tk.BOTH, expand=tk.YES )
    logging.debug( "Size of edit canvas %s" % editCanvas.winfo_geometry( ) )
    

if __name__ == '__main__':
    main()
