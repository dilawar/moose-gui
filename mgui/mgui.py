# Filename: mgui.py
# Description: Graphical user interface of MOOSE simulator.
# Author: Subhasis Ray, Harsha Rani, Dilawar Singh
# Maintainer:
# Created: Mon Nov 12 09:38:09 2012 (+0530)

__author__ = 'Subhasis Ray , HarshaRani, Aviral Goel, NCBS Bangalore'

import sys

from PyQt4 import QtGui, QtCore, Qt
from PyQt4 import Qt, QtCore, QtGui
import posixpath 

from . import config
from . import MWindow as MWindow

def main():
    # create the GUI application
    app = QtGui.QApplication(sys.argv)
    QtGui.qApp = app
    mWindow =  MWindow.MWindow()
    mWindow.setWindowState(QtCore.Qt.WindowMaximized)
    sys.excepthook = mWindow.handleException
    mWindow.show()
    config.settings[config.KEY_FIRSTTIME] = 'False' # string not boolean
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

#
# mgui.py ends here
