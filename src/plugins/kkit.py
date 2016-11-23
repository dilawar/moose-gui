import sys
import posixpath
from os.path import expanduser

from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QColor

from moose import *
from moose.genesis import write
from moose import SBML

from moosegui.mplugin import *
from moosegui.mtoolbutton import MToolButton
from moosegui.plugins.default import *
from moosegui.plugins.kkitUtil import *
from moosegui.plugins.kkitQGraphics import PoolItem, ReacItem, EnzItem, CplxItem, ComptItem
from moosegui.plugins.kkitViewcontrol import *
from moosegui.plugins.kkitCalcArrow import *
from moosegui.plugins.kkitOrdinateUtil import *
from moosegui.plugins.setsolver import *
from moosegui.RunWidget import RunWidget

import moosegui.TooltipInfo as TooltipInfo

from moosegui.config import _logger


class KkitPlugin(MoosePlugin):
    """Default plugin for MOOSE GUI"""

    def __init__(self, *args):
        MoosePlugin.__init__(self, *args)
        self.view = None
        self.fileinsertMenu = QtGui.QMenu('&File')
        if not hasattr(self, 'SaveModelAction'):
            self.saveModelAction = QtGui.QAction('Save', self)
            self.saveModelAction.setShortcut(QtGui.QApplication.translate(
                "MainWindow", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8))
            self.fileinsertMenu.addAction(self.saveModelAction)
        self._menus.append(self.fileinsertMenu)
        self.getEditorView()

    def connect(self, *args):
        """Commeneted out """
        pass

    def SaveModelDialogSlot(self):
        type_sbml = 'SBML'
        type_genesis = 'Genesis'
        dirpath = ""
        if not dirpath:
            dirpath = expanduser("~")
        filters = {'SBML(*.xml)': type_sbml, 'Genesis(*.g)': type_genesis}

        filename, filter_ = QtGui.QFileDialog.getSaveFileNameAndFilter(
            None, 'Save File', dirpath, ';;'.join(filters))
        extension = ""
        if str(filename).rfind('.') != -1:
            filename = filename[:str(filename).rfind('.')]
            if str(filter_).rfind('.') != -1:
                extension = filter_[str(filter_).rfind('.'):len(filter_) - 1]
        if filename:
            filename = filename
            if filters[str(filter_)] == 'SBML':
                self.sceneObj = KkitEditorView(
                    self).getCentralWidget().mooseId_GObj
                self.coOrdinates = {}
                for k, v in list(self.sceneObj.items()):
                    if moose.exists(moose.element(k).path + '/info'):
                        annoInfo = Annotator(k.path + '/info')
                        self.coOrdinates[k] = {
                            'x': annoInfo.x, 'y': annoInfo.y}

                writeerror = -2
                conisitencyMessages = ""
                writtentofile = "/test.xml"
                writeerror, consistencyMessages, writtentofile = moose.SBML.mooseWriteSBML(
                    self.modelRoot, str(filename), self.coOrdinates)
                if writeerror == -2:
                    QtGui.QMessageBox.warning(
                        None, 'Could not save the Model', consistencyMessages)
                elif writeerror == -1:
                    QtGui.QMessageBox.warning(
                        None,
                        'Could not save the Model',
                        '\n This model is not valid SBML Model, failed in the consistency check')
                elif writeerror == 1:
                    QtGui.QMessageBox.information(
                        None, 'Saved the Model', '\n File saved to \'{filename}\''.format(
                            filename=filename + '.xml'), QtGui.QMessageBox.Ok)
                elif writeerror == 0:
                    QtGui.QMessageBox.information(
                        None,
                        'Could not save the Model',
                        '\nThe filename could not be opened for writing')

            elif filters[str(filter_)] == 'Genesis':
                mdtype = moose.Annotator(self.modelRoot + '/info')
                self.coOrdinates = {}
                xycord = []
                self.sceneObj = KkitEditorView(
                    self).getCentralWidget().mooseId_GObj
                # Here get x,y coordinates from the Annotation, to save layout position
                # into genesis
                for k, v in list(self.sceneObj.items()):
                    if moose.exists(moose.element(k).path + '/info'):
                        annoInfo = Annotator(k.path + '/info')
                        self.coOrdinates[k] = {
                            'x': annoInfo.x, 'y': annoInfo.y}
                if mdtype.modeltype != "kkit":
                    # If coordinates come from kkit then directly transfering the co-ordinates
                    # else zoomed in factor is applied before saving it to
                    # genesis form
                    for k, v in list(self.coOrdinates.items()):
                        xycord.append(v['x'])
                        xycord.append(v['y'])
                    cmin = min(xycord)
                    cmax = max(xycord)
                    for k, v in list(self.coOrdinates.items()):
                        x = v['x']
                        xprime = int(
                            (20 * (float(v['x'] - cmin) / float(cmax - cmin))) - 10)
                        v['x'] = xprime
                        y = v['y']
                        yprime = int(
                            (20 * (float(v['y'] - cmin) / float(cmax - cmin))) - 10)
                        v['y'] = -yprime

                filename = filename
                writeerror = write(
                    self.modelRoot,
                    str(filename),
                    self.coOrdinates)
                if not writeerror:
                    QtGui.QMessageBox.information(
                        None, 'Could not save the Model', '\nCheck the file')
                else:
                    QtGui.QMessageBox.information(
                        None, 'Saved the Model', '\n File saved to \'{filename}\''.format(
                            filename=filename + '.g'), QtGui.QMessageBox.Ok)

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
            #self.editorView = KkitEditorView(self, self.dataTable)
            self.editorView = KkitEditorView(self)
            self.editorView.getCentralWidget().editObject.connect(
                self.mainWindow.objectEditSlot)
            # self.editorView.GrViewresize(self)
            # self.editorView.connect(self,QtCore.SIGNAL("resize(QResizeEvent)"),self.editorView.GrViewresize)
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
        schedulingDockWidget = self.view.getSchedulingDockWidget().widget()
        self._kkitWidget = self.view.plugin.getEditorView().getCentralWidget()
        self.runView = KkitRunView(self._kkitWidget)
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
        self._centralWidget = RunWidget(self.modelRoot)
        self.kkitRunView = KkitRunView(self.plugin)
        self.plotWidgetContainer = PlotWidgetContainer(self.modelRoot)
        self._centralWidget.setChildWidget(
            self.kkitRunView.getCentralWidget(), False, 0, 0, 1, 1)
        self._centralWidget.setChildWidget(
            self.plotWidgetContainer, False, 0, 1, 1, 2)
        self._centralWidget.setPlotWidgetContainer(self.plotWidgetContainer)
        self.schedular = self.getSchedulingDockWidget().widget()
        self.schedular.runner.simulationProgressed.connect(
            self.kkitRunView.getCentralWidget().updateValue)
        self.schedular.runner.simulationProgressed.connect(
            self.kkitRunView.getCentralWidget().changeBgSize)
        self.schedular.runner.simulationReset.connect(
            self.kkitRunView.getCentralWidget().resetColor)
        # self.schedular.runner.simulationReset.connect(self.setSolver)
        self.schedular.preferences.applyChemicalSettings.connect(
            self.setSolverFromSettings)
        compt = moose.wildcardFind(self.modelRoot + '/##[ISA=ChemCompt]')
        ann = moose.Annotator(self.modelRoot + '/info')
        if compt:
            #self.runTime = (moose.Annotator(self.modelRoot+'/info')).runtime
            #solver = (moose.Annotator(self.modelRoot+'/info')).solver
            self.runTime = moose.element(ann).runtime
            solver = moose.element(ann).solver
        else:
            self.runTime = 100
            solver = "gsl"
        self.schedular.simulationRuntime.setText(str(self.runTime))
        # preferences
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
        if solver is None:
            reinit = addSolver(
                modelRoot, self.getSchedulingDockWidget().widget().solver)
            if reinit:
                self.getSchedulingDockWidget().widget().resetSimulation()
        else:
            reinit = addSolver(modelRoot, solver)
            if reinit:
                self.getSchedulingDockWidget().widget().resetSimulation()

            # self.kkitRunView.getCentralWidget().addSolver(solver)

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
            self._centralWidget = kineticRunWidget(self.plugin)
            self._centralWidget.editor = self.plugin.editorView
            # self._centralWidget.view.objectSelected.connect(self.plugin.mainWindow.objectEditSlot)
            self._centralWidget.setModelRoot(self.plugin.modelRoot)
        return self._centralWidget


class KkitEditorView(MooseEditorView):

    def __init__(self, plugin):
        MooseEditorView.__init__(self, plugin)

    def getCentralWidget(self):
        if self._centralWidget is None:
            self._centralWidget = KineticEditorWidget(self.plugin)
            self._centralWidget.setModelRoot(self.plugin.modelRoot)
        return self._centralWidget


class KineticsWidget(EditorWidgetBase):

    def __init__(self, plugin, *args):
        EditorWidgetBase.__init__(self, *args)
        self.plugin = plugin
        self.border = 5
        self.comptPen = 5
        self.iconScale = 1
        self.arrowsize = 2
        self.defaultComptsize = 5
        self.noPositionInfo = True
        self.xyCord = {}
        self.reset()
        self.qGraCompt = {}
        self.mooseId_GObj = {}
        self.srcdesConnection = {}
        self.editor = None
        self.xmin = 0.0
        self.xmax = 1.0
        self.ymin = 0.0
        self.ymax = 1.0
        self.xratio = 1.0
        self.yratio = 1.0

    def reset(self):
        self.createdItem = {}
        # This are created at drawLine
        self.lineItem_dict = {}
        self.object2line = defaultdict(list)
        self.itemignoreZooming = False

        if hasattr(self, 'sceneContainer'):
            self.sceneContainer.clear()
        self.sceneContainer = QtGui.QGraphicsScene(self)
        self.sceneContainer.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        sceneDim = self.sceneContainer.itemsBoundingRect()
        # if (sceneDim.width() == 0 and sceneDim.height() == 0):
        #     self.sceneContainer.setSceneRect(0,0,30,30)
        # else:
        # elf.sceneContainer.setSceneRect(self.sceneContainer.itemsBoundingRect())
        self.sceneContainer.setBackgroundBrush(QColor(230, 220, 219, 120))

    def updateModelView(self):
        self.getMooseObj()
        minmaxratiodict = {
            'xmin': self.xmin,
            'xmax': self.xmax,
            'ymin': self.ymin,
            'ymax': self.ymax,
            'xratio': self.xratio,
            'yratio': self.yratio}
        if not self.m:
            # At the time of model building
            # when we want an empty GraphicView while creating new model,
            # then remove all the view and add an empty view
            if hasattr(self, 'view') and isinstance(self.view, QtGui.QWidget):
                self.layout().removeWidget(self.view)
           # self.sceneContainer.setSceneRect(-self.width()/2,-self.height()/2,self.width(),self.height())
            self.view = GraphicalView(
                self.modelRoot,
                self.sceneContainer,
                self.border,
                self,
                self.createdItem,
                minmaxratiodict)

            if isinstance(self, KineticEditorWidget):
                self.view.setRefWidget("editorView")
                self.view.setAcceptDrops(True)
            elif isinstance(self, kineticRunWidget):
                self.view.setRefWidget("runView")
            # self.connect(self.view, QtCore.SIGNAL("dropped"), self.objectEditSlot)
            hLayout = QtGui.QGridLayout(self)
            self.setLayout(hLayout)
            hLayout.addWidget(self.view, 0, 0)
        else:
            # Already created Model
            # maxmium and minimum coordinates of the objects specified in kkit file.
            # self.mooseObjOntoscene()
            # self.drawLine_arrow()
            if hasattr(self, 'view') and isinstance(self.view, QtGui.QWidget):
                self.layout().removeWidget(self.view)
            self.view = GraphicalView(
                self.modelRoot,
                self.sceneContainer,
                self.border,
                self,
                self.createdItem,
                minmaxratiodict)
            if isinstance(self, KineticEditorWidget):
                # self.getMooseObj()
                self.mooseObjOntoscene()
                self.drawLine_arrow()
                self.view.setRefWidget("editorView")
                self.view.setAcceptDrops(True)
                # self.connect(self.view, QtCore.SIGNAL("dropped"), self.objectEditSlot)
                hLayout = QtGui.QGridLayout(self)
                self.setLayout(hLayout)
                hLayout.addWidget(self.view)
            elif isinstance(self, kineticRunWidget):
                self.view.setRefWidget("runView")
                hLayout = QtGui.QGridLayout(self)
                self.setLayout(hLayout)
                hLayout.addWidget(self.view)
                self.view.fitInView(
                    self.sceneContainer.itemsBoundingRect().x() - 10,
                    self.sceneContainer.itemsBoundingRect().y() - 10,
                    self.sceneContainer.itemsBoundingRect().width() + 20,
                    self.sceneContainer.itemsBoundingRect().height() + 20,
                    Qt.Qt.IgnoreAspectRatio)

    def getMooseObj(self):
        # This fun call 2 more function
        # -- setupMeshObj(self.modelRoot),
        #    ----self.meshEntry has [meshEnt] = function: {}, Pool: {} etc
        # setupItem
        self.m = wildcardFind(self.modelRoot + '/##[ISA=ChemCompt]')
        if self.m:
            # self.xmin = 0.0
            # self.xmax = 1.0
            # self.ymin = 0.0
            # self.ymax = 1.0
            self.autoCordinatepos = {}
            self.srcdesConnection = {}

            #self.meshEntry.clear= {}
            # Compartment and its members are setup
            self.meshEntry, self.xmin, self.xmax, self.ymin, self.ymax, self.noPositionInfo = setupMeshObj(
                self.modelRoot)
            self.autocoordinates = False
            if self.srcdesConnection:
                self.srcdesConnection.clear()
            else:
                self.srcdesConnection = {}
            setupItem(self.modelRoot, self.srcdesConnection)
            if not self.noPositionInfo:
                self.autocoordinates = True

                self.xmin, self.xmax, self.ymin, self.ymax, self.autoCordinatepos = autoCoordinates(
                    self.meshEntry, self.srcdesConnection)
            # TODO: size will be dummy at this point, but size I need the
            # availiable size from the Gui
            self.size = QtCore.QSize(1000, 550)

            if self.xmax - self.xmin != 0:
                self.xratio = (self.size.width() - 10) / \
                    (self.xmax - self.xmin)
            else:
                self.xratio = self.size.width() - 10

            if self.ymax - self.ymin:
                self.yratio = (self.size.height() - 10) / \
                    (self.ymax - self.ymin)
            else:
                self.yratio = (self.size.height() - 10)

            self.xratio = int(self.xratio)
            self.yratio = int(self.yratio)
            if self.xratio == 0:
                self.xratio = 1
            if self.yratio == 0:
                self.yratio = 1

    def sizeHint(self):
        return QtCore.QSize(800, 400)

    def updateItemSlot(self, mooseObject):
        # This is overridden by derived classes to connect appropriate
        # slot for updating the display item.
        # In this case if the name is updated from the keyboard both in
        # mooseobj and gui gets updation
        changedItem = ''

        for item in list(self.sceneContainer.items()):
            if isinstance(item, PoolItem):
                if mooseObject.getId() == element(item.mobj).getId():
                    item.updateSlot()
                    # once the text is edited in editor, laydisplay gets
                    # updated in turn resize the length, positionChanged signal
                    # shd be emitted
                    self.positionChange(mooseObject)
                    self.view.removeConnector()
                    self.view.showConnector(item)

    def updateColorSlot(self, mooseObject, color):
        # Color slot for changing background color for PoolItem from
        # objecteditor
        anninfo = moose.Annotator(mooseObject.path + '/info')
        textcolor, bgcolor = getColor(anninfo)
        anninfo.color = str(color.name())
        item = self.mooseId_GObj[mooseObject]
        if (isinstance(item, PoolItem) or isinstance(
                item, EnzItem) or isinstance(item, MMEnzItem)):
            item.updateColor(color)

    def mooseObjOntoscene(self):
        #  All the compartments are put first on to the scene \
        #  Need to do: Check With upi if empty compartments exist
        self.qGraCompt = {}
        self.mooseId_GObj = {}
        if self.qGraCompt:
            self.qGraCompt.clear()
        else:
            self.qGraCompt = {}
        if self.mooseId_GObj:
            self.mooseId_GObj.clear()
        else:
            self.mooseId_GObj = {}

        for cmpt in sorted(self.meshEntry.keys()):
            self.createCompt(cmpt)
            self.qGraCompt[cmpt]
            #comptRef = self.qGraCompt[cmpt]

        # Enzymes of all the compartments are placed first, \
        #     so that when cplx (which is pool object) queries for its parent, it gets its \
        #     parent enz co-ordinates with respect to QGraphicsscene """

        for cmpt, memb in list(self.meshEntry.items()):
            for enzObj in find_index(memb, 'enzyme'):
                enzinfo = enzObj.path + '/info'
                if enzObj.className == 'Enz':
                    enzItem = EnzItem(enzObj, self.qGraCompt[cmpt])
                else:
                    enzItem = MMEnzItem(enzObj, self.qGraCompt[cmpt])
                self.mooseId_GObj[element(enzObj.getId())] = enzItem
                self.setupDisplay(enzinfo, enzItem, "enzyme")

                # self.setupSlot(enzObj,enzItem)
        for cmpt, memb in list(self.meshEntry.items()):
            for poolObj in find_index(memb, 'pool'):
                poolinfo = poolObj.path + '/info'
                # depending on Editor Widget or Run widget pool will be created
                # a PoolItem or PoolItemCircle
                poolItem = self.makePoolItem(poolObj, self.qGraCompt[cmpt])
                self.mooseId_GObj[element(poolObj.getId())] = poolItem
                self.setupDisplay(poolinfo, poolItem, "pool")

            for reaObj in find_index(memb, 'reaction'):
                reainfo = reaObj.path + '/info'
                reaItem = ReacItem(reaObj, self.qGraCompt[cmpt])
                self.setupDisplay(reainfo, reaItem, "reaction")
                self.mooseId_GObj[element(reaObj.getId())] = reaItem

            for tabObj in find_index(memb, 'table'):
                tabinfo = tabObj.path + '/info'
                tabItem = TableItem(tabObj, self.qGraCompt[cmpt])
                self.setupDisplay(tabinfo, tabItem, "tab")
                self.mooseId_GObj[element(tabObj.getId())] = tabItem

            for funcObj in find_index(memb, 'function'):
                funcinfo = moose.element(funcObj).path + '/info'
                if funcObj.parent.className in [ "ZombieBufPool", "BufPool" ]:
                    funcinfo = moose.element(funcObj).path + '/info'
                    Af = Annotator(funcinfo)
                    funcParent = self.mooseId_GObj[element(funcObj.parent)]
                elif funcObj.parent.className in [ "CubeMesh", "CylMesh"] :
                    funcParent = self.qGraCompt[cmpt]
                funcItem = FuncItem(funcObj, funcParent)
                self.mooseId_GObj[element(funcObj.getId())] = funcItem
                self.setupDisplay(funcinfo, funcItem, "Function")

            for cplxObj in find_index(memb, 'cplx'):
                cplxinfo = (cplxObj.parent).path + '/info'
                p = element(cplxObj).parent
                cplxItem = CplxItem(
                    cplxObj, self.mooseId_GObj[
                        element(cplxObj).parent])
                self.mooseId_GObj[element(cplxObj.getId())] = cplxItem
                self.setupDisplay(cplxinfo, cplxItem, "cplx")

        # compartment's rectangle size is calculated depending on children
        self.comptChilrenBoundingRect()

    def comptChilrenBoundingRect(self):
        for k, v in list(self.qGraCompt.items()):
            # compartment's rectangle size is calculated depending on children
            rectcompt = calculateChildBoundingRect(v)
            v.setRect(
                rectcompt.x() - 10,
                rectcompt.y() - 10,
                (rectcompt.width() + 20),
                (rectcompt.height() + 20))
            v.setPen(
                QtGui.QPen(
                    Qt.QColor( 66, 66, 66, 100),
                    self.comptPen,
                    Qt.Qt.SolidLine,
                    Qt.Qt.RoundCap,
                    Qt.Qt.RoundJoin)
                )

    def createCompt(self, key):
        self.new_Compt = ComptItem(self, 0, 0, 0, 0, key)
        self.qGraCompt[key] = self.new_Compt
        self.new_Compt.setRect(10, 10, 10, 10)
        self.sceneContainer.addItem(self.new_Compt)

    def setupDisplay(self, info, graphicalObj, objClass):
        Annoinfo = Annotator(info)
        if objClass in [ "reaction", "cplx", "Function", "StimulusTable" ]:
            textcolor, bgcolor = QColor("white"), QColor("white")
        else:
            textcolor, bgcolor = getColor(info)
            if bgcolor.name() == "#ffffff" or bgcolor == "white":
                bgcolor = getRandColor()
                Annoinfo.color = str(bgcolor.name())

        if isinstance(self, KineticEditorWidget):
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

            self.xylist = [xpos, ypos]
            self.xyCord[moose.element(info).parent] = [xpos, ypos]

        elif isinstance(self, kineticRunWidget):
            self.editormooseId_GObj = self.editor.getCentralWidget().mooseId_GObj
            editorItem = self.editormooseId_GObj[moose.element(info).parent]
            xpos = editorItem.scenePos().x()
            ypos = editorItem.scenePos().y()
            #Annoinfo.x = xpos
            #Annoinfo.y = -ypos
        graphicalObj.setDisplayProperties(xpos, ypos, textcolor, bgcolor)
        #Annoinfo.x = xpos
        #Annoinfo.y = ypos

    def positioninfo(self, iteminfo):
        Anno = moose.Annotator(self.modelRoot + '/info')
        if not self.noPositionInfo:
            try:
                # kkit does exist item's/info which up querying for parent.path
                # gives the information of item's parent
                x, y = self.autoCordinatepos[(element(iteminfo).parent).path]
            except:
                # But in Cspace reader doesn't create item's/info, up on querying gives me the error which need to change\
                # in ReadCspace.cpp, at present i am taking care b'cos i don't want to pass just the item where I need to check\
                # type of the object (rea,pool,enz,cplx,tab) which I have
                # already done.
                parent, child = posixpath.split(iteminfo)
                x, y = self.autoCordinatepos[parent]
            ypos = (y - self.ymin) * self.yratio
        else:
            x = float(element(iteminfo).getField('x'))
            y = float(element(iteminfo).getField('y'))
            # Qt origin is at the top-left corner. The x values increase to the right and the y values increase downwards \
            # as compared to Genesis codinates where origin is center and y value is upwards, that is why ypos is negated
            # if Anno.modeltype == "kkit":
            #     ypos = 1.0-(y-self.ymin)*self.yratio
            # else:
            #     ypos = (y-self.ymin)*self.yratio
            ypos = 1.0 - (y - self.ymin) * self.yratio
        xpos = (x - self.xmin) * self.xratio
        return(xpos, ypos)

    def drawLine_arrow(self, itemignoreZooming=False):
        for inn, out in list(self.srcdesConnection.items()):
            # print "inn ",inn, " out ",out
            # self.srcdesConnection is dictionary which contains key,value \
            #    key is Enzyme or Reaction  and value [[list of substrate],[list of product]] (tuple)
            #    key is Function and value is [list of pool] (list)

            #src = self.mooseId_GObj[inn]
            if isinstance(out, tuple):
                src = self.mooseId_GObj[inn]
                if len(out[0]) == 0:
                    print(
                        inn.className +
                        ' : ' +
                        inn.name +
                        " doesn't output message")
                else:
                    for items in (items for items in out[0]):
                        des = self.mooseId_GObj[element(items[0])]
                        self.lineCord(src, des, items, itemignoreZooming)
                if len(out[1]) == 0:
                    print(
                        inn.className +
                        ' : ' +
                        inn.name +
                        " doesn't output message")
                else:
                    for items in (items for items in out[1]):
                        des = self.mooseId_GObj[element(items[0])]
                        self.lineCord(src, des, items, itemignoreZooming)
            elif isinstance(out, list):
                if len(out) == 0:
                    if inn.className == "StimulusTable":
                        print(inn.name + " doesn't have output")
                    elif inn.className == "ZombieFunction" or inn.className == "Function":
                        print(inn.name + " doesn't have sumtotal ")
                else:
                    src = self.mooseId_GObj[inn]
                    for items in (items for items in out):
                        des = self.mooseId_GObj[element(items[0])]
                        self.lineCord(src, des, items, itemignoreZooming)

    def lineCord(self, src, des, type_no, itemignoreZooming):
        srcdes_list = []
        endtype = type_no[1]
        line = 0
        if (src == "") and (des == ""):
            print("Source or destination is missing or incorrect")
            return
        srcdes_list = [src, des, endtype, line]
        arrow = calcArrow(srcdes_list, itemignoreZooming, self.iconScale)
        self.drawLine(srcdes_list, arrow)

        while(type_no[2] > 1 and line <= (type_no[2] - 1)):
            srcdes_list = [src, des, endtype, line]
            arrow = calcArrow(srcdes_list, itemignoreZooming, self.iconScale)
            self.drawLine(srcdes_list, arrow)
            line = line + 1

        if type_no[2] > 5:
            print("Higher order reaction will not be displayed")

    def drawLine(self, srcdes_list, arrow):
        src = srcdes_list[0]
        des = srcdes_list[1]
        endtype = srcdes_list[2]
        line = srcdes_list[3]
        source = element(
            next(
                (k for k,
                 v in list(
                     self.mooseId_GObj.items()) if v == src),
                None))
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
        pen = QtGui.QPen(
            QtCore.Qt.green,
            0,
            Qt.Qt.SolidLine,
            Qt.Qt.RoundCap,
            Qt.Qt.RoundJoin)
        pen.setWidth(self.arrowsize)
        # Green is default color moose.ReacBase and derivatives - already set
        # above
        if isinstance(source, EnzBase):
            if ((endtype == 's') or (endtype == 'p')):
                pen.setColor(QtCore.Qt.red)
            elif(endtype != 'cplx'):
                p1 = (
                    next(
                        (k for k,
                         v in list(
                             self.mooseId_GObj.items()) if v == src),
                        None))
                pinfo = p1.parent.path + '/info'
                color, bgcolor = getColor(pinfo)
                #color = QColor(color[0],color[1],color[2])
                pen.setColor(bgcolor)

        elif isinstance(source, moose.PoolBase) or isinstance(source, moose.Function):
            pen.setColor(QtCore.Qt.blue)
        elif isinstance(source, moose.StimulusTable):
            pen.setColor(QtCore.Qt.yellow)
        self.lineItem_dict[qgLineitem] = srcdes_list
        self.object2line[src].append((qgLineitem, des, endtype, line))
        self.object2line[des].append((qgLineitem, src, endtype, line))
        qgLineitem.setPen(pen)

    def positionChange(self, mooseObject):
        # If the item position changes, the corresponding arrow's are
        # calculated
        if isinstance(element(mooseObject), ChemCompt):
            for k, v in list(self.qGraCompt.items()):
                mesh = mooseObject
                if k.path == mesh:
                    for rectChilditem in v.childItems():
                        if isinstance(rectChilditem, KineticsDisplayItem):
                            if isinstance(
                                    moose.element(
                                        rectChilditem.mobj.path),
                                    PoolBase):
                                t = moose.element(rectChilditem.mobj.path)
                                moose.element(t).children
                                for items in moose.element(t).children:
                                    if isinstance(
                                            moose.element(items), Function):
                                        test = moose.element(items.path + '/x')
                                        for i in moose.element(
                                                test).neighbors['input']:
                                            j = self.mooseId_GObj[
                                                moose.element(i)]
                                            self.updateArrow(j)
                            self.updateArrow(rectChilditem)
        else:
            mobj = self.mooseId_GObj[element(mooseObject)]
            self.updateArrow(mobj)
            elePath = moose.element(mooseObject).path
            pos = elePath.find('/', 1)
            l = elePath[0:pos]
            linfo = moose.Annotator(l + '/info')
            for k, v in list(self.qGraCompt.items()):
                #rectcompt = v.childrenBoundingRect()
                rectcompt = calculateChildBoundingRect(v)
                comptBoundingRect = v.boundingRect()
                if not comptBoundingRect.contains(rectcompt):
                    self.updateCompartmentSize(v)
                '''
                if linfo.modeltype == "new_kkit":
                    #if newly built model then compartment is size is fixed for some size.
                    comptBoundingRect = v.boundingRect()
                    if not comptBoundingRect.contains(rectcompt):
                        self.updateCompartmentSize(v)
                else:
                    #if already built model then compartment size depends on max and min objects
                    rectcompt = calculateChildBoundingRect(v)
                    v.setRect(rectcompt.x()-10,rectcompt.y()-10,(rectcompt.width()+20),(rectcompt.height()+20))
                '''

    def updateCompartmentSize(self, compartment):
        compartmentBoundary = compartment.rect()
        # print " compartmentBoundary ",compartmentBoundary, "  ",compartment.childrenBoundingRect()
        #compartmentBoundary =compartment.childrenBoundingRect()
        #childrenBoundary    = compartment.childrenBoundingRect()
        # print " 758 ",compartment.childrenBoundaryRect()
        childrenBoundary = calculateChildBoundingRect(compartment)
        # print " ch ",childrenBoundary
        x = min(compartmentBoundary.x(), childrenBoundary.x())
        y = min(compartmentBoundary.y(), childrenBoundary.y())
        width = max(compartmentBoundary.width(), childrenBoundary.width())
        height = max(compartmentBoundary.height(), childrenBoundary.height())
        compartment.setRect(x - 10, y - 10, width + 20, height + 20
                            )

    def updateArrow(self, qGTextitem):
        # if there is no arrow to update then return
        if qGTextitem not in self.object2line:
            return
        listItem = self.object2line[qGTextitem]
        for ql, va, endtype, order in self.object2line[qGTextitem]:
            srcdes = []
            srcdes = self.lineItem_dict[ql]
            # Checking if src (srcdes[0]) or des (srcdes[1]) is ZombieEnz,
            # if yes then need to check if cplx is connected to any mooseObject,
            # so that when Enzyme is moved, cplx connected arrow to other
            # mooseObject(poolItem) should also be updated
            if(isinstance(srcdes[0], EnzItem) or type(srcdes[0] == MMEnzItem)):
                self.cplxUpdatearrow(srcdes[0])
            elif(isinstance(srcdes[1], EnzItem) or type(srcdes[1] == MMEnzItem)):
                self.cplxUpdatearrow(srcdes[1])
            # For calcArrow(src,des,endtype,itemignoreZooming) is to be
            # provided
            arrow = calcArrow(srcdes, self.itemignoreZooming, self.iconScale)
            ql.setPolygon(arrow)

    def cplxUpdatearrow(self, srcdes):
        # srcdes which is 'EnzItem' from this,get ChildItems are retrived (b'cos cplx is child of zombieEnz)
        # And cplxItem is passed for updatearrow
        for item in srcdes.childItems():
            if isinstance(item, CplxItem):
                self.updateArrow(item)

    # def deleteSolver(self):
    #     print " delete Solver"
    #     print "### ",moose.wildcardFind(self.modelRoot+'/data/graph#/#')
    #     if moose.wildcardFind(self.modelRoot+'/##[ISA=ChemCompt]'):
    #         compt = moose.wildcardFind(self.modelRoot+'/##[ISA=ChemCompt]')
    #         print " deletSolver ",
    #         # print moose.exists(compt[0].path+'/stoich'), " ksolve ", moose.exists(compt[0].path+'/ksolve')
    #         # print "gsolve ", moose.delete( compt[0].path+'/gsolve' )
    #         if ( moose.exists( compt[0].path+'/stoich' ) ):
    #             #print "delete"
    #             moose.delete( compt[0].path+'/stoich' )
    #         if ( moose.exists( compt[0].path+'/ksolve' ) ):
    #             moose.delete( compt[0].path+'/ksolve' )
    #         if ( moose.exists( compt[0].path+'/gsolve' ) ):
    #             moose.delete( compt[0].path+'/gsolve' )
    #         for x in moose.wildcardFind( self.modelRoot+'/data/graph#/#' ):
    #                 x.tick = -1
    def positionChange1(self, mooseObject):
        # If the item position changes, the corresponding arrow's are
        # calculated
        if ((isinstance(element(mooseObject), CubeMesh))
                or (isinstance(element(mooseObject), CylMesh))):
            v = self.qGraCompt[mooseObject]
            for rectChilditem in v.childItems():
                self.updateArrow(rectChilditem)
        else:
            mobj = self.mooseId_GObj[mooseObject.getId()]
            self.updateArrow(mobj)
            mooseObjcompt = self.findparent(mooseObject)
            v = self.qGraCompt[mooseObjcompt]
            #childBoundingRect = v.childrenBoundingRect()
            childBoundingRect = calculateChildBoundingRect(v)
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


class KineticEditorWidget(KineticsWidget):

    def __init__(self, plugin, *args):

        KineticsWidget.__init__(self, plugin, *args)
        self.plugin = plugin
        self.insertMenu = QtGui.QMenu('&Insert')
        self._menus.append(self.insertMenu)
        self.insertMapper = QtCore.QSignalMapper(self)
        classlist = [
            'CubeMesh',
            'CylMesh',
            'Pool',
            'BufPool',
            'Function',
            'Reac',
            'Enz',
            'MMenz',
            'StimulusTable']
        self.toolTipinfo = TooltipInfo.tooltip_info_dict_
        insertMapper, actions = self.getInsertActions(classlist)
        for action in actions:
            self.insertMenu.addAction(action)
            doc = self.toolTipinfo[str(action.text())]
            if doc == "":
                classname = str(action.text())
                doc = moose.element('/classes/%s' % (classname)).docs
                doc = doc.split('Description:')[-1].split('Name:')[0].strip()
            action.setToolTip(doc)

        # Set size policy
        self.setMinimumSize( 1000, 1000 )
        self.setSizePolicy( 
                QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding 
                )

    def makePoolItem(self, poolObj, qGraCompt):
        return PoolItem(poolObj, qGraCompt)

    def rescaleView( self ):
        """Rescale when outerboundries are crowded. But not too much

        NOTE: The size policy should take care of this.
        
        """
        pass

    def getToolBars(self):
        # Add specific tool items with respect to kkit
        if not hasattr(self, '_insertToolBar'):
            self._insertToolBar = QtGui.QToolBar('Insert')
            self._toolBars.append(self._insertToolBar)
            for action in self.insertMenu.actions():
                button = MToolButton()
                button.setDefaultAction(action)
                # set the unicode instead of image by setting
                # button.setText(unicode(u'\u20de'))
                Iconpath = os.path.join(config.MOOSE_ICON_DIR, 'classIcon')
                _logger.debug( "Reading icons from %s" % Iconpath )
                button.setIcon( 
                        QtGui.QIcon( 
                            os.path.join(Iconpath, '%s' % action.text() + ".png")
                            )
                        )
                self._insertToolBar.addWidget(button)
        return self._toolBars


class kineticRunWidget(KineticsWidget):

    def __init__(self, plugin, *args):
        KineticsWidget.__init__(self, plugin, *args)

    def showEvent(self, event):
        self.refresh()
        # pass

    def refresh(self):
        self.sceneContainer.clear()
        self.Comptexist = wildcardFind(self.modelRoot + '/##[ISA=ChemCompt]')
        if self.Comptexist:
            # pass
            self.getMooseObj()
            self.mooseObjOntoscene()
            self.drawLine_arrow(itemignoreZooming=False)

    def makePoolItem(self, poolObj, qGraCompt):
        return PoolItemCircle(poolObj, qGraCompt)

    def getToolBars(self):
        return self._toolBars

    def updateValue(self):
        for item in list(self.sceneContainer.items()):
            if isinstance(
                item,
                ReacItem) or isinstance(
                item,
                MMEnzItem) or isinstance(
                item,
                EnzItem) or isinstance(
                    item,
                    PoolItemCircle) or isinstance(
                        item,
                    CplxItem):
                item.updateValue(item.mobj)

    def changeBgSize(self):
        for item in list(self.sceneContainer.items()):
            if isinstance(item, PoolItemCircle):
                initialConc = moose.element(item.mobj).concInit
                presentConc = moose.element(item.mobj).conc
                if initialConc != 0:
                    ratio = presentConc / initialConc
                else:
                    # multipying by 1000 b'cos moose concentration is in milli
                    # in moose
                    ratio = presentConc
                if ratio > 10:
                    ratio = 9
                if ratio < 0.0:
                    ratio = 0.1
                item.updateRect(math.sqrt(abs(ratio)))

    def resetColor(self):
        for item in list(self.sceneContainer.items()):
            if isinstance(item, PoolItemCircle):
                item.returnEllispeSize()


# if __name__ == "__main__":
#     app = QtGui.QApplication(sys.argv)
#     size = QtCore.QSize(1024 ,768)
#     modelPath = 'acc27'
#     itemignoreZooming = False
#     try:
#         filepath = '../../Demos/Genesis_files/'+modelPath+'.g'
#         filepath = '/home/harsha/genesis_files/gfile/'+modelPath+'.g'
#         print(filepath)
#         f = open(filepath, "r")
#         loadModel(filepath,'/'+modelPath)
#
#         #moose.le('/'+modelPath+'/kinetics')
#         dt = KineticsWidget()
#         dt.modelRoot ='/'+modelPath
#         ''' Loading moose signalling model in python '''
#         #execfile('/home/harsha/BuildQ/Demos/Genesis_files/scriptKineticModel.py')
#         #dt.modelRoot = '/model'
#
#         dt.updateModelView()
#         dt.show()
#
#     except  IOError as what:
#       (errno, strerror) = what
#       print("Error number",errno,"(%s)" %strerror)
#       sys.exit(0)
#     sys.exit(app.exec_())
#
