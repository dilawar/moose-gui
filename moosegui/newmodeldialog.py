# -*- coding: utf-8 -*-
 
import re

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QDialogButtonBox, QDialog
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit
from PyQt5.QtWidgets import QHBoxLayout

class DialogWidget(QDialog):
    def __init__(self,parent=None):
        QWidget.__init__(self, parent)
        self.warning = None
        self._currentRadioButton ="kkit"
        self.layout = QGridLayout()
        self.modelPathLabel = QLabel('Model Name')
        self.modelPathEdit =  QLineEdit('')
        self.layout.addWidget(self.modelPathLabel, 0, 0)
        self.layout.addWidget(self.modelPathEdit, 0, 1,1,1)
        self.hbox = QHBoxLayout()
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.validateAccept)
        self.hbox.addWidget(self.buttonBox,1)
        self.buttonBox1 = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.buttonBox1.rejected.connect(self.Cancel)
        self.hbox.addWidget(self.buttonBox1,0)
        self.layout.addLayout(self.hbox,1,1)
        self.setLayout(self.layout)

    def Cancel (self):
        self.close()

    def validateAccept(self):
        text = str(self.modelPathEdit.text())
        self.layout.removeWidget(self.warning)
        #replace / to _
        text = text.replace('/','_')

        #print(self.layout.widgets())
        if len(text) == 0:
            self.warning = QtGui.QLabel("Model name cannot be empty!")
            self.layout.addWidget(self.warning, 1, 0, 1, -1)
        elif not re.match("^[a-zA-Z]+.*",text):
            self.warning = QtGui.QLabel("Start special characters not allowed!")
            self.layout.addWidget(self.warning, 1, 0, 1, -1)
        else:
            self.accept()
        return False

    def getcurrentRadioButton(self):
        return self._currentRadioButton

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    widget = DialogWidget()
    widget.setWindowTitle('New Model')
    widget.setMinimumSize(400, 200)
    widget.show()
    app.exec_()


