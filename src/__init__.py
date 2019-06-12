from .mgui import main

# Hack. In python3, Qt4 does not have QString object. 
from PyQt5 import QtCore
try:
    from PyQt5.QtCore import QString
except ImportError:
    # we are using Python3 so QString is not defined. Also QVariant is a mapped
    # type.
    QtCore.QString = type("")
    # In python3, QtCore.QVariant is just a string
    QtCore.QVariant = type( "" )
