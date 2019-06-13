# -*- coding: utf-8 -*-
# Description:
# Author: Subhasis Ray
# Maintainer:
# Created: Wed Jun 30 11:18:34 2010 (+0530)

import sys
from collections import deque
import numpy as np

from PyQt5 import QtCore
from PyQt5.QtWidgets import QTextEdit, QWidget, QLineEdit
from PyQt5.QtWidgets import QVBoxLayout, QSizePolicy, QSplitter
from PyQt5.QtWidgets import QTableView, QDockWidget, QPushButton
from PyQt5.QtWidgets import QColorDialog, QMessageBox

import moose
from moosegui import defaults 
from moose.chemUtil.chemConnectUtil import getColor

#these fields will be ignored
extra_fields = [
    'this',
    'me',
    'parent',
    'path',
    'children',
    'linearSize',
    'objectDimensions',
    'lastDimension',
    'localNumField',
    'pathIndices',
    'msgOut',
    'msgIn',
    'diffConst',
    'speciesId',
    'Coordinates',
    'neighbors',
    'DiffusionArea',
    'DiffusionScaling',
    'x',
    'x0',
    'x1',
    'dx',
    'nx',
    'y',
    'y0',
    'y1',
    'dy',
    'ny',
    'z',
    'z0',
    'z1',
    'dz',
    'nz',
    'coords',
    'isToroid',
    'preserveNumEntries',
    # 'numKm',
    'numSubstrates',
    'concK1',
    'meshToSpace',
    'spaceToMesh',
    'surface',
    'method',
    'alwaysDiffuse',
    'numData',
    'numField',
    'valueFields',
    'sourceFields',
    'motorConst',
    'destFields',
    'dt',
    'tick',
    'idValue',
    'index',
    'fieldIndex'
]


class ObjectEditModel(QtCore.QAbstractTableModel):
    """Model class for editing MOOSE elements. This is not to be used
    directly, except that its undo and redo slots should be connected
    to by the GUI actions for the same.

    SIGNALS:

    objectNameChanged(PyQt_PyObject): when a moose object's name is
    changed, this signal is emitted with the object as argument. This
    can be captured by widgets that display the object name.

    dataChanged: emitted when any data is changed in the moose object

    """

    objectNameChanged = QtCore.pyqtSignal('PyQt_PyObject')
    dataChanged = QtCore.pyqtSignal(QtCore.QModelIndex, QtCore.QModelIndex)

    def __init__(self,
                 datain,
                 headerdata=['Field', 'Value'],
                 undolen=100,
                 parent=None,
                 *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.fieldFlags = {}
        self.fields = []
        self.mooseObject = datain
        self.headerdata = headerdata
        self.undoStack = deque(maxlen=undolen)
        self.redoStack = deque(maxlen=undolen)
        self.checkState_ = False

        for fieldName in self.mooseObject.getFieldNames('valueFinfo'):
            if fieldName in extra_fields:
                continue
            self.fields.append(fieldName)
        if (isinstance (self.mooseObject,moose.ChemCompt) or \
            isinstance(self.mooseObject,moose.ReacBase)  or \
            isinstance(moose.element(moose.element(self.mooseObject).parent),moose.EnzBase) \
           ):
            pass
        else:
            self.fields.append("Color")

        flag = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        self.fieldFlags[fieldName] = flag

        if (isinstance(self.mooseObject, moose.ReacBase)):
            self.fields.append("Kd")
        flag = QtCore.Qt.ItemIsEnabled
        self.fieldFlags[fieldName] = flag

    def rowCount(self, parent):
        return len(self.fields)

    def columnCount(self, parent):
        return len(self.headerdata)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid() or index.row() >= len(
                self.fields) or index.column() != 1:
            return False
        field = self.fields[index.row()]
        if (role == QtCore.Qt.CheckStateRole):
            if (index.column() == 1):
                self.checkState_ = value
                return True

        else:
            # convert Qt datastructure to Python string
            value = value.strip()
            if len(value) == 0:
                return False
            if field == "Notes":
                field = "notes"
                ann = moose.Annotator(self.mooseObject.path + '/info')
                oldValue = ann.getField(field)
                value = type(oldValue)(value)
                ann.setField(field, value)
                self.undoStack.append((index, oldValue))
            elif field == "vector":
                for ch in ['[', ']']:
                    if ch in value:
                        value = value.replace(ch, " ")
                value = value.replace(",", " ")
                valuelist = []
                if value.find(',') != -1:
                    valuelist = value.split(",")
                elif value.find(' ') != -1:
                    valuelist = value.split(" ")
                else:
                    valuelist = value
                self.mooseObject.setField(field, np.array(valuelist, dtype=np.float))
            else:
                oldValue = self.mooseObject.getField(field)
                if field != "isBuffered":
                    value = type(oldValue)(value)
                    self.mooseObject.setField(field, value)
                else:
                    if self.mooseObject.className == "ZombiePool" or self.mooseObject.className == "ZombieBufPool":
                        QMessageBox.warning(
                            None, 'Solver is set, Could not set the value',
                            '\n Unset the solver by clicking \n run widget -> Preferences -> Exponential Euler->Apply'
                        )
                    else:
                        if value.lower() in ("yes", "true", "t", "1"):
                            self.mooseObject.setField(field, True)
                        else:
                            self.mooseObject.setField(field, False)
                self.undoStack.append((index, oldValue))
            if field == 'name':
                self.emit(QtCore.SIGNAL('objectNameChanged(PyQt_PyObject)'),
                          self.mooseObject)
            return True

        self.dataChanged.emit(index, index)
        return True

    def data(self, index, role):
        ret = None
        field = self.fields[index.row()]
        if index.column() == 0 and role == QtCore.Qt.DisplayRole:
            try:
                ret = '%s (%s)' % (field, defaults.FIELD_UNITS[field])
            except KeyError:
                ret = field
            return ret

        if index.column() == 1:
            if role == QtCore.Qt.CheckStateRole:
                if (str(field) == "plot Conc") or (str(field) == "plot n"):
                    return self.checkState_
            elif (role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole):
                try:
                    if (str(field) == "Color"):
                        return QPushButton("Press Me!")
                    if (str(field) == "Kd"):
                        Kd = 0
                        if self.mooseObject.className == "ZombieReac" or self.mooseObject.className == "Reac":
                            if self.mooseObject.numSubstrates > 1 or self.mooseObject.numProducts > 1:
                                if self.mooseObject.Kf != 0:
                                    Kd = self.mooseObject.Kb / self.mooseObject.Kf
                        ret = QtCore.QVariant(QtCore.QString(str(Kd)))
                    if ((str(field) != "Notes") and (str(field) != "className")
                            and (str(field) != "Kd")):
                        ret = self.mooseObject.getField(str(field))
                        ret = QtCore.QString(str(ret))
                    elif (str(field) == "className"):
                        ret = self.mooseObject.getField(str(field))
                        if 'Zombie' in ret:
                            ret = ret.split('Zombie')[1]
                        ret = QtCore.QString(str(ret))
                    elif (str(field) == "Notes"):
                        astr = self.mooseObject.path + '/info'
                        mastr = moose.Annotator(astr)
                        ret = (mastr).getField(str('notes'))
                        ret = (QtCore.QString(str(ret)))
                except ValueError:
                    ret = None
        return ret

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return (self.headerdata[col])
        return ""


class ObjectEditView(QTableView):
    """View class for object editor.

    This class creates an instance of ObjectEditModel using the moose
    element passed as its first argument.

    undolen - specifies the size of the undo stack. By default set to
    OBJECT_EDIT_UNDO_LENGTH constant in defaults.py. Specify something smaller if
    large number of objects are likely to be edited.

    To enable undo/redo conect the corresponding actions from the gui
    to view.model().undo and view.model().redo slots.
    """

    def __init__(self,
                 mobject,
                 undolen=defaults.OBJECT_EDIT_UNDO_LENGTH,
                 parent=None):
        QTableView.__init__(self, parent)
        vh = self.verticalHeader()
        vh.setVisible(False)
        hh = self.horizontalHeader()
        hh.setStretchLastSection(True)
        self.setAlternatingRowColors(True)
        self.resizeColumnsToContents()
        self.setModel(ObjectEditModel(mobject, undolen=undolen))
        self.colorButton = QPushButton()
        self.colorDialog = QColorDialog()
        self.textEdit = QTextEdit()
        try:
            notesIndex = self.model().fields.index("Notes")
            self.setIndexWidget(self.model().index(notesIndex, 1),
                                self.textEdit)
            info = moose.Annotator(self.model().mooseObject.path + '/info')
            self.textEdit.setText(QtCore.QString(info.getField('notes')))
            self.setRowHeight(notesIndex, self.rowHeight(notesIndex) * 3)

            # self.colorDialog.colorSelected.connect(
            #     lambda color:
            #
            # self.setColor(getColor(self.model().mooseObject.path+'/info')[1])
        except:
            pass

        try:
            self.colorButton.clicked.connect(self.colorDialog.show)
            self.colorButton.setFocusPolicy(QtCore.Qt.NoFocus)
            self.colorDialog.colorSelected.connect(
                lambda color: self.colorButton.setStyleSheet(
                    "QPushButton {" + "background-color: {0}; color: {0};".
                    format(color.name()) + "}"))
            # FIXME:
            #  colorIndex = self.model().fields.index("Color")
            #  self.setIndexWidget(self.model().index(colorIndex, 1), self.colorButton)
            self.setColor(getColor(self.model().mooseObject.path + '/info')[1])
        except:
            pass
        print('Created view with %s' % (mobject))

    def setColor(self, color):
        self.colorButton.setStyleSheet(
            "QPushButton {" +
            "background-color: {0}; color: {0};".format(color) + "}")
        self.colorDialog.setCurrentColor(color)

    def dataChanged(self, tl, br):
        QTableView.dataChanged.emit(tl, br)
        self.viewport().update()


class ObjectEditDockWidget(QDockWidget):
    """A dock widget whose title is set by the current moose
    object. Allows switching the moose object. It stores the created
    view in a dict for future use.

    TODO possible performance issue: storing the views (along with
    their models) ensures the undo history for each object is
    retained. But without a limit on the number of views stored, it
    will be wasteful on memory.

    """
    objectNameChanged = QtCore.pyqtSignal('PyQt_PyObject')
    colorChanged = QtCore.pyqtSignal(object, object)

    def __init__(self, mobj='/', parent=None, flags=None):
        QDockWidget.__init__(self, parent=parent)
        mobj = moose.element(mobj)
        #self.view = view = ObjectEditView(mobj)
        self.view = view = ObjectEditView(mobj)
        self.view_dict = {mobj: view}
        base = QWidget()
        layout = QVBoxLayout()
        base.setLayout(layout)
        layout.addWidget(self.view)
        layout.addWidget(QTextEdit())
        self.setWidget(base)
        self.setWindowTitle('Edit: %s' % (mobj.path))
        # self.view.colorDialog.colorSelected.connect(self.colorChangedEmit)

    # def clearDict(self):
    #     self.view_dict.clear()

    def setObject(self, mobj):
        element = moose.element(mobj)
        try:
            view = self.view_dict[element]
        except KeyError:
            view = ObjectEditView(element)
            self.view_dict[element] = view
            view.model().objectNameChanged.connect(self.emitObjectNameChanged)
        view.colorDialog.colorSelected.connect(lambda color: self.colorChanged.
                                               emit(element, color))
        textEdit = QTextEdit()
        view.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        textEdit.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        base = QSplitter()
        base.setOrientation(QtCore.Qt.Vertical)
        layout = QVBoxLayout()
        layout.addWidget(view)  #, 0, 0)
        lineedit = QLineEdit("Notes:")
        lineedit.setReadOnly(True)
        layout.addWidget(lineedit)

        if (isinstance(mobj, moose.PoolBase)
                or isinstance(mobj, moose.ReacBase)
                or isinstance(mobj, moose.EnzBase)):
            info = moose.Annotator(mobj.path + '/info')
            textEdit.setText(QtCore.QString(info.getField('notes')))
            textEdit.textChanged.connect(lambda: info.setField(
                'notes', str(textEdit.toPlainText())))
            layout.addWidget(textEdit)  #,1,0)
        base.setLayout(layout)
        self.setWidget(base)
        self.setWindowTitle('Edit: %s' % (element.path))
        view.update()

    def emitObjectNameChanged(self, mobj):
        self.objectNameChanged.emit(mobj)
        self.setWindowTitle('Edit:%s' % (mobj.path))

    def undo(self):
        if len(self.undoStack) == 0:
            raise RuntimeWarning('No more undo information')
        index, oldvalue, = self.undoStack.pop()
        field = self.fields[index.row()]
        currentvalue = self.mooseObject.getField(field)
        oldvalue = type(currentvalue)(oldvalue)
        self.redoStack.append((index, str(currentvalue)))
        self.mooseObject.setField(field, oldvalue)
        if field == 'name':
            self.objectNameChanged.emit(self.mooseObject)
        self.dataChanged.emit(index, index)

def main():
    from PyQt5.QtWidgets import QApplication, QMainWindow, QAction
    app = QApplication(sys.argv)
    mainwin = QMainWindow()
    c = moose.Compartment("test")
    view = ObjectEditView(c, undolen=3)
    mainwin.setCentralWidget(view)
    action = QAction('Undo', mainwin)
    action.setShortcut('Ctrl+z')
    action.triggered.connect(view.model().undo)
    mainwin.menuBar().addAction(action)
    action = QAction('Redo', mainwin)
    action.setShortcut('Ctrl+y')
    action.triggered.connect(view.model().redo)
    mainwin.menuBar().addAction(action)
    mainwin.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
