"""GenericTypes

This class fixes the pytho2 and python3 related issues with PyQt4

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

from PyQt4 import QtCore

if sys.version_info >= (3, 0):

    class QVariant(str):
        """docstring for QVariant"""
        def __init__(self, val):
            super(QVariant, self).__init__()
            self.val = val

        def toString( self ):
            return "%s" % self.val

else:
    QVariant = QtCore.QVariant

