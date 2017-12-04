"""menus.py: 
Menu management.

"""

from __future__ import absolute_import, division


__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2016, Dilawar Singh"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import functools 

PY_MAJOR = int( sys.version_info.major )
if PY_MAJOR == 2:
    import Tkinter as tk
    import tkFileDialog as tkfd
else:
    import tkinter as tk
    import tkinter.filedialog as tkfg


import os
import logging
from moosegui.config import _logger
import moosegui.canvas as canvas
import moosegui.GuiAction as act

menus_ = [ 'File', 'Insert' ]
menu_dict_ = { 
        "File" : [ ("New Model", "Ctrl+N", "Control-n" )
            , ("Load Model", "Ctrl+O", "Control-o")
            , ("Exit", "Ctrl+Q", "Control-q") ]
        , "Insert" : [ ( "CubeMesh", )
            , ( "CylMesh" , )
            , ( "Pool" , )
            , ( "BufPool", )
            , ( "Reac" , ) ]
        }

def callback( action, parent, data=None ):
    """Call function on Menu
    """
    logging.info( "Got action %s" % str(action) )
    action = action[0]
    if action.lower() == 'exit':
        raise SystemExit( "Exit command" )
    elif action == "Load Model":
        modelFile = tkfd.askopenfilename( parent = parent )
        logging.info( "Loading model %s" % modelFile )
        act.loadModel( modelFile )
    else:
        logging.info( "TODO %s" % action )


def main( parent ):
    """
    This function adds required menues. All action are handled in callback
    function.
    """
    global menu_dict_
    menu = tk.Menu( parent )
    for menuName in menus_ :
        logging.info( "Adding menu %s" % menuName )
        thismenu = tk.Menu( menu )
        menu.add_cascade( label = menuName, menu = thismenu )
        for action in menu_dict_[ menuName ]:
            shortcut, underline = '', 0
            if len( action ) > 1:
                shortcut, underline = action[1], 1
                shortKey = "<%s>" % action[2]
                parent.bind( shortKey, functools.partial( callback, action, parent) )

            thismenu.add_command( label = action[0]
                , command = functools.partial( callback, action, parent  )
                , underline = underline
                , accelerator = shortcut
                )

    parent.config( menu = menu )

if __name__ == '__main__':
    main()
