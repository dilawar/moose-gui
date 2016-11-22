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
    packages = [ "moosegui"
        , "moosegui.mgui"
        , 'moosegui.mgui.plugins'
        , 'moosegui.suds' 
        ],
    package_dir = { 
        'moosegui' : '.'
        , 'moosegui.mgui' : 'mgui'
        , 'moosegui.mgui.plugins' : 'mgui/plugins'
        , 'moosegui.suds' : 'suds'
        },
    package_data = { 
        'moosegui' : [ 'moose', 'examples/*' ]
        , 'moosegui.mgui' : [ 'icons/*', 'colormaps/*', ]
        , 'moosegui.mgui.plugins' : [ 'datastore/*', 'list.txt' ]
        },
    author = open('AUTHOR').read(),
    maintainer = 'Dilawar Singh',
    maintainer_email = 'dilawars@ncbs.res.in',
    url = "http://github.com/BhallaLab/moose-gui",
    license='GPL',
)
