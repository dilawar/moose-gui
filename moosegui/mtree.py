# -*- coding: utf-8 -*-

# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Tue May 14 11:51:35 2013 (+0530)

from PyQt5 import QtCore
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QTreeWidgetItem, QTreeWidget

import moose

class MooseTreeModel(QtCore.QAbstractItemModel):
    """Tree model for the MOOSE element tree.
    
    This is not going to work as the MOOSE tree nodes are
    inhomogeneous. The parent of a node is an melement, but the
    children of an melement are vec objects.

    Qt can handle only homogeneous tere nodes.
    """
    def __init__(self, *args):
        super(MooseTreeModel, self).__init__(*args)
        self.rootItem = moose.element('/')

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        childItem = parentItem.children[row]
        if childItem.path == '/':
            return QtCore.QModelIndex()
        return self.createIndex(row, column, childItem)

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        childItem = index.internalPointer()
        parentItem = childItem.parent()
        if parentItem == self.rootItem:
            return QtCore.QModelIndex()
        return self.createIndex(parentItem.parent.children.index(parentItem), parentItem.getDataIndex(), parentItem)

    def rowCount(self, parent):
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        ret = len(parentItem.children)
        return ret

    def columnCount(self, parent):
        if parent.isValid():
            return len(parent.internalPointer())
        ret = len(self.rootItem)
        return ret

    def data(self, index, role):
        if not index.isValid():
            return None
        item = index.internalPointer()
        return QtCore.QVariant(item[index.column()].name)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:  
            return QtCore.QVariant('Model Tree')
        return None

    def flags(self, index):
         if not index.isValid():
             return QtCore.Qt.NoItemFlags
         return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        
    
class MooseTreeItem(QTreeWidgetItem):
    def __init__(self, *args):
        QTreeWidgetItem.__init__(self, *args)
        self.mobj = None

    def setObject(self, element):
        self.mobj = moose.element(element)
        self.setText(0, self.mobj.path.rpartition('/')[-1])
        self.setText(1, self.mobj.className)

    def updateSlot(self):
        self.setText(0, self.mobj.name)


class MooseTreeWidget(QTreeWidget):
    """Widget for displaying MOOSE model tree.

    """
    # Author: subhasis ray
    #
    # Created: Tue Jun 23 18:54:14 2009 (+0530)
    #
    # Updated for moose 2 and multiscale GUI: 2012-12-06
    # Further updated for pymoose2: Tue May 14 14:35:35 IST 2013

    # Ignored are elements to be ignored when building the tree
    ignored = ['/Msgs', '/classes']
    elementInserted = QtCore.pyqtSignal('PyQt_PyObject')
    def __init__(self, *args):
        """A tree widget to display model tree in MOOSE.

        Members:
        
        rootElement: melement
                    root element for the tree.

        SIGNAL:

        elementInserted(melement) emitted when a new element is inserted.

        """
        QTreeWidget.__init__(self, *args)
        self.header().hide()
        self.rootElement = moose.element('/')
        self.odict = {}
        self.recreateTree()        

    def setupTree(self, obj, parent, odict):
        """Recursively setup the tree items.
        
        Parameters
        ----------
        obj: melement
        object to be associated with the tree item created.

        parent: MooseTreeItem
        parent item of the current tree item
                
        odict: dict
        dictionary to store melement to tree widget item mapping.
        
        """
        for ii in MooseTreeWidget.ignored:
            if obj.path.startswith(ii):
                return None
        item = MooseTreeItem(parent)
        item.setObject(obj)
        odict[obj] = item
        # TODO: check and verify that this still works with synapses -
        # there have been change in API. - Subha, Fri Sep 19 19:04:35 IST 2014

        for child in obj.children:    
            ch = child
            if child.name in obj.getFieldNames('fieldElementFinfo'):
                ch = obj.getField(child.name)
            for elm in ch:
                self.setupTree(moose.element(elm), item, odict)      
        return item

    def recreateTree(self, root=None):        
        """Clears the current tree and recreates the tree. If root is not
        specified it uses the current `root` otherwise replaces the
        rootElement with specified root element.
        
        Parameter
        ---------
        root: str or melement or vec 
              New root element of the tree. Use current rootElement if `None`
        """        
        self.clear()
        self.odict.clear()
        if root is not None:
            self.rootElement = moose.element(root)
        self.setupTree(self.rootElement, self, self.odict)
        self.setCurrentItem(self.rootElement)
        self.expandToDepth(0)

    def insertElementSlot(self, class_name):
        """Creates an instance of the class class_name and inserts it
        under currently selected element in the model tree."""
        # print 'Inserting element ...', class_name
        current = self.currentItem()
        print(('CLASS NAME:', class_name))
        self.insertChildElement(current, class_name)

    def insertChildElement(self, item, class_name, name=''):
        if len(name) == 0:
            name = class_name
        path = '%s/%s' % (item.mobj.path, str(name))
        mclassname = 'moose.%s' % (str(class_name))
        mclass = eval(mclassname)
        obj = mclass(path)
        newitem = MooseTreeItem(item)
        newitem.setObject(obj)
        item.addChild(newitem)
        self.odict[obj] = newitem
        self.elementInserted.emit(obj)
        

    def setCurrentItem(self, item):
        """Overloaded version of QTreeWidget.setCurrentItem

        - adds ability to set item by corresponding moose object.
        """
        if isinstance(item, QTreeWidgetItem):
            QTreeWidget.setCurrentItem(self, item)
            return        
        mobj = moose.element(item)
        QTreeWidget.setCurrentItem(self, self.odict[mobj])

    def updateItemSlot(self, element):
        self.odict[element].updateSlot()
        
def main():
    """
    Test main: load a model and display the tree for it
    """
    import sys
    import os
    sdir = os.path.dirname(__file__)
    from PyQt5.QtWidgets import QApplication, QMainWindow
    #  model = moose.Neutral('/model')
    modelfile = os.path.join(sdir, '../data/Kholodenko.g')
    moose.loadModel(modelfile, '/model')
    app = QApplication(sys.argv)
    mainwin = QMainWindow()
    mainwin.setWindowTitle('Model tree test')
    tree = MooseTreeWidget()
    tree.recreateTree(root='/model/')
    mainwin.setCentralWidget(tree)
    mainwin.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
