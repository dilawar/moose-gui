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
        "Model" : [ "New", "Open", "Exit" ]
        }

def callback( action, parent ):
    logging.info( "Got action %s" % action )
    if action.lower() == 'exit':
        parent.quit( )

def main( parent ):
    """
    This function adds required menues 

    """
    menu = tk.Menu( parent )
    parent.config( menu = menu )
    for menuName in menuList_ :
        logging.info( "Adding menu %s" % menuName )
        thismenu = tk.Menu( menu )
        menu.add_cascade( label = menuName, menu = thismenu )
        for action in menuList_[ menuName ]:
            thismenu.add_command( label = action 
                    , command = lambda action=action: callback(action, parent)
                    )

if __name__ == '__main__':
    main()
