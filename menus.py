"""menus.py: 

Menu management.

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
import logging

menuList_ = { 
        "Model" : [ ("New", "Ctrl+N", "Control-n" )
            , ("Open", "Ctrl+O", "Control-o")
            , ("Exit", "Ctrl+Q", "Control-q") ]
            }

def callback( action, parent ):
    logging.info( "Got action %s" % action )
    if action.lower() == 'exit':
        parent.quit( )
    else:
        logging.info( "TODO %s" % action )

def main( parent ):
    """
    This function adds required menues 

    """
    menu = tk.Menu( parent )
    for menuName in menuList_ :
        logging.info( "Adding menu %s" % menuName )
        thismenu = tk.Menu( menu )
        menu.add_cascade( label = menuName, menu = thismenu )
        for action in menuList_[ menuName ]:
            shortcut, underline = '', 0
            cmd = action[0]
            if len( action ) > 1:
                shortcut, underline = action[1], 1
                shortKey = "<%s>" % action[2]
                logging.debug( "Bidning key %s to action %s" % (shortKey, cmd))
                parent.bind( shortKey, lambda e, x=cmd:  callback(x, parent) )

            thismenu.add_command( label = action[0]
                , command = lambda x=cmd: callback(x, parent)
                , underline = underline
                , accelerator = shortcut
                )

    parent.config( menu = menu )

if __name__ == '__main__':
    main()
