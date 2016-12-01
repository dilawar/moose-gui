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
import sys
from distutils.core import setup

setup(
    name = "moosegui",
    version = "1.0.0",
    description = "Graphical User Interface of MOOSE simulator",
    long_description = open( 'README.md' ).read(),
    packages = [ "moosegui", 'moosegui.plugins', "moosegui.demos"
        , 'suds', 'suds.bindings', 'suds.sax', 'suds.mx', 'suds.xsd'
        , 'suds.umx', 'suds.transport'
        ],
    package_dir = { 
        'moosegui' : 'src'
        , 'moosegui.demos' : 'demos'
        , 'moosegui.plugins' : 'src/plugins'
        , 'suds' : 'suds'
        },
    package_data = { 
        'moosegui' : [ 'icons/*', 'colormaps/*' ]
        , 'moosegui.demos' : [ './*' ]
        , 'moosegui.plugins' : [ 'datastore/*', 'list.txt' ]
        },
    author = open('AUTHOR').read(),
    maintainer = 'Dilawar Singh',
    maintainer_email = 'dilawars@ncbs.res.in',
    url = "http://github.com/BhallaLab/moose-gui",
    license='GPL',
)
