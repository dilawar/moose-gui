"""setup.py: 

Install script of moose-gui project.

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
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from distutils.core import setup

setup(
    name = "moosegui",
    version = "1.0.0",
    description = "Graphical User Interface of MOOSE simulator",
    long_description = open( 'README.md' ).read(),
    packages = [ 
        "moosegui", 'moosegui.plugins' , 'moosegui.demos'
        , 'moosegui.suds', 'moosegui.suds.bindings'
        , 'moosegui.suds.transport', 'moosegui.suds.mx'
        , 'moosegui.suds.umx', 'moosegui.suds.xsd', 'moosegui.suds.sax'
        ],
    package_dir = { 
        'moosegui' : 'src'
        , 'moosegui.demos' : 'demos'
        , 'moosegui.suds' : 'external/suds'
        },
    package_data = { 
        'moosegui' : [ '../moose', 'icons/*', 'colormaps/*' ]
        , 'moosegui.demos' : [ './*' ]
        , 'moosegui.plugins' : [ 'datastore/*', 'list.txt' ]
        },
    author = open('AUTHOR').read(),
    maintainer = 'Dilawar Singh',
    maintainer_email = 'dilawars@ncbs.res.in',
    url = "http://github.com/BhallaLab/moose-gui",
    license='GPL',
)
