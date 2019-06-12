# Filename: moosegui.py
# Description: Graphical user interface of MOOSE simulator.
# Author: Subhasis Ray, Harsha Rani, Dilawar Singh
# Maintainer:
# Created: Mon Nov 12 09:38:09 2012 (+0530)

__author__ = 'Subhasis Ray , HarshaRani, Aviral Goel, NCBS Bangalore'

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtGui, QtCore
from moosegui import config
from moosegui import MWindow as MWindow

app_ = None

def main():
    # create the GUI application
    global app_
    app_ = QApplication(sys.argv)
    QtGui.qApp = app_
    mWindow =  MWindow.MWindow()
    mWindow.setWindowState(QtCore.Qt.WindowMaximized)
    sys.excepthook = mWindow.handleException
    mWindow.show()
    sys.exit( app_.exec_() )

if __name__ == '__main__':
    main()

