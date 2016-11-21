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

with open("README.md") as f:
    readme = f.read()

setup(
    name = "moose-gui",
    version = "1.0.0",
    description = "Graphical User Interface of MOOSE simulator",
    long_description = readme,
    packages = [ "mgui", 'mgui.plugins', 'mgui.colormaps', 'suds' ],
    package_dir = { 'mgui' : 'mgui'
        , 'suds' : 'suds'
        , 'mgui.plugins' : 'mgui/plugins'
        , 'mgui.colormaps' : 'mgui/colormaps'
        },
    package_data = { 'mgui' : [ 'icons/*', 'colormaps/*', '../examples/*' ] },
    author = "Harsha Rani",
    author_email = "hrani@ncbs.res.in",
    maintainer = 'Dilawar Singh',
    maintainer_email = 'dilawars@ncbs.res.in',
    url = "http://github.com/BhallaLab/moose-gui",
    license='GPL',
)
