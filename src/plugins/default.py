# default.py ---
#
# Filename: default.py
# Description:
# Author: Subhasis Ray
# Maintainer:
# Created: Tue Nov 13 15:58:31 2012 (+0530)
# Version:
# Last-Updated: Mon Sep 10 23:35:00 2018 (+0530)
#           By: Harsha
#     Update #: 
# URL:
# Keywords:
# Compatibility:
#
#

# Commentary:
#
# The default placeholder plugin for MOOSE
#
#

# Change log:
#
#
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth
# Floor, Boston, MA 02110-1301, USA.
#
#

# Code:
'''
2018
Sep 10: replace addSolver to mooseAddChemSolver from moose.chemUtil's
2013
Oct 5: could not recreate if object already exist in moose which was allowed earlier
        now if object exist need to use element which is cleaned here

'''
import sys
import pickle
import os
from collections import defaultdict
import numpy as np

from matplotlib import rcParams
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
rcParams.update({'figure.autolayout': True})

import moose
from moose import utils

import moosegui.mtree as mtree
from moosegui.mtoolbutton import MToolButton
from moosegui.msearch import SearchWidget
from moosegui.checkcombobox import CheckComboBox
from moosegui import config
from moosegui.mplugin import MoosePluginBase, EditorBase, EditorWidgetBase, PlotBase, RunBase
from moosegui.PlotWidgetContainer import PlotWidgetContainer
from moosegui.plugins.kkitUtil import getColor
from moosegui.plugins.Runner import Runner
from moosegui.global_constants import preferences
from moosegui.plugins.setsolver import *

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDoubleValidator
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QToolButton
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QErrorMessage
from PyQt4.QtGui import QSizeGrip
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QAction
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
#from EventBlocker import EventBlocker
# from PlotNavigationToolbar import PlotNavigationToolbar
from global_constants import preferences
#from setsolver import *
from moose.chemUtil.add_Delete_ChemicalSolver import *

ELECTRICAL_MODEL = 0
CHEMICAL_MODEL   = 1

class MoosePlugin(MoosePluginBase):
    """Default plugin for MOOSE GUI"""
    def __init__(self, root, mainwindow):
        MoosePluginBase.__init__(self, root, mainwindow)

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
            self.editorView = MooseEditorView(self)
            #signal to objecteditor from default plugin
            self.editorView.getCentralWidget().editObject.connect(self.mainWindow.objectEditSlot)
            self.currentView = self.editorView
        return self.editorView

    def getPlotView(self):
        if not hasattr(self, 'plotView'):
            self.plotView = PlotView(self)
        return self.plotView

    def getRunView(self):

        if not hasattr(self, 'runView') or self.runView is None:
            self.runView = RunView(self.modelRoot, self)
        return self.runView

    def getMenus(self):
        """Create a custom set of menus."""
        return self._menus


class MooseEditorView(EditorBase):
    """Default editor.

    """
    def __init__(self, plugin):
        EditorBase.__init__(self, plugin)
        self.__initMenus()
        self.__initToolBars()

    def __initMenus(self):
        editMenu = QtGui.QMenu('&Edit')
        for menu in self.getCentralWidget().getMenus():
            editMenu.addMenu(menu)
        self._menus.append(editMenu)

    def __initToolBars(self):
        for toolbar in self.getCentralWidget().getToolBars():
            self._toolBars.append(toolbar)

    def getToolPanes(self):
        return super(MooseEditorView, self).getToolPanes()

    def getLibraryPane(self):
        return super(MooseEditorView, self).getLibraryPane()

    def getOperationsWidget(self):
        return super(MooseEditorView, self).getOperationsPane()

    def getCentralWidget(self):
        """Retrieve or initialize the central widget.

        Note that we call the widget's setModelRoot() function
        explicitly with the plugin's modelRoot as the argument. This
        enforces an update of the widget display with the current
        modelRoot.

        This function should be overridden by any derived class as it
        has the editor widget class hard coded into it.

        """
        if self._centralWidget is None:
            self._centralWidget = DefaultEditorWidget()
        if hasattr(self._centralWidget, 'init'):
            self._centralWidget.init()
            self._centralWidget.setModelRoot(self.plugin.modelRoot)
        return self._centralWidget


class MooseTreeEditor(mtree.MooseTreeWidget):
    """Subclass of MooseTreeWidget to implement drag and drop events. It
    creates an element under the drop location using the dropped mime
    data as class name.

    """
    def __init__(self, *args):
        mtree.MooseTreeWidget.__init__(self, *args)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Insert an element of the specified class in drop location"""
        if not event.mimeData().hasFormat('text/plain'):
            return
        pos = event.pos()
        item = self.itemAt(pos)
        try:
            self.insertChildElement(item, str(event.mimeData().text()))
            event.acceptProposedAction()
        except NameError:
            return


class DefaultEditorWidget(EditorWidgetBase):
    """Editor widget for default plugin.

    Plugin-writers should code there own editor widgets derived from
    EditorWidgetBase.

    It adds a toolbar for inserting moose objects into the element
    tree. The toolbar contains MToolButtons for moose classes.

    Signals: editObject - inherited from EditorWidgetBase , emitted
    with currently selected element's path as argument. Should be
    connected to whatever slot is responsible for firing the object
    editor in top level.

    """
    def __init__(self, *args):
        EditorWidgetBase.__init__(self, *args)
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
        self.tree = MooseTreeEditor()
        self.tree.setAcceptDrops(True)
        self.getTreeMenu()
        self.layout().addWidget(self.tree)

    def getTreeMenu(self):
        try:
            return self.treeMenu
        except AttributeError:
            self.treeMenu = QtGui.QMenu()

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(lambda : self.treeMenu.exec_(QtGui.QCursor.pos()) )
        # Inserting a child element
        self.insertMenu = QtGui.QMenu('Insert')
        self._menus.append(self.insertMenu)
        self.treeMenu.addMenu(self.insertMenu)
        self.insertMapper = QtCore.QSignalMapper(self)
        ignored_bases = ['ZPool', 'Msg', 'Panel', 'SolverBase', 'none']
        ignored_classes = ['ZPool','ZReac','ZMMenz','ZEnz','CplxEnzBase']
        classlist = [ch[0].name for ch in moose.element('/classes').children
                     if (ch[0].baseClass not in ignored_bases)
                     and (ch[0].name not in (ignored_bases + ignored_classes))
                     and not ch[0].name.startswith('Zombie')
                     and not ch[0].name.endswith('Base')
                 ]
        insertMapper, actions = self.getInsertActions(classlist)
        for action in actions:
            self.insertMenu.addAction(action)
        self.connect(insertMapper, QtCore.SIGNAL('mapped(const QString&)'), self.tree.insertElementSlot)
        self.editAction = QtGui.QAction('Edit', self.treeMenu)
        self.editAction.triggered.connect(self.editCurrentObjectSlot)
        self.tree.elementInserted.connect(self.elementInsertedSlot)
        self.treeMenu.addAction(self.editAction)
        return self.treeMenu

    def updateModelView(self):
        self.tree.recreateTree(root=self.modelRoot)
        # if current in self.tree.odict:
        #     self.tree.setCurrentItem(current)

    def updateItemSlot(self, mobj):
        """This should be overridden by derived classes to connect appropriate
        slot for updating the display item.

        """
        self.tree.updateItemSlot(mobj)

    def editCurrentObjectSlot(self):
        """Emits an `editObject(str)` signal with moose element path of
        currently selected tree item as argument

        """
        mobj = self.tree.currentItem().mobj
        self.editObject.emit(mobj.path)

    def sizeHint(self):
        return QtCore.QSize(400, 300)

    def getToolBars(self):
        if not hasattr(self, '_insertToolBar'):
            self._insertToolBar = QtGui.QToolBar('Insert')
            return self._toolBars
            for action in self.insertMenu.actions():
                button = MToolButton()
                button.setDefaultAction(action)
                self._insertToolBar.addWidget(button)
            self._toolBars.append(self._insertToolBar)
        return self._toolBars


############################################################
#
# View for running a simulation and runtime visualization
#
############################################################
from moosegui.mplot import CanvasWidget

class RunView(RunBase):
    """A default runtime view implementation. This should be
    sufficient for most common usage.

    canvas: widget for plotting

    dataRoot: location of data tables

    """
    def __init__(self, modelRoot, *args, **kwargs):
        RunBase.__init__(self, *args, **kwargs)
        self.modelRoot = modelRoot
        if modelRoot != "/":
            self.dataRoot = modelRoot + '/data'
        else:
            self.dataRoot = "/data"
        if not moose.exists(self.plugin.modelRoot):
            moose.Neutral(self.plugin.modelroot)
        self.setModelRoot(moose.element(self.plugin.modelRoot).path)
        if not moose.exists('/data'):
            moose.Neutral('/data')
        self.setDataRoot(moose.element('/data').path)
        if not moose.exists(self.plugin.modelRoot):
            moose.Neutral(self.plugin.modelRoot)
        self.setDataRoot(moose.element(self.plugin.modelRoot).path)
        self.plugin.modelRootChanged.connect(self.setModelRoot)
        self.plugin.dataRootChanged.connect(self.setDataRoot)
        # self.getCentralWidget()
        self._menus += self.getCentralWidget().getMenus()

    def getCentralWidget(self):
        """TODO: replace this with an option for multiple canvas
        tabs"""
        if self._centralWidget is None:
            self._centralWidget = PlotWidgetContainer(self.modelRoot)
        return self._centralWidget

    def setDataRoot(self, path):
        self.dataRoot = path

    def setModelRoot(self, path):
        self.modelRoot = path

    def getDataTablesPane(self):
        """This should create a tree widget with dataRoot as the root
        to allow visual selection of data tables for plotting."""
        raise NotImplementedError()

    def plotAllData(self):
        """This is wrapper over the same function in PlotWidget."""
        self.centralWidget.plotAllData()

    def getToolPanes(self):
        return []
        if not self._toolPanes:
            self._toolPanes = [self.getSchedulingDockWidget()]
        return self._toolPanes

    def getSchedulingDockWidget(self):
        """Create and/or return a widget for schduling"""
        if hasattr(self, 'schedulingDockWidget')  and self.schedulingDockWidget is not None:
            return self.schedulingDockWidget
        self.schedulingDockWidget = QtGui.QDockWidget('Scheduling')
        self.schedulingDockWidget.setFeatures( QtGui.QDockWidget.NoDockWidgetFeatures);
        self.schedulingDockWidget.setWindowFlags(Qt.CustomizeWindowHint)
        titleWidget = QtGui.QWidget();
        self.schedulingDockWidget.setTitleBarWidget(titleWidget)
        widget = SchedulingWidget()
        widget.setDataRoot(self.dataRoot)
        widget.setModelRoot(self.modelRoot)
        self.schedulingDockWidget.setWidget(widget)
        widget.runner.simulationStarted.connect(self._centralWidget.extendXAxes)
        widget.runner.simulationProgressed.connect(self._centralWidget.updatePlots)
        widget.runner.simulationFinished.connect(self._centralWidget.rescalePlots)
        # widget.runner.simulationContinued.connect(self._centralWidget.extendXAxes)
        widget.runner.simulationReset.connect(self._centralWidget.plotAllData)
        self._toolBars += widget.getToolBars()
        return self.schedulingDockWidget


class SchedulingWidget(QtGui.QWidget):
    """Widget for scheduling.

    Important member fields:

    runner - object to run/pause/continue simulation. Whenever
    `updateInterval` time has been simulated this object sends an
    `update()` signal. This can be connected to other objects to
    update their data.

    SIGNALS:
    resetAndRun(tickDt, tickTargets, simtime, updateInterval)

        tickDt: dict mapping tick nos to dt
        tickTargets: dict mapping ticks to target paths
        simtime: total simulation runtime
        updateInterval: interval between update signals are to be emitted.

    simtimeExtended(simtime)
        emitted when simulation time is increased by user.

    """

    resetAndRun = QtCore.pyqtSignal(dict, dict, float, float, name='resetAndRun')
    simtimeExtended = QtCore.pyqtSignal(float, name='simtimeExtended')
    continueRun = QtCore.pyqtSignal(float, float, name='continueRun')

    def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args, **kwargs)
        self.simulationInterval = None
        self.updateInterval     = None
        self.runTime            = None

        self.modelRoot                  = None
        self.dataRoot                   = None
        self.runner                     = Runner()
        self.resetAndRunAction          = None
        self.stopAction                 = None
        self.continueAction             = None
        self.preferences                = preferences
        self.currentSimulationRuntime   = None
        self.modelType                  = None
        self.simulationRuntime          = None
        self.schedulerToolBar           = self.getSchedulerToolBar()
        self.runner.simulationProgressed.connect(self.updateCurrentSimulationRuntime)
        self.continueFlag               = False
        self.preferences.applyChemicalSettings.connect(self.resetSimulation)

    def updateCurrentSimulationRuntime(self, time):
        self.currentSimulationRuntime.setText(str(time))

    def getToolBars(self):
        return [self.schedulerToolBar]

    def getSchedulerToolBar(self):

        bar = QToolBar("Run", self)

        self.resetAction = bar.addAction( 
                QIcon( os.path.join( config.MOOSE_ICON_DIR, 'reset.png' ) )
                , 'Reset'
                , self.resetSimulation
                )
        self.resetAction.setToolTip('Reset simulation.')

        self.runAction = bar.addAction( 
                QIcon( os.path.join( config.MOOSE_ICON_DIR, 'run.png') )
                , 'Run'
                , self.runSimulation
                )
        self.runAction.setToolTip('Run simulation.')


        self.stopAction = bar.addAction( 
                QIcon( os.path.join( config.MOOSE_ICON_DIR,  'stop.png') )
                , 'Stop'
                , self.runner.togglePauseSimulation
                )
        self.stopAction.setToolTip('Stop simulation.')

        bar.addSeparator()

        runtimeLabel = QLabel('Run for')
        self.simulationRuntime = QLineEdit()
        self.simulationRuntime.setValidator(QDoubleValidator())
        self.simulationRuntime.setFixedWidth(75)
        bar.addWidget(runtimeLabel)
        bar.addWidget(self.simulationRuntime)
        bar.addWidget(QLabel(' (s)'))
        bar.addSeparator()

        #: current time
        self.currentSimulationRuntime = QLineEdit() # 6 digits
        self.currentSimulationRuntime.setToolTip('Current simulation runtime.')
        self.currentSimulationRuntime.setFixedWidth(75)
        self.currentSimulationRuntime.setValidator(QDoubleValidator())
        self.currentSimulationRuntime.setText("0.0")
        self.currentSimulationRuntime.setReadOnly(True)

        # self.runner.currentTime.connect(self.currentTimeWidget.display)
        bar.addWidget(QLabel("Current Time : "))
        bar.addWidget(self.currentSimulationRuntime)
        bar.addWidget(QLabel(" (s)"))

        bar.addSeparator()

        self.preferencesButton = QToolButton()
        self.preferencesButton.setText("Preferences")
        self.preferencesButton.clicked.connect(self.preferencesToggler)

        bar.addWidget(self.preferencesButton)
        return bar


    def continueSimulation(self):
        self.runner.continueSimulation( self.runTime
                                      , self.updateInterval
                                      , self.simulationInterval
                                      )
        self.simulationRuntime.setText(str(float(self.simulationRuntime.text()) + self.runTime))

    def resetSimulation(self):
        self.setParameters()
        try:
            self.runtime = float(runtime)
        except:
            self.runtime = 100.0
        # print(self.runTime)
        # print(self.updateInterval)
        # print(self.simulationInterval)
        self.currentSimulationRuntime.setText("0.0")
        self.checkConsistency()
        # self.preferences.setChemicalClocks()
        self.simulationRuntime.setText(str(self.runTime))
        self.runner.resetSimulation( self.runTime
                                   , self.updateInterval
                                   , self.simulationInterval
                                   )
        self.continueFlag               = False

    def runSimulation(self):
        if self.modelType == CHEMICAL_MODEL:
            compt = moose.wildcardFind(self.modelRoot+'/##[ISA=ChemCompt]')
            if not moose.exists(compt[0].path+'/stoich'):
                chemPref = self.preferences.getChemicalPreferences()
                solver = chemPref["simulation"]["solver"]
                mooseAddChemSolver(self.modelRoot,solver)
            status = self.solverStatus()
            #print "status ",status
                   # if status != 0 or status == -1:
            #     return
            if status == None or int(status) == -1 or int(status) == 0:
                #allow the model to Run
                pass
            else:
                # if something is dangling or solver is not set then return
                return
        runtime = str(self.simulationRuntime.text())
        try:
            self.runtime = float(runtime)
        except:
            self.runtime = 100.0
            self.simulationRuntime.setText("100.0")
        self.checkConsistency()
        self.continueSimulation = True
        self.runner.runSimulation(self.runtime)

    def setParameters(self):
        if self.modelType == ELECTRICAL_MODEL:
            self.setElectricalParameters()
        elif self.modelType == CHEMICAL_MODEL:
            self.setChemicalParameters()

    def setChemicalParameters(self):
        chemicalPreferences   = self.preferences.getChemicalPreferences()
        self.preferences.initializeChemicalClocks()
        self.updateInterval     = chemicalPreferences["simulation"]["gui-update-interval"]
        self.simulationInterval = chemicalPreferences["simulation"]["simulation-dt"]
        if str(self.simulationRuntime.text()) == "":
            self.simulationRuntime.setText(str(chemicalPreferences["simulation"]["default-runtime"]))
        self.runTime            = float(self.simulationRuntime.text())
        self.solver             = chemicalPreferences["simulation"]["solver"]

    def setElectricalParameters(self):
        electricalPreferences   = self.preferences.getElectricalPreferences()
        self.preferences.initializeElectricalClocks()
        self.updateInterval     = electricalPreferences["simulation"]["gui-update-interval"]
        self.simulationInterval = electricalPreferences["simulation"]["simulation-dt"]
        if str(self.simulationRuntime.text()) == "":
            self.simulationRuntime.setText(str(electricalPreferences["simulation"]["default-runtime"]))
        self.runTime            = float(self.simulationRuntime.text())
        self.solver             = electricalPreferences["simulation"]["solver"]

    def checkConsistency(self):
        if self.updateInterval < self.simulationInterval :
            self.updateInterval = self.simulationInterval
        if self.runTime < self.updateInterval :
            self.runTime = self.updateInterval
        return True

    def solverStatus(self):
        compt = moose.wildcardFind(self.modelRoot+'/##[ISA=ChemCompt]')
        if not moose.exists(compt[0].path+'/stoich'):
            return None
        else:
            stoich = moose.Stoich(compt[0].path+'/stoich')
            status = int(stoich.status)
            # Flag to track status of Stoich object.
            # -1: No path yet assigned.
            # 0: Success
            # 1: Warning: Missing reactant in Reac or Enz
            # 2: Warning: Missing substrate in MMenz
            # 4: Warning: Compartment not defined
            # 8: Warning: Neither Ksolve nor Dsolve defined
            # 16: Warning: No objects found on path

            # print("Status =>", status)

            if status == 1 or status == 2:
                nameRE = "\n\nclassName --> parentName/groupName --> name  "
                for res in moose.wildcardFind(self.modelRoot+'/##[ISA=ReacBase],'+self.modelRoot+'/##[ISA=EnzBase]'):
                    if not len(res.neighbors["sub"]) or not len(res.neighbors["prd"]):
                        nameRE = nameRE+"\n "+res.className + " --> "+res.parent.name+ " --> "+res.name

            if status == -1:
                QtGui.QMessageBox.warning(None,"Could not Run the model","Warning: Reaction path not yet assigned.\n ")
                return -1
            if status == 1:
                #QtGui.QMessageBox.warning(None,"Could not Run the model","Warning: Missing a reactant in a Reac or Enz.\n ")
                QtGui.QMessageBox.warning(None,"Could not Run the model","Warning: Missing a reactant in %s " %(nameRE))
                return 1
            elif status == 2:
                QtGui.QMessageBox.warning(None,"Could not Run the model","Warning: Missing a substrate in an MMenz %s " %(nameRE))
                #QtGui.QMessageBox.warning(None,"Could not Run the model","Warning: Missing a substrate in an MMenz.\n ")
                return 2
            elif status == 4:
                QtGui.QMessageBox.warning(None,"Could not Run the model"," Warning: Compartment not defined.\n ")
                return 4
            elif status == 8:
                QtGui.QMessageBox.warning(None,"Could not Run the model","Warning: Neither Ksolve nor Dsolve defined.\n ")
                return 8
            elif status == 16:
                QtGui.QMessageBox.warning(None,"Could not Run the model","Warning: No objects found on path.\n ")
                return 16
            elif status == 0:
                print("Successfully built stoichiometry matrix.\n ")
                # moose.reinit()
                return 0

    def __getAdvanceOptionsButton(self):
        icon = QtGui.QIcon(os.path.join(config.settings[config.KEY_ICON_DIR],'arrow.png'))
        # self.advancedOptionsButton.setIcon(QtGui.QIcon(icon))
        # self.advancedOptionsButton.setToolButtonStyle( Qt.ToolButtonTextBesideIcon );
        return self.advancedOptionsButton

    def preferencesToggler(self):
        visibility = not self.preferences.getView().isVisible()
        self.preferences.getView().setVisible(visibility)

    def continueSlot(self):
        pass

    def updateCurrentTime(self):
        sys.stdout.flush()
        self.currentTimeWidget.dispay(str(moose.Clock('/clock').currentTime))

    def updateTextFromTick(self, tickNo):
        tick = moose.vector('/clock/tick')[tickNo]
        widget = self.tickListWidget.layout().itemAtPosition(tickNo + 1, 1).widget()
        if widget is not None and isinstance(widget, QtGui.QLineEdit):
            widget.setText(str(tick.dt))

    def updateFromMoose(self):
        """Update the tick dt from the tick objects"""
        ticks = moose.vector('/clock/tick')
        # Items at position 0 are the column headers, hence ii+1
        for ii in range(ticks[0].localNumField):
            self.updateTextFromTick(ii)
        self.updateCurrentTime()

    def getSimTime(self):
        try:
            time = float(str(self.simtimeEdit.text()))
            return time
        except ValueError as e:
            QtGui.QMessageBox.warning(self, 'Invalid value', 'Specified runtime was meaningless.')
        return 0


    def setDataRoot(self, root='/data'):
        self.dataRoot = moose.element(root).path

    def setModelRoot(self, root='/model'):
        self.modelRoot = moose.element(root).path
        self.setModelType()

    def setModelType(self):
        if moose.exists(self.modelRoot + "/model/cells"):
            self.modelType = ELECTRICAL_MODEL
        else:
            self.modelType = CHEMICAL_MODEL
        self.resetSimulation()

from collections import namedtuple

# Keeps track of data sources for a plot. 'x' can be a table path or
# '/clock' to indicate time points from moose simulations (which will
# be created from currentTime field of the `/clock` element and the
# number of dat points in 'y'. 'y' should be a table. 'z' can be empty
# string or another table or something else. Will not be used most of
# the time (unless 3D or heatmap plotting).

PlotDataSource = namedtuple('PlotDataSource', ['x', 'y', 'z'], verbose=False)
event = None
legend = None
canvas = None

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QSizeGrip
from PyQt4.QtGui import QLayout
from PyQt4.QtGui import QScrollArea
from PyQt4.QtGui import QMenu
from PyQt4.QtCore import pyqtSlot,SIGNAL,SLOT, Signal, pyqtSignal

class PlotWidget(QWidget):
    """A wrapper over CanvasWidget to handle additional MOOSE-specific
    stuff.

    modelRoot - path to the entire model our plugin is handling

    dataRoot - path to the container of data tables.

    pathToLine - map from moose path to Line2D objects in plot. Can
    one moose table be plotted multiple times? Maybe yes (e.g., when
    you want multiple other tables to be compared with the same data).

    lineToDataSource - map from Line2D objects to moose paths

    """

    widgetClosedSignal = pyqtSignal(object)
    addGraph           = pyqtSignal(object)

    def __init__(self, model, graph, index, parentWidget, *args, **kwargs):
        super(PlotWidget, self).__init__()
        self.model = model
        self.graph = graph
        self.index = index

        self.menu = self.getContextMenu()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect( self
                    , SIGNAL("customContextMenuRequested(QPoint)")
                    , self
                    , SLOT("contextMenuRequested(QPoint)")
                    )

        self.canvas = CanvasWidget(self.model, self.graph, self.index)
        self.canvas.setParent(self)
        self.navToolbar = NavigationToolbar(self.canvas, self)
        self.hackNavigationToolbar()
        self.canvas.mpl_connect('pick_event',self.togglePlot)
        layout = QtGui.QGridLayout()
        layout.addWidget(self.navToolbar, 0, 0)
        layout.addWidget(self.canvas, 1, 0)
        self.setLayout(layout)
        self.pathToLine = defaultdict(set)
        self.lineToDataSource = {}
        self.axesRef = self.canvas.addSubplot(1, 1)
        self.legend  = None
        desktop = QtGui.QApplication.desktop()
        self.setMinimumSize(desktop.screenGeometry().width() / 4, desktop.screenGeometry().height() / 3)
        self.canvas.updateSignal.connect(self.plotAllData)
        self.plotAllData()

    def hackNavigationToolbar(self):
        # ADD Graph Action
        pixmap = QPixmap(
                os.path.join( config.MOOSE_ICON_DIR, 'add_graph.png' )
                )
        icon   = QIcon(pixmap)
        action  = QAction(icon, "Add a graph", self.navToolbar)
        # self.navToolbar.addAction(action)
        action.triggered.connect( self.addGraph.emit )
        self.navToolbar.insertAction(self.navToolbar.actions()[0], action)

        # Delete Graph Action
        pixmap = QPixmap( os.path.join( config.MOOSE_ICON_DIR,
            "delete_graph.png") )
        icon   = QIcon(pixmap)
        action  = QAction(icon, "Delete this graph", self.navToolbar)
        action.triggered.connect(self.delete)
        self.navToolbar.insertAction(self.navToolbar.actions()[1], action)

        #Toggle Grid Action
        pixmap = QPixmap(
                os.path.join( config.MOOSE_ICON_DIR, "grid.png" )
                )
        icon   = QIcon(pixmap)
        action  = QAction(icon, "Toggle Grid", self.navToolbar)
        action.triggered.connect(self.canvas.toggleGrid)
        self.navToolbar.insertAction(self.navToolbar.actions()[2], action)
        self.navToolbar.insertSeparator(self.navToolbar.actions()[3])


    @property
    def plotAll(self):
        return len(self.pathToLine) == 0

    def toggleLegend(self):
        if self.legend is not None:
            self.legend.set_visible(not self.legend.get_visible())
        self.canvas.draw()

    def getContextMenu(self):
        menu =  QMenu()
        # closeAction      = menu.addAction("Delete")
        exportCsvAction = menu.addAction("Export to CSV")
        exportCsvAction.triggered.connect(self.saveAllCsv)
        toggleLegendAction = menu.addAction("Toggle legend")
        toggleLegendAction.triggered.connect(self.toggleLegend)
        self.removeSubmenu = menu.addMenu("Remove")
        # configureAction.triggered.connect(self.configure)
        # self.connect(,SIGNAL("triggered()"),
        #                 self,SLOT("slotShow500x500()"))
        # self.connect(action1,SIGNAL("triggered()"),
        #                 self,SLOT("slotShow100x100()"))

        return menu

    def deleteGraph(self):
        """ If there is only one graph in the view, please don't delete it """
        print( "Deleting %s " % self.graph.path)
        moose.delete(self.graph.path)

    def delete(self, event):
        """FIXME: The last element should not be deleted """
        _logger.info("Deleting PlotWidget " )
        self.deleteGraph()
        self.close()
        self.widgetClosedSignal.emit(self)

    def configure(self, event):
        print("Displaying configure view!")
        self.plotView.getCentralWidget().show()

    @pyqtSlot(QtCore.QPoint)
    def contextMenuRequested(self,point):
        self.menu.exec_(self.mapToGlobal(point))

    def setModelRoot(self, path):
        self.modelRoot = path

    def setDataRoot(self, path):
        self.dataRoot = path
        #plotAllData()

    def genColorMap(self,tableObject):
        species = tableObject+'/info'
        colormap_file = open(os.path.join(config.settings[config.KEY_COLORMAP_DIR], 'rainbow2.pkl'),'rb')
        self.colorMap = pickle.load(colormap_file)
        colormap_file.close()
        hexchars = "0123456789ABCDEF"
        color = 'white'
        #Genesis model exist the path and color will be set but not xml file so bypassing
        #print "here genColorMap ",moose.exists(species)
        if moose.exists(species):
            color = moose.element(species).getField('color')
            if ((not isinstance(color,(list,tuple)))):
                if color.isdigit():
                    tc = int(color)
                    tc = (tc * 2 )
                    r,g,b = self.colorMap[tc]
                    color = "#"+ hexchars[r / 16] + hexchars[r % 16] + hexchars[g / 16] + hexchars[g % 16] + hexchars[b / 16] + hexchars[b % 16]
            else:
                color = 'white'
        return color

    def removePlot(self, table):
        print(("removePlot =>", table))
        moose.delete(table)
        self.plotAllData()

    def makeRemovePlotAction(self, label, table):
        action = self.removeSubmenu.addAction(label)
        action.triggered.connect(lambda: self.removePlot(table))
        return action

    def plotAllData(self):
        """Plot data from existing tables"""
        self.axesRef.lines = []
        self.pathToLine.clear()
        self.removeSubmenu.clear()
        if self.legend is not None:
            self.legend.set_visible(False)
        path = self.model.path
        modelroot = self.model.path
        time = moose.Clock('/clock').currentTime
        tabList = []
        #for tabId in moose.wildcardFind('%s/##[TYPE=Table]' % (path)):
        #harsha: policy graphs will be under /model/modelName need to change in kkit
        #for tabId in moose.wildcardFind('%s/##[TYPE=Table]' % (modelroot)):

        plotTables = list(moose.wildcardFind(self.graph.path + '/##[TYPE=Table]'))
        plotTables.extend(moose.wildcardFind(self.graph.path + '/##[TYPE=Table2]'))
        if len (plotTables) > 0:
            for tabId in plotTables:
                tab = moose.Table(tabId)
                #print("Table =>", tab)
                line_list=[]
                tableObject = tab.neighbors['requestOut']
                # Not a good way
                #tableObject.msgOut[0]
                if len(tableObject) > 0:

                    # This is the default case: we do not plot the same
                    # table twice. But in special cases we want to have
                    # multiple variations of the same table on different
                    # axes.
                    #
                    #Harsha: Adding color to graph for signalling model, check if given path has cubemesh or cylmesh

                    color = '#FFFFFF'
                    if moose.exists(tableObject[0].path + '/info'):
                        color = getColor(tableObject[0].path + '/info')
                        color = str(color[1].name()).upper()

                    lines = self.pathToLine[tab.path]
                    if len(lines) == 0:
                        #Harsha: pass color for plot if exist and not white else random color
                        #print "tab in plotAllData ",tab, tab.path,tab.name
                        field = tab.path.rpartition(".")[-1]
                        if field.endswith("[0]") or field.endswith("_0_"):
                            field = field[:-3]
                        # label = ( tableObject[0].path.partition(self.model.path + "/model[0]/")[-1]
                        #         + "."
                        #         + field
                        #         )
                        label = ( tableObject[0].path.rpartition("/")[-1]
                                + "."
                                + field
                                )
                        self.makeRemovePlotAction(label, tab)
                        if (color != '#FFFFFF'):
                            newLines = self.addTimeSeries(tab, label=label,color=color)
                        else:
                            newLines = self.addTimeSeries(tab, label=label)
                        self.pathToLine[tab.path].update(newLines)
                        for line in newLines:
                            self.lineToDataSource[line] = PlotDataSource(x='/clock', y=tab.path, z='')
                    else:
                        for line in lines:
                            dataSrc = self.lineToDataSource[line]
                            xSrc = moose.element(dataSrc.x)
                            ySrc = moose.element(dataSrc.y)
                            if isinstance(xSrc, moose.Clock):
                                ts = np.linspace(0, time, len(tab.vector))
                            elif isinstance(xSrc, moose.Table):
                                ts = xSrc.vector.copy()
                            line.set_data(ts, tab.vector.copy())
                    tabList.append(tab)

            # if len(tabList) > 0:
        self.legend = self.canvas.callAxesFn( 'legend'
                                            , loc='upper right'
                                            , prop= {'size' : 10 }
                                            # , bbox_to_anchor=(1.0, 0.5)
                                            , fancybox = True
                                            , shadow=False
                                            , ncol=1
                                            )
        if self.legend is not None:
            self.legend.draggable()
            self.legend.get_frame().set_alpha(0.5)
            self.legend.set_visible(True)


        self.canvas.draw()

            #     # leg = self.canvas.callAxesFn( 'legend'
            #     #                             , loc               ='upper right'
            #     #                             , prop              = {'size' : 10 }
            #     #                             # , bbox_to_anchor    = (0.5, -0.03)
            #     #                              , fancybox          = False
            #     #                             # , shadow            = True
            #     #                             , ncol              = 1
            #     #                             )
            #     # leg.draggable(False)
            #     # print(leg.get_window_extent())
            #             #leg = self.canvas.callAxesFn('legend')
            #             #leg = self.canvas.callAxesFn('legend',loc='upper left', fancybox=True, shadow=True)
            #             #global legend
            #             #legend =leg
            #     for legobj in leg.legendHandles:
            #         legobj.set_linewidth(5.0)
            #         legobj.set_picker(True)
            # else:
            #     print "returning as len tabId is zero ",tabId, " tableObject ",tableObject, " len ",len(tableObject)

    def togglePlot(self, event):
        #print "onclick",event1.artist.get_label()
        #harsha:To workout with double-event-registered on onclick event
        #http://stackoverflow.com/questions/16278358/double-event-registered-on-mouse-click-if-legend-is-outside-axes
        legline = event.artist
        for line in self.axesRef.lines:
            if line.get_label() == event.artist.get_label():
                vis = not line.get_visible()
                line.set_visible(vis)
                if vis:
                    legline.set_alpha(1.0)
                else:
                    legline.set_alpha(0.2)
                break
        self.canvas.draw()

    def addTimeSeries(self, table, *args, **kwargs):
        ts = np.linspace(0, moose.Clock('/clock').currentTime, len(table.vector))
        return self.canvas.plot(ts, table.vector, *args, **kwargs)

    def addRasterPlot(self, eventtable, yoffset=0, *args, **kwargs):
        """Add raster plot of events in eventtable.

        yoffset - offset along Y-axis.
        """
        y = np.ones(len(eventtable.vector)) * yoffset
        return self.canvas.plot(eventtable.vector, y, '|')

    def updatePlots(self):
        for path, lines in list(self.pathToLine.items()):
            element = moose.element(path)
            if isinstance(element, moose.Table2):
                tab = moose.Table2(path)
            else:
                tab = moose.Table(path)
            data = tab.vector
            ts = np.linspace(0, moose.Clock('/clock').currentTime, len(data))
            for line in lines:
                line.set_data(ts, data)
        self.canvas.draw()

    def extendXAxes(self, xlim):
        for axes in list(self.canvas.axes.values()):
            # axes.autoscale(False, axis='x', tight=True)
            axes.set_xlim(right=xlim)
            axes.autoscale_view(tight=True, scalex=True, scaley=True)
        self.canvas.draw()

    def rescalePlots(self):
        """This is to rescale plots at the end of simulation.

        ideally we should set xlim from simtime.
        """
        for axes in list(self.canvas.axes.values()):
            axes.autoscale(True, tight=True)
            axes.relim()
            axes.autoscale_view(tight=True,scalex=True,scaley=True)
        self.canvas.draw()


    def saveCsv(self, line, directory):
        """Save selected plot data in CSV file"""
        src = self.lineToDataSource[line]
        xSrc = moose.element(src.x)
        ySrc = moose.element(src.y)
        y = ySrc.vector.copy()
        if isinstance(xSrc, moose.Clock):
            x = np.linspace(0, xSrc.currentTime, len(y))
        elif isinstance(xSrc, moose.Table):
            x = xSrc.vector.copy()
        nameVec = ySrc.neighbors['requestOut']
        name = moose.element(nameVec[0]).name
        filename = str(directory)+'/'+'%s.csv' %(name)
        np.savetxt(filename, np.vstack((x, y)).transpose())
        print('Saved data from %s and %s in %s' % (xSrc.path, ySrc.path, filename))

    def saveAllCsv(self):
        """Save data for all currently plotted lines"""
        #Harsha: Plots were saved in GUI folder instead provided QFileDialog box to save to
        #user choose
        fileDialog2 = QtGui.QFileDialog(self)
        fileDialog2.setFileMode(QtGui.QFileDialog.Directory)
        fileDialog2.setWindowTitle('Select Directory to save plots')
        fileDialog2.setOptions(QtGui.QFileDialog.ShowDirsOnly)
        fileDialog2.setLabelText(QtGui.QFileDialog.Accept, self.tr("Save"))
        targetPanel = QtGui.QFrame(fileDialog2)
        targetPanel.setLayout(QtGui.QVBoxLayout())
        layout = fileDialog2.layout()
        layout.addWidget(targetPanel)
        if fileDialog2.exec_():
            directory = fileDialog2.directory().path()
            for line in list(self.lineToDataSource.keys()):
                        self.saveCsv(line,directory)


    def getMenus(self):
        if not hasattr(self, '_menus'):
            self._menus = []
            self.plotAllAction = QtGui.QAction('Plot all data', self)
            self.plotAllAction.triggered.connect(self.plotAllData)
            self.plotMenu = QtGui.QMenu('Plot')
            self.plotMenu.addAction(self.plotAllAction)
            self.saveAllCsvAction = QtGui.QAction('Save all data in CSV files', self)
            self.saveAllCsvAction.triggered.connect(self.saveAllCsv)
            self.plotMenu.addAction(self.saveAllCsvAction)
            self._menus.append(self.plotMenu)
        return self._menus

    # def resizeEvent(self, event):
    #     print("Here", event)
        # self.canvas.figure.subplots_adjust(bottom=0.2)#, left = 0.18)

###################################################
#
# Plot view - select fields to record
#
###################################################
class PlotSelectionWidget(QtGui.QScrollArea):
    """Widget showing the fields of specified elements and their plottable
    fields. User can select any number of fields for plotting and click a
    button to generate the tables for recording data.

    The data tables are by default created under /data. One can call
    setDataRoot with a path to specify alternate location.

    """
    def __init__(self, model, graph, *args):
        QtGui.QScrollArea.__init__(self, *args)
        self.model = moose.element(model.path + "/model")
        self.modelRoot = self.model.path
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().addWidget(self.getPlotListWidget())
        self.setDataRoot(self.model.path)
        self._elementWidgetsDict = {} # element path to corresponding qlabel and fields combo

    def getPlotListWidget(self):
        """An internal widget to display the list of elements and their
        plottable fields in comboboxes."""
        if not hasattr(self, '_plotListWidget'):
            self._plotListWidget = QtGui.QWidget(self)
            layout = QtGui.QGridLayout(self._plotListWidget)
            self._plotListWidget.setLayout(layout)
            layout.addWidget(QtGui.QLabel('<h1>Elements matching search criterion will be listed here</h1>'), 0, 0)
        return self._plotListWidget

    def setSelectedElements(self, elementlist):
        """Create a grid of widgets displaying paths of elements in
        `elementlist` if it has at least one plottable field (a field
        with a numeric value). The numeric fields are listed in a
        combobox next to the element path and can be selected for
        plotting by the user.

        """
        for ii in range(self.getPlotListWidget().layout().count()):
            item = self.getPlotListWidget().layout().itemAt(ii)
            if item is None:
                continue
            self.getPlotListWidget().layout().removeItem(item)
            w = item.widget()
            w.hide()
            del w
            del item
        self._elementWidgetsDict.clear()
        label = QtGui.QLabel('Element')
        label.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.getPlotListWidget().layout().addWidget(label, 0, 0, 1, 2)
        self.getPlotListWidget().layout().addWidget(QtGui.QLabel('Fields to plot'), 0, 2, 1, 1)
        for ii, entry in enumerate(elementlist):
            el = moose.element(entry)
            plottableFields = []
            for field, dtype in  list(moose.getFieldDict(el.className, 'valueFinfo').items()):
                if dtype == 'double':
                    plottableFields.append(field)
            if len(plottableFields) == 0:
                continue
            elementLabel = QtGui.QLabel(el.path)
            fieldsCombo = CheckComboBox(self)
            fieldsCombo.addItem('')
            for item in plottableFields:
                fieldsCombo.addItem(item)
            self.getPlotListWidget().layout().addWidget(elementLabel, ii+1, 0, 1, 2)
            self.getPlotListWidget().layout().addWidget(fieldsCombo, ii+1, 2, 1, 1)
            self._elementWidgetsDict[el] = (elementLabel, fieldsCombo)

    def setModelRoot(self, root):
        pass

    def setDataRoot(self, path):
        """The tables will be created under dataRoot"""
        pass
        self.dataRoot = path

    def getSelectedFields(self):
        """Returns a list containing (element, field) for all selected fields"""
        ret = []
        for el, widgets in list(self._elementWidgetsDict.items()):
            combo = widgets[1]
            for ii in range(combo.count()):
                field = str(combo.itemText(ii)).strip()
                if len(field) == 0:
                    continue
                checked, success = combo.itemData(ii, Qt.CheckStateRole).toInt()
                if success and checked == Qt.Checked:
                    ret.append((el, field))
        return ret

    def setSelectedFields(self, elementFieldList):
        """Set the checked fields for each element in elementFieldList.

        elementFieldList: ((element1, field1), (element2, field2), ...)

        """
        for el, field in elementFieldList:
            combo = self._elementWidgetsDict[el][1]
            idx = combo.findText(field)
            if idx >= 0:
                combo.setItemData(idx, QtCore.QVariant(Qt.Checked), Qt.CheckStateRole)
                combo.setCurrentIndex(idx)
