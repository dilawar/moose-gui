# -*- coding: utf-8 -*-

__author__ = "HarshaRani"
__credits__ = ["Upi Lab"]
__license__ = "GPL3"
__version__ = "1.0.0"
__maintainer__ = "HarshaRani"
__email__ = "hrani@ncbs.res.in"
__status__ = "Development"
__updated__ = "Feb 22 2019"

import os
import sys
import re
import math

from PyQt5.QtWidgets import QApplication

# For testing: QApplication must be created before any other widget.
if __name__ == "__main__":
    app = QApplication(sys.argv)

from PyQt5 import QtGui, QtCore, Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QFileDialog
from PyQt5.QtWidgets import QMenu, QAction, QGraphicsScene
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtGui import QColor

# moosegui
from moosegui import RunWidget
from moosegui import mplugin, config
from moosegui.mtoolbutton import MToolButton
from moosegui.plugins.default import MoosePlugin, MooseEditorView, RunView
from moosegui.plugins import kkitUtil, kkitOrdinateUtil
from moosegui.plugins import kkitQGraphics
from moosegui.plugins import kkitViewcontrol
from moosegui.PlotWidgetContainer import PlotWidgetContainer

# moose
import moose

# Logging
import logging
logger_ = logging.getLogger('gui.plugins.kkit')

class KkitPlugin(MoosePlugin):
    """
    Default plugin for MOOSE GUI
    """

    def __init__(self, *args):
        MoosePlugin.__init__(self, *args)
        self.view = None
        self.fileinsertMenu = QMenu('&File')

        if not hasattr(self, 'SaveModelAction'):
            #self.fileinsertMenu.addSeparator()
            self.saveModelAction = QAction('Save', self)
            self.saveModelAction.setShortcut("Ctrl+S")
            self.saveModelAction.triggered.connect(self.SaveModelDialogSlot)
            self.fileinsertMenu.addAction(self.saveModelAction)

        self._menus.append(self.fileinsertMenu)
        self.getEditorView()

    def SaveModelDialogSlot(self):

        dirpath = ""
        if not dirpath:
            dirpath = os.path.expanduser("~")
        filters = {'SBML(*.xml)': 'SBML', 'Genesis(*.g)': 'Genesis'}
        filename, filter_ = QFileDialog.getSaveFileNameAndFilter(
            None, 'Save File', dirpath, "SBML(*.xml);;Genesis(*.g)")
        if str(filename).rfind('.') != -1:
            filename = filename[:str(filename).rfind('.')]

        if filename:
            filename = filename
            if filters[str(filter_)] == 'SBML':
                self.coOrdinates = {}
                self.plugin = KkitEditorView(self).getCentralWidget().plugin
                self.coOrdinates = KkitEditorView(
                    self).getCentralWidget().getsceneCord()
                #writeerror = moose.writeSBML(self.modelRoot,str(filename),self.coOrdinates)
                writeerror = -2
                writtentofile = "/test.xml"
                writeerror, consistencyMessages, writtentofile = moose.SBML.mooseWriteSBML(
                    self.modelRoot, str(filename), self.coOrdinates)
                if writeerror == -2:
                    QtGui.QMessageBox.warning(None, 'Could not save the Model',
                                              consistencyMessages)
                elif writeerror == -1:
                    QtGui.QMessageBox.warning(
                        None, 'Could not save the Model',
                        '\n This model is not valid SBML Model, failed in the consistency check'
                    )
                elif writeerror == 1:
                    QtGui.QMessageBox.information(
                        None, 'Saved the Model',
                        '\n File saved to \'{filename}\''.format(
                            filename=filename + '.xml'), QtGui.QMessageBox.Ok)
                elif writeerror == 0:
                    QtGui.QMessageBox.information(
                        None, 'Could not save the Model',
                        '\nThe filename could not be opened for writing')

            elif filters[str(filter_)] == 'Genesis':
                moose.Annotator(self.modelRoot + '/info')
                self.coOrdinates = {}
                ss = KkitEditorView(self).getCentralWidget().mooseId_GObj
                for k, v in ss.items():
                    if moose.exists(moose.element(k).path + '/info'):
                        annoInfo = moose.Annotator(k.path + '/info')
                        x = annoInfo.x * 10
                        y = -annoInfo.y * 10
                        self.coOrdinates[k] = {'x': x, 'y': y}

                error, written = moose.mooseWriteKkit(self.modelRoot,
                                                      str(filename),
                                                      self.coOrdinates)
                if written == False:
                    QtGui.QMessageBox.information(None,
                                                  'Could not save the Model',
                                                  '\nCheck the file')
                else:
                    if error == "":
                        QtGui.QMessageBox.information(
                            None, 'Saved the Model',
                            '\n File saved to \'{filename}\''.format(
                                filename=filename + '.g'),
                            QtGui.QMessageBox.Ok)
                    else:
                        QtGui.QMessageBox.information(
                            None, 'Saved the Model but ...',
                            '{error}'.format(error=error),
                            QtGui.QMessageBox.Ok)

    def getPreviousPlugin(self):
        return None

    def getNextPlugin(self):
        return None

    def getAdjacentPlugins(self):
        return []

    def getViews(self):
        return self._views

    def getCurrentView(self):
        return self.currentView

    def getEditorView(self):
        if not hasattr(self, 'editorView'):
            self.editorView = KkitEditorView(self)
            self.editorView.getCentralWidget().editObject.connect(
                self.mainWindow.objectEditSlot)
            self.currentView = self.editorView
        return self.editorView

    def getRunView(self):
        if self.view is None:
            self.view = AnotherKkitRunView(self.modelRoot, self)
        return self.view

        if self.view is not None:
            return AnotherKkitRunView(self.modelRoot, self)
        if self.view is not None:
            return self.view
        self.view = RunView(self.modelRoot, self)
        graphView = self.view._centralWidget
        graphView.setDataRoot(self.modelRoot)
        graphView.plotAllData()
        self._kkitWidget = self.view.plugin.getEditorView().getCentralWidget()
        self.runView = KkitRunView(self, self._kkitWidget)
        self.currentRunView = self.ruAnotherKkitRunViewnView.getCentralWidget()
        graphView.layout().addWidget(self.currentRunView, 0, 0, 2, 1)
        return self.view


class AnotherKkitRunView(RunView):
    def __init__(self, modelRoot, plugin, *args):
        RunView.__init__(self, modelRoot, plugin, *args)
        self.modelRoot = modelRoot
        self.plugin = plugin
        self.schedular = None

    def setSolverFromSettings(self, chemicalSettings):
        self.setSolver(self.modelRoot,
                       chemicalSettings["simulation"]["solver"])

    def createCentralWidget(self):
        self._centralWidget = RunWidget.RunWidget(self.modelRoot)
        self.kkitRunView = KkitRunView(self.plugin)
        self.plotWidgetContainer = PlotWidgetContainer(self.modelRoot)
        self._centralWidget.setChildWidget(self.kkitRunView.getCentralWidget(),
                                           False, 0, 0, 1, 1)
        self._centralWidget.setChildWidget(self.plotWidgetContainer, False, 0,
                                           1, 1, 2)
        self._centralWidget.setPlotWidgetContainer(self.plotWidgetContainer)
        self.schedular = self.getSchedulingDockWidget().widget()
        self.schedular.runner.simulationProgressed.connect(
            self.kkitRunView.getCentralWidget().updateValue)
        self.schedular.runner.simulationProgressed.connect(
            self.kkitRunView.getCentralWidget().changeBgSize)
        self.schedular.runner.simulationReset.connect(
            self.kkitRunView.getCentralWidget().resetColor)
        self.schedular.preferences.applyChemicalSettings.connect(
            self.setSolverFromSettings)
        compt = moose.wildcardFind(self.modelRoot + '/##[ISA=ChemCompt]')
        ann = moose.Annotator(self.modelRoot + '/info')
        if compt:
            self.runTime = moose.element(ann).runtime
            solver = moose.element(ann).solver
        else:
            self.runTime = 100
            solver = "gsl"
        self.schedular.simulationRuntime.setText(str(self.runTime))
        chemprefs = self.schedular.preferences.getChemicalPreferences()
        c = moose.Clock('/clock')
        self.simulationdt = c.tickDt[11]
        self.plotdt = c.tickDt[18]
        chemprefs["simulation"]["simulation-dt"] = self.simulationdt
        chemprefs["simulation"]["plot-update-interval"] = self.plotdt
        chemprefs["simulation"]["gui-update-interval"] = 2 * self.plotdt
        chemprefs["simulation"]["solver"] = "Runge Kutta"
        if solver == "gsl":
            chemprefs["simulation"]["solver"] = "Runge Kutta"
        elif solver == "gssa":
            chemprefs["simulation"]["solver"] = "Gillespie"
        elif solver == "ee" or solver == " ":
            chemprefs["simulation"]["solver"] = "Exponential Euler"
        else:
            chemprefs["simulation"]["solver"] = "Runge Kutta"
        self.schedular.preferences.setChemicalPreferences()
        return self._centralWidget

    def setSolver(self, modelRoot, solver=None):
        if solver == None:
            reinit = moose.mooseAddChemSolver(
                modelRoot,
                self.getSchedulingDockWidget().widget().solver)
            if reinit:
                self.getSchedulingDockWidget().widget().resetSimulation()
        else:
            reinit = moose.mooseAddChemSolver(modelRoot, solver)
            if reinit:
                self.getSchedulingDockWidget().widget().resetSimulation()

            #self.kkitRunView.getCentralWidget().addSolver(solver)

    def getCentralWidget(self):
        if self._centralWidget is None:
            self.createCentralWidget()
        return self._centralWidget


class KkitRunView(MooseEditorView):
    def __init__(self, plugin):
        MooseEditorView.__init__(self, plugin)
        self.plugin = plugin

    def getCentralWidget(self):
        if self._centralWidget is None:
            self._centralWidget = KineticRunWidget(self.plugin)
            self._centralWidget.editor = self.plugin.editorView
            self._centralWidget.setModelRoot(self.plugin.modelRoot)
        return self._centralWidget


class KkitEditorView(MooseEditorView):
    def __init__(self, plugin):
        MooseEditorView.__init__(self, plugin)

    def getCentralWidget(self):
        if self._centralWidget is None:
            self._centralWidget = kineticEditorWidget(self.plugin)
            self._centralWidget.setModelRoot(self.plugin.modelRoot)
        return self._centralWidget


class KineticsWidget(mplugin.EditorWidgetBase):
    def __init__(self, plugin, *args):
        mplugin.EditorWidgetBase.__init__(self, *args)
        self.plugin = plugin
        self.border = 5
        self.comptPen = 5
        self.iconScale = 1
        self.arrowsize = 2
        self.reset()

        self.defaultSceneheight = 1  #800#1000
        self.defaultScenewidth = 1  #000#2400
        self.positionInfoExist = True
        self.defaultComptsize = 5
        self.srcdesConnection = {}
        self.meshEntry = {}
        self.mooseId_GObj = {}
        self.qGraCompt = {}
        self.qGraGrp = {}
        self.xyCord = {}
        self.editor = None

    def reset(self):
        self.createdItem = {}
        #This are created at drawLine
        self.lineItem_dict = {}
        self.itemignoreZooming = False
        if hasattr(self, 'sceneContainer'):
            self.sceneContainer.clear()
        self.sceneContainer = QGraphicsScene(self)
        self.sceneContainer.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.sceneContainer.setBackgroundBrush(QColor(230, 220, 219, 120))

    def getsceneCord(self):
        self.cord = {}
        self.view.setRefWidget("runView")
        for item in self.sceneContainer.items():
            if isinstance(item, kkitQGraphics.KineticsDisplayItem):
                self.cord[item.mobj] = {
                    'x': item.scenePos().x(),
                    'y': item.scenePos().y()
                }
        return self.cord

    def updateModelView(self):
        self.initMooseObject()
        logger_.info( "updateModelView called ... %s" % str(self.m) )
        if not self.m:
            if hasattr(self, 'view') and isinstance(self.view, QWidget):
                self.layout().removeWidget(self.view)

            self.view = kkitViewcontrol.GraphicalView(self.modelRoot,
                    self.sceneContainer,
                    self.border, self,
                    self.createdItem)

            if isinstance(self, kineticEditorWidget):
                self.view.setRefWidget("editorView")
                self.view.setAcceptDrops(True)
            elif isinstance(self, KineticRunWidget):
                self.view.setRefWidget("runView")

            self.view.dropped.connect(self.objectEditSlot)
            hLayout = QGridLayout(self)
            self.setLayout(hLayout)
            hLayout.addWidget(self.view, 0, 0)
            return

        if hasattr(self, 'view') and isinstance(self.view, QWidget):
            self.layout().removeWidget(self.view)

        self.view = kkitViewcontrol.GraphicalView(self.modelRoot,
                self.sceneContainer, self.border, self, self.createdItem)

        if isinstance(self, kineticEditorWidget):
            self.mooseObjOntoscene()
            self.drawLine_arrow()
            self.view.setRefWidget("editorView")
            self.view.setAcceptDrops(True)
            self.view.dropped.connect(self.objectEditSlot)
            hLayout = QGridLayout(self)
            self.setLayout(hLayout)
            hLayout.addWidget(self.view)
        elif isinstance(self, KineticRunWidget):
            self.view.setRefWidget("runView")
            hLayout = QGridLayout(self)
            self.setLayout(hLayout)
            hLayout.addWidget(self.view)
            self.view.fitInView(
                self.sceneContainer.itemsBoundingRect().x() - 10,
                self.sceneContainer.itemsBoundingRect().y() - 10,
                self.sceneContainer.itemsBoundingRect().width() + 20,
                self.sceneContainer.itemsBoundingRect().height() + 20,
                Qt.Qt.IgnoreAspectRatio)
        else:
            logger_.warning("Unhandled type: %s:%s" % (type(self),self))

    def initMooseObject(self):
        self.m = moose.wildcardFind(self.modelRoot + '/##[ISA=ChemCompt]')
        if self.m:
            self.srcdesConnection = {}
            if self.meshEntry:
                self.meshEntry.clear()
            else:
                self.meshEntry = {}
            self.objPar, self.meshEntry, self.xmin, self.xmax, self.ymin\
                    , self.ymax, self.noPositionInfo = kkitOrdinateUtil.setupMeshObj(self.modelRoot)
            self.autocoordinates = False
            if self.srcdesConnection:
                self.srcdesConnection.clear()
            else:
                self.srcdesConnection = {}

            kkitOrdinateUtil.setupItem(self.modelRoot, self.srcdesConnection)
            if not self.noPositionInfo:
                self.autocoordinates = True
                kkitOrdinateUtil.autoCoordinates(self.meshEntry,
                                                 self.srcdesConnection)

        self.size = QtCore.QSize(1000, 550)

    def sizeHint(self):
        return QtCore.QSize(800, 400)

    def updateItemSlot(self, mooseObject):
        for item in self.sceneContainer.items():
            if isinstance(item, kkitQGraphics.PoolItem):
                if mooseObject.getId() == moose.element(item.mobj).getId():
                    item.updateSlot()
                    # once the text is edited in editor, laydisplay gets updated
                    # in turn resize the length, positionChanged signal shd be
                    # emitted.
                    self.positionChange(mooseObject)
                    self.view.removeConnector()
                    self.view.showConnector(item)

    def updateColorSlot(self, mooseObject, colour):
        #Color slot for changing background color for Pool,Enz and group from objecteditor
        anninfo = moose.Annotator(mooseObject.path + '/info')
        textcolor, bgcolor = kkitUtil.getColor(anninfo)
        anninfo.color = str(colour.name())

        if mooseObject.className == "Neutral":
            item = self.qGraGrp[mooseObject]
            item.setPen(
                QtGui.QPen(QtGui.QColor(colour),
                           item.pen().width(),
                           item.pen().style(),
                           item.pen().capStyle(),
                           item.pen().joinStyle()))

        elif (isinstance(mooseObject, moose.PoolBase) \
                or isinstance(mooseObject, moose.EnzBase) ):
            item = self.mooseId_GObj[mooseObject]
            item.updateColor(colour)

    def mooseObjOntoscene(self):
        #  All the compartments are put first on to the scene \
        #  Need to do: Check With upi if empty compartments exist
        self.qGraCompt = {}
        self.qGraGrp = {}
        self.mooseId_GObj = {}
        if self.qGraCompt:
            self.qGraCompt.clear()
        else:
            self.qGraCompt = {}

        if self.qGraGrp:
            self.qGraGrp.clear()
        else:
            self.qGraGrp = {}

        if self.qGraGrp:
            self.qGraGrp.clear()
        else:
            self.qGraGrp = {}

        if self.mooseId_GObj:
            self.mooseId_GObj.clear()
        else:
            self.mooseId_GObj = {}

        logger_.debug( "self.objPar: " + str(self.objPar) )
        for k, v in self.objPar.items():
            if isinstance(moose.element(k), moose.ChemCompt):
                self.createCompt(k)
                self.qGraCompt[k]

            elif isinstance(moose.element(k), moose.Neutral):
                if len(self.meshEntry[k]):
                    if isinstance(moose.element(v), moose.ChemCompt):
                        group_parent = self.qGraCompt[v]
                    elif isinstance(moose.element(v), moose.Neutral):
                        group_parent = self.qGraGrp[v]
                    self.createGroup(k, group_parent)

        for cmpt_grp, memb in self.meshEntry.items():
            if len(memb):
                if isinstance(moose.element(cmpt_grp), moose.ChemCompt):
                    qtGrpparent = self.qGraCompt[cmpt_grp]
                elif isinstance(moose.element(cmpt_grp), moose.Neutral):
                    qtGrpparent = self.qGraGrp[cmpt_grp]
                for mclass in [
                        "enzyme", "pool", "reaction", "cplx", "function",
                        "stimTab"
                ]:
                    self.mObjontoscene(memb, mclass, qtGrpparent)

        self.groupChildrenBoundingRect()
        # compartment's rectangle size is calculated depending on children
        self.comptChildrenBoundingRect()

    def mObjontoscene(self, memb, mclass, qtGrpparent):
        try:
            memb[mclass]
        except KeyError:
            pass
        else:
            for mObj in memb[mclass]:
                minfo = mObj.path + '/info'
                if mObj.className in ['Enz', "ZombieEnz"]:
                    mItem = kkitQGraphics.EnzItem(mObj, qtGrpparent)

                elif mObj.className in ['MMenz', "ZombieMMenz"]:
                    mItem = kkitQGraphics.MMEnzItem(mObj, qtGrpparent)

                elif isinstance(moose.element(mObj),
                                moose.PoolBase) and mclass != "cplx":
                    # depending on Editor Widget or Run widget pool will be
                    # created a PoolItem or PoolItemCircle
                    mItem = self.makePoolItem(mObj, qtGrpparent)

                elif isinstance(moose.element(mObj), moose.ReacBase):
                    mItem = kkitQGraphics.ReacItem(mObj, qtGrpparent)

                elif mclass == "cplx":
                    minfo = (mObj.parent).path + '/info'
                    mItem = kkitQGraphics.CplxItem(
                        mObj, self.mooseId_GObj[moose.element(mObj).parent])
                    self.mooseId_GObj[moose.element(mObj.getId())] = mItem

                elif mclass == "function":
                    if isinstance(moose.element(mObj.parent), moose.PoolBase):
                        minfo = moose.element(mObj).path + '/info'
                        moose.Annotator(minfo)
                        qtGrpparent = self.mooseId_GObj[moose.element(
                            mObj.parent)]
                    mItem = kkitQGraphics.FuncItem(mObj, qtGrpparent)

                elif mclass == "stimTab":
                    minfo = mObj.path + '/info'
                    mItem = kkitQGraphics.TableItem(mObj, qtGrpparent)
                self.mooseId_GObj[moose.element(mObj.getId())] = mItem
                self.setupDisplay(minfo, mItem, mclass)

    def createGroup(self, key, parent):
        self.new_GRP = kkitQGraphics.GRPItem(parent, 0, 0, 0, 0, key)
        self.qGraGrp[key] = self.new_GRP
        self.new_GRP.setRect(20, 20, 20, 20)

    def groupChildrenBoundingRect(self):
        for k, v in self.qGraGrp.items():
            grpcolor = moose.Annotator(moose.element(k.path + '/info')).color
            # TODO: One may need to calculate explicitly the boundary for Group
            # also if there is a cross-group connection, then
            # childrenBoundrect() will take the QPolygonItem position
            rectcompt = v.childrenBoundingRect()
            v.setRect(rectcompt.x() - 10,
                      rectcompt.y() - 10,
                      rectcompt.width() + 20,
                      rectcompt.height() + 20)
            v.setPen(
                QtGui.QPen(Qt.QColor(grpcolor), self.comptPen, Qt.Qt.SolidLine,
                           Qt.Qt.RoundCap, Qt.Qt.RoundJoin))

    def comptChildrenBoundingRect(self):
        for k, v in self.qGraCompt.items():
            # compartment's rectangle size is calculated depending on children
            rectcompt = kkitUtil.calculateChildBoundingRect(v)
            v.setRect(rectcompt.x() - 10,
                      rectcompt.y() - 10, (rectcompt.width() + 20),
                      (rectcompt.height() + 20))
            v.setPen(
                QtGui.QPen(Qt.QColor(66, 66, 66, 100), self.comptPen,
                           Qt.Qt.SolidLine, Qt.Qt.RoundCap, Qt.Qt.RoundJoin))

    def createCompt(self, key):
        logger_.debug( "Creating new compartment %s" % key)
        self.new_Compt = kkitQGraphics.ComptItem(self, 0, 0, 0, 0, key)
        self.qGraCompt[key] = self.new_Compt
        self.new_Compt.setRect(10, 10, 10, 10)
        self.sceneContainer.addItem(self.new_Compt)

    def setupDisplay(self, info, graphicalObj, objClass):
        Annoinfo = moose.Annotator(info)
        # For Reaction and Complex object I have skipped the process to get the
        # facecolor and background color.
        # we are not using these colors for displaying the object so just
        # passing dummy color white
        if (objClass == "reaction" or objClass == "cplx"
                or objClass == "Function" or objClass == "StimulusTable"):
            textcolor, bgcolor = QColor("white"), QColor("white")
        elif (objClass == "enzyme"):
            textcolor, bgcolor = kkitUtil.getColor(info)
            if bgcolor.name() == "#ffffff" or bgcolor == "white":
                bgcolor = kkitUtil.getRandColor()
                Annoinfo.color = str(bgcolor.name())
        else:
            textcolor, bgcolor = kkitUtil.getColor(info)
            if bgcolor.name() == "#ffffff" or bgcolor == "white":
                bgcolor = kkitUtil.getRandColor()
                Annoinfo.color = str(bgcolor.name())
        if isinstance(self, kineticEditorWidget):
            funct = ["Function", "ZombieFunction"]
            comptt = ["CubeMesh", "CylMesh"]

            if objClass in funct:
                poolt = ["ZombieBufPool", "BufPool"]
                if graphicalObj.mobj.parent.className in poolt:
                    xpos = 0
                    ypos = 30
                if graphicalObj.mobj.parent.className in comptt:
                    xpos, ypos = self.positioninfo(info)
            else:
                xpos, ypos = self.positioninfo(info)

        elif isinstance(self, KineticRunWidget):
            self.editormooseId_GObj = self.editor.getCentralWidget(
            ).mooseId_GObj
            editorItem = self.editormooseId_GObj[moose.element(info).parent]
            xpos = editorItem.scenePos().x()
            ypos = editorItem.scenePos().y()
        graphicalObj.setDisplayProperties(xpos, ypos, textcolor, bgcolor)

    def positioninfo(self, iteminfo):
        '''
        By this time, model loaded from kkit,cspace,SBML would have info
        field created and co-ordinates are added either by autocoordinates (for
        cspace,SBML(unless it is not saved from moose)) or from kkit.
        '''
        x = float(moose.element(iteminfo).getField('x'))
        y = float(moose.element(iteminfo).getField('y'))
        return x, y

    def drawLine_arrow(self, itemignoreZooming=False):
        for inn, out in self.srcdesConnection.items():
            #print "inn ",inn, " out ",out
            # self.srcdesConnection is dictionary which contains key,value \
            #    key is Enzyme or Reaction  and value [[list of substrate],[list of product]] (tuple)
            #    key is Function and value is [list of pool] (list)

            #src = self.mooseId_GObj[inn]
            linetype = "regular"
            if isinstance(out, tuple):
                src = self.mooseId_GObj[inn]
                if len(out[0]) == 0:
                    print(inn.className + ' : ' + inn.name +
                          " doesn't output message")
                else:
                    for items in (items for items in out[0]):
                        if re.search("xfer", moose.element(items[0]).name):
                            xrefPool = items[0].name[:items[0].name.
                                                     index("_xfer_")]
                            xrefCompt = items[0].name[items[0].name.
                                                      index("_xfer_") +
                                                      len("_xfer_"):]
                            orgCompt = moose.wildcardFind(self.modelRoot +
                                                          '/##[FIELD(name)=' +
                                                          xrefCompt + ']')[0]
                            orgPool = moose.wildcardFind(orgCompt.path +
                                                         '/##[FIELD(name)=' +
                                                         xrefPool + ']')[0]
                            itemslist = list(items)
                            itemslist[0] = orgPool
                            items = tuple(itemslist)
                            linetype = "crosscompt"
                        des = self.mooseId_GObj[moose.element(items[0])]
                        self.lineCord(src, des, items, itemignoreZooming,
                                      linetype)
                if len(out[1]) == 0:
                    print(inn.className + ' : ' + inn.name +
                          " doesn't output message")
                else:
                    for items in (items for items in out[1]):
                        if re.search("xfer", moose.element(items[0]).name):
                            xrefPool = items[0].name[:items[0].name.
                                                     index("_xfer_")]
                            xrefCompt = items[0].name[items[0].name.
                                                      index("_xfer_") +
                                                      len("_xfer_"):]
                            orgCompt = moose.wildcardFind(self.modelRoot +
                                                          '/##[FIELD(name)=' +
                                                          xrefCompt + ']')[0]
                            orgPool = moose.wildcardFind(orgCompt.path +
                                                         '/##[FIELD(name)=' +
                                                         xrefPool + ']')[0]
                            itemslist = list(items)
                            itemslist[0] = orgPool
                            items = tuple(itemslist)
                            linetype = "crosscompt"
                        des = self.mooseId_GObj[moose.element(items[0])]
                        self.lineCord(src, des, items, itemignoreZooming,
                                      linetype)
            elif isinstance(out, list):
                if len(out) == 0:
                    if inn.className == "StimulusTable":
                        print(inn.name + " doesn't have output")
                    elif inn.className == "ZombieFunction" or inn.className == "Function":
                        print(inn.name + " doesn't have sumtotal ")
                else:
                    src = self.mooseId_GObj[inn]
                    for items in (items for items in out):
                        if re.search("xfer", moose.element(items[0]).name):
                            xrefPool = items[0].name[:items[0].name.
                                                     index("_xfer_")]
                            xrefCompt = items[0].name[items[0].name.
                                                      index("_xfer_") +
                                                      len("_xfer_"):]
                            orgCompt = moose.wildcardFind(self.modelRoot +
                                                          '/##[FIELD(name)=' +
                                                          xrefCompt + ']')[0]
                            orgPool = moose.wildcardFind(orgCompt.path +
                                                         '/##[FIELD(name)=' +
                                                         xrefPool + ']')[0]
                            itemslist = list(items)
                            itemslist[0] = orgPool
                            items = tuple(itemslist)
                            linetype = "crosscompt"
                        des = self.mooseId_GObj[moose.element(items[0])]
                        self.lineCord(src, des, items, itemignoreZooming,
                                      linetype)

    def lineCord(self, src, des, type_no, itemignoreZooming, linetype):
        srcdes_list = []
        endtype = type_no[1]
        line = 0
        if (src == "") and (des == ""):
            print("Source or destination is missing or incorrect")
            return
        srcdes_list = [src, des, endtype, line]
        arrow = kkitUtil.calcArrow(srcdes_list, itemignoreZooming,
                                   self.iconScale)
        self.drawLine(srcdes_list, arrow, linetype)

        while (type_no[2] > 1 and line <= (type_no[2] - 1)):
            srcdes_list = [src, des, endtype, line]
            arrow = kkitUtil.calcArrow(srcdes_list, itemignoreZooming,
                                       self.iconScale)
            self.drawLine(srcdes_list, arrow, linetype)
            line = line + 1

        if type_no[2] > 5:
            print("Higher order reaction will not be displayed")

    def drawLine(self, srcdes_list, arrow, linetype="solid"):
        src = srcdes_list[0]
        des = srcdes_list[1]
        endtype = srcdes_list[2]
        line = srcdes_list[3]
        source = moose.element(
            next((k for k, v in self.mooseId_GObj.items() if v == src), None))
        for l, v, et, o in self.object2line[src]:
            if v == des and o == line:
                l.setPolygon(arrow)
                arrowPen = l.pen()
                arrowPenWidth = self.arrowsize * self.iconScale
                arrowPen.setColor(l.pen().color())
                arrowPen.setWidth(arrowPenWidth)
                l.setPen(arrowPen)
                return
        qgLineitem = self.sceneContainer.addPolygon(arrow)
        qgLineitem.setParentItem(src.parentItem())
        pen = QtGui.QPen(QtCore.Qt.green, 0, Qt.Qt.SolidLine, Qt.Qt.RoundCap,
                         Qt.Qt.RoundJoin)
        if linetype == "crosscompt":
            pen.setStyle(Qt.Qt.CustomDashLine)
            pen.setDashPattern([1, 5, 1, 5])

        pen.setWidth(self.arrowsize)

        # Green is default color moose.ReacBase and derivatives - already set above
        if isinstance(source, moose.EnzBase):
            if ((endtype == 's') or (endtype == 'p')):
                pen.setColor(QtCore.Qt.red)
            elif (endtype != 'cplx'):
                p1 = (next(
                    (k for k, v in self.mooseId_GObj.items() if v == src),
                    None))
                pinfo = p1.parent.path + '/info'
                color, bgcolor = kkitUtil.getColor(pinfo)
                #color = QColor(color[0],color[1],color[2])
                pen.setColor(bgcolor)

        elif isinstance(source, moose.PoolBase) or isinstance(
                source, moose.Function):
            pen.setColor(QtCore.Qt.blue)
        elif isinstance(source, moose.StimulusTable):
            pen.setColor(QtCore.Qt.yellow)
        self.lineItem_dict[qgLineitem] = srcdes_list
        self.object2line[src].append((qgLineitem, des, endtype, line))
        self.object2line[des].append((qgLineitem, src, endtype, line))
        qgLineitem.setPen(pen)

    def positionChange(self, mooseObject):
        #If the item position changes, the corresponding arrow's are calculated
        for k, v in self.qGraCompt.items():
            for rectChilditem in v.childItems():
                self.updateArrow(rectChilditem)
                if isinstance(rectChilditem, kkitQGraphics.GRPItem):
                    for grpChilditem in rectChilditem.childItems():
                        self.updateArrow(grpChilditem)
                        if isinstance(grpChilditem,
                                      kkitQGraphics.KineticsDisplayItem):
                            if moose.exists(grpChilditem.mobj.path + '/info'):
                                #print grpChilditem.mobj.name,   grpChilditem.scenePos()
                                moose.element(
                                    grpChilditem.mobj.path +
                                    '/info').x = grpChilditem.scenePos().x()
                                moose.element(
                                    grpChilditem.mobj.path +
                                    '/info').y = grpChilditem.scenePos().y()
                if isinstance(rectChilditem, kkitUtil.KineticsDisplayItem):
                    if moose.exists(rectChilditem.mobj.path + '/info'):
                        moose.element(
                            rectChilditem.mobj.path +
                            '/info').x = rectChilditem.scenePos().x()
                        moose.element(
                            rectChilditem.mobj.path +
                            '/info').y = rectChilditem.scenePos().y()

            rectcompt = kkitUtil.calculateChildBoundingRect(v)
            comptBoundingRect = v.boundingRect()
            if not comptBoundingRect.contains(rectcompt):
                self.updateCompartmentSize(v)
            else:
                rectcompt = kkitUtil.calculateChildBoundingRect(v)
                v.setRect(rectcompt.x() - 10,
                          rectcompt.y() - 10, (rectcompt.width() + 20),
                          (rectcompt.height() + 20))

    def positionChange_old(self, mooseObject):
        # If the item position changes, the corresponding arrow's are calculated
        if isinstance(moose.element(mooseObject), kkitQGraphics.ChemCompt):
            for k, v in self.qGraCompt.items():
                mesh = moose.element(mooseObject).path
                if k.path == mesh:
                    for rectChilditem in v.childItems():
                        if isinstance(rectChilditem,
                                      kkitQGraphics.KineticsDisplayItem):
                            if moose.exists(rectChilditem.mobj.path):
                                iInfo = rectChilditem.mobj.path + '/info'
                                moose.Annotator(iInfo)
                                if isinstance(
                                        moose.element(rectChilditem.mobj.path),
                                        moose.PoolBase):
                                    t = moose.element(rectChilditem.mobj.path)
                                    moose.element(t).children
                                    for items in moose.element(t).children:
                                        if isinstance(moose.element(items),
                                                      moose.Function):
                                            test = moose.element(items.path +
                                                                 '/x')
                                            for i in moose.element(
                                                    test).neighbors['input']:
                                                j = self.mooseId_GObj[
                                                    moose.element(i)]
                                                self.updateArrow(j)
                            self.updateArrow(rectChilditem)
        elif moose.element(mooseObject).className == 'Neutral':
            for k, v in self.qGraGrp.items():
                for grpChilditem in v.childItems():
                    if isinstance(grpChilditem,
                                  kkitQGraphics.KineticsDisplayItem):
                        if moose.exists(grpChilditem.mobj.path):
                            iInfo = grpChilditem.mobj.path + '/info'
                            moose.Annotator(iInfo)

                        if isinstance(moose.element(grpChilditem.mobj.path),
                                      moose.PoolBase):
                            t = moose.element(grpChilditem.mobj.path)
                            moose.element(t).children
                            for items in moose.element(t).children:
                                if isinstance(moose.element(items),
                                              moose.Function):
                                    test = moose.element(items.path + '/x')
                                    for i in moose.element(
                                            test).neighbors['input']:
                                        j = self.mooseId_GObj[moose.element(i)]
                                        self.updateArrow(j)
                        self.updateArrow(grpChilditem)
                rectgrp = kkitUtil.calculateChildBoundingRect(v)
                v.setRect(rectgrp.x() - 10,
                          rectgrp.y() - 10, (rectgrp.width() + 20),
                          (rectgrp.height() + 20))
                for k, v in self.qGraCompt.items():
                    rectcompt = kkitUtil.calculateChildBoundingRect(v)
                    comptBoundingRect = v.boundingRect()
                    if not comptBoundingRect.contains(rectcompt):
                        self.updateCompartmentSize(v)

                    else:
                        rectcompt = kkitUtil.calculateChildBoundingRect(v)
                        v.setRect(rectcompt.x() - 10,
                                  rectcompt.y() - 10,
                                  rectcompt.width() + 20,
                                  rectcompt.height() + 20)
        else:
            mobj = self.mooseId_GObj[moose.element(mooseObject)]
            self.updateArrow(mobj)
            for k, v in self.qGraCompt.items():
                rectcompt = kkitUtil.calculateChildBoundingRect(v)
                comptBoundingRect = v.boundingRect()
                if not comptBoundingRect.contains(rectcompt):
                    self.updateCompartmentSize(v)

                else:
                    rectcompt = kkitUtil.calculateChildBoundingRect(v)
                    v.setRect(rectcompt.x() - 10,
                              rectcompt.y() - 10,
                              rectcompt.width() + 20,
                              rectcompt.height() + 20)

    def updateGrpSize(self, grp):
        childrenBoundary = kkitUtil.calculateChildBoundingRect(grp)
        x = childrenBoundary.x()
        y = childrenBoundary.y()
        height = childrenBoundary.height()
        width = childrenBoundary.width()
        grp.setRect(x - 10, y - 10, width + 20, height + 20)

    def updateCompartmentSize(self, compartment):
        compartmentBoundary = compartment.rect()
        childrenBoundary = kkitUtil.calculateChildBoundingRect(compartment)
        x = min(compartmentBoundary.x(), childrenBoundary.x())
        y = min(compartmentBoundary.y(), childrenBoundary.y())
        width = max(compartmentBoundary.width(), childrenBoundary.width())
        height = max(compartmentBoundary.height(), childrenBoundary.height())
        compartment.setRect(x - 10, y - 10, width + 20, height + 20)

    def updateArrow(self, qGTextitem):
        #if there is no arrow to update then return
        listItem = self.object2line[qGTextitem]
        for ql, va, endtype, order in listItem:
            srcdes = []
            srcdes = self.lineItem_dict[ql]
            # Checking if src (srcdes[0]) or des (srcdes[1]) is ZombieEnz,
            # if yes then need to check if cplx is connected to any mooseObject,
            # so that when Enzyme is moved, cplx connected arrow to other
            # mooseObject(poolItem) should also be updated
            if( type(srcdes[0]) == kkitQGraphics.EnzItem \
                    or type(srcdes[0] == kkitQGraphics.MMEnzItem)):
                self.cplxUpdatearrow(srcdes[0])
            elif( type(srcdes[1]) == kkitQGraphics.EnzItem \
                    or type(srcdes[1] == kkitQGraphics.MMEnzItem)):
                self.cplxUpdatearrow(srcdes[1])
            arrow = kkitUtil.calcArrow(srcdes, self.itemignoreZooming,
                                       self.iconScale)
            ql.setPolygon(arrow)

    def cplxUpdatearrow(self, srcdes):
        # srcdes which is 'EnzItem' from this,get ChildItems are retrived (b'cos cplx is child of zombieEnz)
        #And cplxItem is passed for updatearrow
        for item in srcdes.childItems():
            if isinstance(item, kkitQGraphics.CplxItem):
                self.updateArrow(item)

    def positionChange1(self, mooseObject):
        #If the item position changes, the corresponding arrow's are calculated
        if ( (isinstance(moose.element(mooseObject), moose.CubeMesh)) \
                or (isinstance(moose.element(mooseObject), moose.CylMesh))):
            v = self.qGraCompt[mooseObject]
            for rectChilditem in v.childItems():
                self.updateArrow(rectChilditem)
        else:
            mobj = self.mooseId_GObj[mooseObject.getId()]
            self.updateArrow(mobj)
            mooseObjcompt = self.findparent(mooseObject)
            v = self.qGraCompt[mooseObjcompt]
            #childBoundingRect = v.childrenBoundingRect()
            childBoundingRect = kkitUtil.calculateChildBoundingRect(v)
            comptBoundingRect = v.boundingRect()
            rectcompt = comptBoundingRect.united(childBoundingRect)
            comptPen = v.pen()
            comptWidth = 5
            comptPen.setWidth(comptWidth)
            v.setPen(comptPen)
            if not comptBoundingRect.contains(childBoundingRect):
                v.setRect(rectcompt.x() - comptWidth,
                          rectcompt.y() - comptWidth,
                          rectcompt.width() + (comptWidth * 2),
                          rectcompt.height() + (comptWidth * 2))


class kineticEditorWidget(KineticsWidget):
    def __init__(self, plugin, *args):

        KineticsWidget.__init__(self, plugin, *args)
        self.plugin = plugin
        self.insertMenu = QMenu('&Insert')
        self._menus.append(self.insertMenu)
        self.insertMapper = QtCore.QSignalMapper(self)
        classlist = [
            'CubeMesh', 'CylMesh', 'Pool', 'BufPool', 'Function', 'Reac',
            'Enz', 'MMenz', 'StimulusTable'
        ]
        self.toolTipinfo = {
            "CubeMesh":
            "",
            "CylMesh":
            "",
            "Pool":
            "A Pool is a collection of molecules of a given species in a given cellular compartment.\n It can undergo reactions that convert it into other pool(s). \nParameters: initConc (Initial concentration), diffConst (diffusion constant). Variable: conc (Concentration)",
            "BufPool":
            "A BufPool is a buffered pool. \nIt is a collection of molecules of a given species in a given cellular compartment, that are always present at the same concentration.\n This is set by the initConc parameter. \nIt can undergo reactions in the same way as a pool.",
            "Function":
            "A Func computes an arbitrary mathematical expression of one or more input concentrations of Pools. The output can be used to control the concentration of another Pool, or as an input to another Func",
            "StimulusTable":
            "A StimulusTable stores an array of values that are read out during a simulation, and typically control the concentration of one of the pools in the model. \nParameters: size of table, values of entries, start and stop times, and an optional loopTime that defines the period over which the StimulusTable should loop around to repeat its values",
            "Reac":
            "A Reac is a chemical reaction that converts substrates into products, and back. \nThe rates of these conversions are specified by the rate constants Kf and Kb respectively.",
            "MMenz":
            "An MMenz is the Michaelis-Menten version of an enzyme activity of a given Pool.\n The MMenz must be created on a pool and can only catalyze a single reaction with a specified substrate(s). \nIf a given enzyme species can have multiple substrates, then multiple MMenz activites must be created on the parent Pool. \nThe rate of an MMenz is V [S].[E].kcat/(Km + [S]). There is no enzyme-substrate complex. Parameters: Km and kcat.",
            "Enz":
            "An Enz is an enzyme activity of a given Pool. The Enz must be created on a pool and can only catalyze a single reaction with a specified substrate(s). \nIf a given enzyme species can have multiple substrates, then multiple Enz activities must be created on the parent Pool. \nThe reaction for an Enz is E + S <===> E.S ---> E + P. \nThis means that a new Pool, the enzyme-substrate complex E.S, is always formed when you create an Enz. \nParameters: Km and kcat, or alternatively, K1, K2 and K3. Km = (K2+K3)/K1"
        }
        insertMapper, actions = self.getInsertActions(classlist)
        for action in actions:
            self.insertMenu.addAction(action)
            doc = self.toolTipinfo[str(action.text())]
            if doc == "":
                classname = str(action.text())
                doc = moose.element('/classes/%s' % (classname)).docs
                doc = doc.split('Description:')[-1].split('Name:')[0].strip()
            action.setToolTip(doc)

    def GrViewresize(self, event):
        #when Gui resize and event is sent which inturn call resizeEvent of qgraphicsview
        pass
        #self.view.resizeEvent1(event)

    def makePoolItem(self, poolObj, qGraCompt):
        return kkitQGraphics.PoolItem(poolObj, qGraCompt)

    def getToolBars(self):
        #Add specific tool items with respect to kkit
        if not hasattr(self, '_insertToolBar'):
            self._insertToolBar = QToolBar('Insert')
            self._toolBars.append(self._insertToolBar)
            for action in self.insertMenu.actions():
                button = MToolButton()
                button.setDefaultAction(action)
                iconPath = os.path.join(config.MOOSE_ICON_DIR, action.text() + '.png')
                assert os.path.exists(iconPath), "Does not exists %s" % iconPath
                button.setIcon(QtGui.QIcon(iconPath))
                self._insertToolBar.addWidget(button)
        return self._toolBars

class KineticRunWidget(KineticsWidget):
    def __init__(self, plugin, *args):
        KineticsWidget.__init__(self, plugin, *args)

    def showEvent(self, event):
        self.refresh()
        # pass
    def refresh(self):
        self.sceneContainer.clear()
        self.Comptexist = moose.wildcardFind(self.modelRoot +
                                             '/##[ISA=ChemCompt]')
        if self.Comptexist:
            # pass
            self.initMooseObject()
            self.mooseObjOntoscene()
            self.drawLine_arrow(itemignoreZooming=False)

    def makePoolItem(self, poolObj, qGraCompt):
        return kkitQGraphics.PoolItemCircle(poolObj, qGraCompt)

    def getToolBars(self):
        return self._toolBars

    def updateValue(self):
        for item in self.sceneContainer.items():
            if isinstance(item, kkitQGraphics.ReacItem) \
                    or isinstance(item, kkitQGraphics.MMEnzItem) \
                    or isinstance(item, kkitQGraphics.EnzItem) \
                    or isinstance(item, kkitQGraphics.PoolItemCircle) \
                    or isinstance(item, kkitQGraphics.CplxItem):
                item.updateValue(item.mobj)

    def changeBgSize(self):
        for item in self.sceneContainer.items():
            if isinstance(item, kkitQGraphics.PoolItemCircle):
                initialConc = moose.element(item.mobj).concInit
                presentConc = moose.element(item.mobj).conc
                if initialConc != 0:
                    ratio = presentConc / initialConc
                else:
                    ratio = presentConc
                if ratio > '10':
                    ratio = 9
                if ratio < '0.0':
                    ratio = 0.1
                item.updateRect(math.sqrt(abs(ratio)))

    def resetColor(self):
        for item in self.sceneContainer.items():
            if isinstance(item, kkitQGraphics.PoolItemCircle):
                item.returnEllispeSize()


if __name__ == "__main__":
    size = QtCore.QSize(1024, 768)
    sdir = os.path.dirname(__file__)
    modelPath = 'Kholodenko'
    itemignoreZooming = False
    try:
        filepath = os.path.join(sdir, '../../data/' + modelPath + '.g')
        print("%s" % (filepath))
        moose.loadModel(filepath, '/' + modelPath)
        dt = KineticsWidget( "kkit" )
        dt.modelRoot = '/' + modelPath
        dt.updateModelView()
        dt.show()
    except IOError as e:
        print(e)
    sys.exit(app.exec_())
