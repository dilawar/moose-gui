# -*- coding: utf-8 -*-
    
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
from setuptools import setup

demofiles = []

version_ = '0.1.0'

demoDir = os.path.join(os.path.dirname(__file__), 'demos')

for d, sd, fs in os.walk( demoDir ):
    for f in fs:
        filepath = os.path.join( d, f ).replace( demoDir, '' ) 
        demofiles.append( filepath )

setup(
    name = "moosegui",
    version = version_,
    description = "Graphical User Interface of MOOSE simulator",
    long_description = open( 'README.md' ).read(),
    packages = [ "moosegui", 'moosegui.plugins', "moosegui.demos"
        , 'suds', 'suds.bindings', 'suds.sax', 'suds.mx', 'suds.xsd'
        , 'suds.umx', 'suds.transport'
        ],
    package_dir = { 
        'moosegui' : 'moosegui'
        , 'moosegui.demos' : '.'
        , 'moosegui.plugins' : 'moosegui/plugins'
        , 'suds' : 'suds'
        },
    package_data = { 
        'moosegui' : [ 'icons/*', 'colormaps/*' ] + demofiles
        , 'moosegui.demos' : [ '*' ] + demofiles
        , 'moosegui.plugins' : [ 'datastore/*', 'list.txt' ]
        },
    author = open('AUTHOR').read(),
    maintainer = 'Dilawar Singh',
    maintainer_email = 'dilawars@ncbs.res.in',
    url = "http://github.com/BhallaLab/moose-gui",
    license='GPLv3',
    install_requires = [ 'pymoose', 'pyqt5' ],
    entry_points = {
        'console_scripts' : [
            'moosegui = moosegui.mgui:main'
            ],
        },
)
