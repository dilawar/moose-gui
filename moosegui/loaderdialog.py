# -*- coding: utf-8 -*-
# Description: 
# Author: 
# Maintainer: 
# Created: Mon Feb 25 15:59:54 2013 (+0530)

import sys
import moose
import os
import posixpath
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog

class LoaderDialog(QFileDialog):
    # Update ftypes to include new file types 
    ftypes='All Supported Files (*.cspace *.g *.xml *.p);; CSPACE (*.cspace);; GENESIS (*.g);; GENESIS Prototype (*.p);; NeuroML/SBML (*.xml)'
    target_default = '' # The default target when loading a model
    def __init__(self, *args):
        self.modelpath = None
        super(LoaderDialog, self).__init__(*args)
        self.setNameFilter(self.tr(self.ftypes))
        self.setNameFilterDetailsVisible(True)
        self.setReadOnly(True)
        self.setFileMode(self.ExistingFile)
        # self.targetPanel = QtGui.QFrame()
        # self.targetLabel = QtGui.QLabel('Model name')
        # self.targetText = QtGui.QLineEdit(self.target_default)
        # form = QtGui.QFormLayout()
        # form.addRow(self.targetLabel, self.targetText)
        # self.modelChoiceBox = QtGui.QGroupBox('Model name')
        # self.replaceExistingButton = QtGui.QRadioButton('&Replace current model')
        # self.mergeExistingButton = QtGui.QRadioButton('&Keep current model')
        # self.replaceExistingButton.setChecked(True)
        # vbox = QtGui.QVBoxLayout()
        # vbox.addWidget(self.replaceExistingButton)
        # vbox.addWidget(self.mergeExistingButton)
        # self.modelChoiceBox.setLayout(vbox)
        # self.targetPanel.setLayout(form)
        # self.layout().addWidget(self.targetPanel)
        # self.layout().addWidget(self.modelChoiceBox)
        self.fileSelected.connect(self.fileSelectedSlot)
        
    def fileSelectedSlot(self, fpath):
        """On selecting a file, this function will cause the target location to change to:

        /model/filename_minus_extension

        """
        self.modelpath = os.path.splitext(os.path.basename(str(fpath)))[0]
                                  
    # def isReplace(self):
    #     return self.replaceExistingButton.isChecked()

    # def isMerge(self):
    #     return self.mergeExistingButton.isChecked()

    def getTargetPath(self):
        return self.modelpath


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    QtGui.qApp = app
    mw = LoaderDialog()
    mw.show()
    # mw.exec_()
    sys.exit(app.exec_())
        


# 
# fileloader.py ends here
