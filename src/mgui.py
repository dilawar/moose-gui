# Filename: moosegui.py
# Description: Graphical user interface of MOOSE simulator.
# Author: Subhasis Ray, Harsha Rani, Dilawar Singh
# Maintainer:
# Created: Mon Nov 12 09:38:09 2012 (+0530)

__author__ = 'Subhasis Ray , HarshaRani, Aviral Goel, NCBS Bangalore'

import sys
import signal

from PyQt4 import QtGui, QtCore, Qt
from PyQt4 import Qt, QtCore, QtGui
import posixpath 

from moosegui import config
from moosegui import MWindow as MWindow

app_ = None

def signal_handler( *args  ):
    global app_
    sys.stderr.write( '\r' )
    sys.exit( app_.exec_() )

def main():
    # create the GUI application
    global app_
    app_ = QtGui.QApplication(sys.argv)
    signal.signal( signal.SIGINT, signal_handler )
    QtGui.qApp = app_
    mWindow =  MWindow.MWindow()
    mWindow.setWindowState(QtCore.Qt.WindowMaximized)
    sys.excepthook = mWindow.handleException
    mWindow.show()
    # config.settings[config.KEY_FIRSTTIME] = 'False'
    sys.exit( app_.exec_() )

if __name__ == '__main__':
    main()

#
# moosegui.py ends here
