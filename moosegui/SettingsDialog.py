# -*- coding: utf-8 -*-

"""
Dialog for settings. Currently only plot settings are supported
"""

__author__      =   "Aviral Goel"
__credits__     =   ["Upi Lab"]
__license__     =   "GPL3"
__version__     =   "1.0.0"
__maintainer__  =   "Aviral Goel"
__email__       =   "goel.aviral@gmail.com"
__status__      =   "Development"


import sys
from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QTabWidget

class SettingsWidget(QTabWidget):
    def __init__( self
                , plotFieldMap
                , parent        = None
                ):
        super(SettingsWidget, self).__init__(parent)

        self.plotFieldMap = plotFieldMap

        self.addTab(self.plotSettingsPage(),"Plot Settings");
        self.addTab(self.plotSettingsPage(),"Other Settings");

    def plotSettingsPage(self):
        page = QWidget()
        layout = QGridLayout()
        page.setLayout(layout)
        index = 0
        for key, values in list(self.plotFieldMap.items()) :
            label = QLabel(key, page)
            combo = QComboBox(page)
            for value in values:
                combo.addItem(value)
            layout.addWidget(label,index,0, Qt.Qt.AlignRight)
            layout.addWidget(combo,index,1, Qt.Qt.AlignLeft)
            index += 1
        return page

def main():
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = SettingsWidget({
        'LeakyIaF':['Vm'],
        'Compartment':['Vm','Im'],
        'HHChannel':['Ik','Gk'],
        'ZombiePool':['n','conc'],
        'ZombieBufPool':['n','conc'],
        'HHChannel2D':['Ik','Gk'],
        'CaConc':['Ca']
        }
        )
    dialog.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
