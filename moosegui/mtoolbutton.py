# -*- coding: utf-8 -*-

# Description: Subclass of QToolButton to allow drag and drop
# Author: 
# Maintainer: 
# Created: Fri Jun 14 14:24:11 2013 (+0530)

import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QToolButton, QToolBar, QMainWindow
from PyQt5.QtWidgets import QApplication, QTextBrowser
from PyQt5.Qt import Qt

import logging
logger_ = logging.getLogger('mtoolbutton')

class MToolButton(QToolButton):
    """
    QToolButton subclass with dragEvent reimplemented. It sends the
    text of the ToolButton as the mimedata.

    """
    def __init__(self, *args):
        QToolButton.__init__(self, *args)
        self.dragStartPosition = QtCore.QPoint(0,0)

    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.dragStartPosition = event.pos()

    def mouseMoveEvent(self, event):        
        if not (event.buttons() & Qt.LeftButton):
            return 
        if (event.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance():
            return
        drag = QtGui.QDrag(self)
        mimeData = QtCore.QMimeData()
        mimeData.setText(self.text())
        drag.setMimeData(mimeData)
        drag.exec_(Qt.CopyAction)


class MyWidget(QTextBrowser):
    """Class for testing the drag and drop ability of MToolButton"""
    def __init__(self, *args):
        QTextBrowser.__init__(self, *args)
        self.dropCount = 0
        self.setPlainText('Drops: %d' % (self.dropCount))
        self.setAcceptDrops(True)
        

    def dragEnterEvent(self, event):
        print(('2222', event.mimeData().text()))
        if event.mimeData().hasFormat('text/plain'):
            event.acceptProposedAction()
            print('3333 accepted ')

    def dragMoveEvent(self, event):
        """This must be reimplemented to accept the event in case of
        QTextBrowser. Not needed in QWidgets in general."""
        print('4444')
        event.acceptProposedAction()

    def dropEvent(self, event):
        print(('5555', event.mimeData().text()))
        self.dropCount += 1
        self.setPlainText('`%s` dropped: %d times' % (event.mimeData().text(), self.dropCount))
        event.acceptProposedAction()
        QTextBrowser.dropEvent(self, event)

def test_main():
    """Test main: see if drag and drop is working"""
    app = QApplication(sys.argv)
    mainwin = QMainWindow()
    mainwin.setWindowTitle('MTooButton')
    toolbar = QToolBar()
    mainwin.addToolBar(toolbar)
    button = MToolButton()
    button.setText('test')
    toolbar.addWidget(button)
    browser = MyWidget(mainwin)
    print((browser.acceptDrops()))
    mainwin.setCentralWidget(browser)
    mainwin.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    test_main()

# 
# mtoolbutton.py ends here
