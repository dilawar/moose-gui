from .mgui import main

# Hack. In python3, Qt4 does not have QString object. 
from PyQt4 import QtCore
try:
    from PyQt4.QtCore import QString
except ImportError:
    # we are using Python3 so QString is not defined
    QtCore.QString = type("")

# QtCore is a mapped type i.e. 
try:
    from PyQt4.QtCore import QVariant
except Exception as e:
    QtCore.QVariant = type( "" )

