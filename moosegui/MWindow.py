# -*- coding: utf-8 -*-

# Author: "Subhasis", "HarshaRani","Aviral Goel"
# Maintainer: HarshaRani, Dilawar Singh
# Created: Mon Nov 12 09:38:09 2012 (+0530)

import os
import imp
import inspect
import traceback
import re
import sys
import code

from collections import OrderedDict
from PyQt5 import QtGui, QtCore, Qt
from PyQt5.QtWidgets import QMainWindow, QAction, QApplication
from PyQt5.QtWidgets import QDockWidget, QMdiArea, QMenu
from PyQt5.QtWidgets import QActionGroup, QSizePolicy, QDialog
from PyQt5.QtWidgets import QGridLayout, QPushButton
from PyQt5.QtWidgets import QHBoxLayout, QMessageBox

# moose
import moose

# moosegui
from moosegui import config 
from moosegui import mplugin
from moosegui import mexception
from moosegui import mload
from moosegui.loaderdialog import LoaderDialog
from moosegui.shell import get_shell_class
from moosegui.objectedit import ObjectEditDockWidget
from moosegui.newmodeldialog import DialogWidget
from moosegui.biomodelsclient import BioModelsClientWidget
from moosegui.MdiArea import MdiArea
from moosegui.plugins import defines

# Logger
import logging
logger_ = logging.getLogger("moosegui.window")

# This maps model subtypes to corresponding plugin names. Should be
# moved to a separate property file perhaps
subtype_plugin_map = {  
        'genesis/kkit': 'kkit'
        ,  'cspace/': 'kkit'
        ,  'xml/sbml': 'kkit'
        ,  'xml/neuroml': 'NeuroKit'
        }

def busyCursor():
    app = QtGui.qApp
    app.setOverrideCursor(QtGui.QCursor(Qt.Qt.BusyCursor)) 

def freeCursor():
    app = QtGui.qApp
    app.restoreOverrideCursor()

class MWindow(QMainWindow):
    """The main window for MOOSE GUI.

    This is the driver class that uses the mplugin API. mplugin based
    classes will provide the toolbar, plugin specific menu items and a
    set of panes to be displayed on the docks.

    1. Setting a plugin

       When a plugin is set as the current plugin, the view and the
       menus are updated.

    1.a) Updating menus:

    the plugin can provide its own list of menus by implementing the
    function getMenus().

    the view of the plugin can also provide its own list of
    menus by implementing the function getMenus().

    the currentView provides a set of toolbars that are added to the
    main window.

    1.b) Updating views

    central widget is set to the currentView (a ViewBase instance) of
    the plugin.

    the currentView provides a set of panes that are inserted in the
    right dock area one by one.

    """
    def __init__(self, *args):
        QMainWindow.__init__(self, *args)
        self.setWindowTitle('MOOSE')
        self.pluginNames = None
        self.plugin = None
        self.fileMenu = None
        self.editMenu = None
        self.helpMenu = None
        self.helpActions = None
        self.viewActions = None
        self.editActions = None
        self.connectMenu = None

        self.toolBars       = []
        self._loadedPlugins = {}
        self._plugins       = {}
        self._loadedModels  = []
        self.setUnifiedTitleAndToolBarOnMac(True)
        self.setDockOptions(self.AnimatedDocks and self.AllowNestedDocks and self.AllowTabbedDocks)
        self.mdiArea = MdiArea()

        self.quitAction = QAction('&Quit', self)
        self.quitAction.triggered.connect(self.quit)
        self.quitAction.setShortcut("Ctrl+Q")
        self.getMyDockWidgets()
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.setViewMode(QMdiArea.TabbedView)
        self.mdiArea.subWindowActivated.connect(self.switchSubwindowSlot)
        self.setPlugin('default', '/')
        self.plugin.getEditorView().getCentralWidget().parent().close()
        self.popup = None
        cmdfilepath = ""
        try:
            sys.argv[1]
        except:
            pass
        else:
            cmdfilepath = os.path.abspath(sys.argv[1])

        try:
            sys.argv[2]
        except:
            solver = 'gsl'
        else:
            solver = os.path.abspath(sys.argv[2])

        if cmdfilepath:
            filepath,fileName = os.path.split(cmdfilepath)
            modelRoot,extension = os.path.splitext(fileName)
            if extension == '.py':
                self.setWindowState(QtCore.Qt.WindowMaximized)
                self.show()
                self.createPopup()
                freeCursor()
                reply = QMessageBox.information(self,"Model file can not open","At present python file cann\'t be laoded into GUI", QMessageBox.Ok)
                if reply == QMessageBox.Ok:
                    QApplication.restoreOverrideCursor()
                    return
            if not os.path.exists(cmdfilepath):
                self.setWindowState(QtCore.Qt.WindowMaximized)
                self.show()
                self.createPopup()
                reply = QMessageBox.information(self,"Model file can not open","File Not Found \n \nCheck filename or filepath\n ", QMessageBox.Ok)
                if reply == QMessageBox.Ok:
                    QApplication.restoreOverrideCursor()
                    return
            if os.path.isdir(cmdfilepath):
                self.setWindowState(QtCore.Qt.WindowMaximized)
                self.show()
                self.loadModelDialogFunc(cmdfilepath)
                
            else:
                filePath = filepath+'/'+fileName
                ret = loadFile(str(filePath), '%s' % (modelRoot), solver, merge=False)
                #self.objectEditSlot('/',False)
                self.objectEditSlot(ret['model'].path,False)
                pluginLookup = '%s/%s' % (ret['modeltype'], ret['subtype'])
                try:
                    pluginName = subtype_plugin_map['%s/%s' % (ret['modeltype'], ret['subtype'])]
                except KeyError:
                    pluginName = 'default'
                self.loadedModelsAction(ret['model'].path,pluginName)
                if len(self._loadedModels)>5:
                    self._loadedModels.pop(0)

                if not moose.exists(ret['model'].path+'/info'):
                        moose.Annotator(ret['model'].path+'/info')

                modelAnno = moose.Annotator(ret['model'].path+'/info')
                if ret['subtype']:
                    modelAnno.modeltype = ret['subtype']
                else:
                    modelAnno.modeltype = ret['modeltype']
                #modelAnno.dirpath = str(dialog.directory().absolutePath())
                if moose.exists(ret['model'].path + "/data"):
                    self.data   = moose.element(ret['model'].path + "/data")
                    self.data   = moose.Neutral(ret['model'].path + "/data")

                modelAnno.dirpath = str(filepath)
                self.setPlugin(pluginName, ret['model'].path)
                self.setWindowState(QtCore.Qt.WindowMaximized)
                self.show()
                if pluginName == 'kkit':
                    self.displaymodelInfo(ret)
        else: 
            self.createPopup()

    def createPopup(self):
        self.popup = dialog = QDialog()
        createKineticModelButton = QPushButton("Create Kinetic Model")
        loadKineticModelButton   = QPushButton("Load Model")
        loadNeuronalModelButton  = QPushButton("Load Neuronal Model")

        # setup layout.
        layout = QGridLayout()
        _m = 15
        layout.setContentsMargins(QtCore.QMargins(_m, _m, _m, _m))

        self.menuitems = [
                ("Fig2C" ,            "../moose-examples/paper-2015/Fig2_elecModels/Fig2C.py"),
                ("Fig2D (35s)",       "../moose-examples/paper-2015/Fig2_elecModels/Fig2D.py"),
                ("Fig2E" ,            "../moose-examples/paper-2015/Fig2_elecModels/Fig2E.py"),
                ("Fig3B_Gssa",        "../moose-examples/paper-2015/Fig3_chemModels/Fig3ABC.g"),
                ("Fig3C_Gsl",         "../moose-examples/paper-2015/Fig3_chemModels/Fig3ABC.g"),
                ("Fig3D",             "../moose-examples/paper-2015/Fig3_chemModels/Fig3D.py"),
                ("Fig4B",             "../moose-examples/paper-2015/Fig4_ReacDiff/Fig4B.py"  ),
                ("Fig4K",             "../moose-examples/paper-2015/Fig4_ReacDiff/rxdSpineSize.py"),
                ("Fig5A (20s)",       "../moose-examples/paper-2015/Fig5_CellMultiscale/Fig5A.py"),
                ("Fig5BCD (240s)" ,   "../moose-examples/paper-2015/Fig5_CellMultiscale/Fig5BCD.py"),
                ("Fig6A (60s)",       "../moose-examples/paper-2015/Fig6_NetMultiscale/Fig6A.py" ),
                ("ReducedModel (200s)",   "../moose-examples/paper-2015/Fig6_NetMultiscale/ReducedModel.py"),
                ("Squid" ,            "../moose-examples/squid/squid_demo.py")
                ]
        layout1 = QHBoxLayout()
        layout1.addWidget(createKineticModelButton)
        layout1.addWidget(loadKineticModelButton)
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout4 = QHBoxLayout()
        layout5 = QHBoxLayout()
        layout6 = QHBoxLayout()
        layout7 = QHBoxLayout()
        for i, k in enumerate( self.menuitems ):
            button = QPushButton(k[0])
            if k[0] == "Fig2E":
                button.setToolTip("<span style=\"color:black;\">Illustrates loading a model from an SWC file, inserting  channels, and running it</span>")
            elif k[0] == "Fig2D (35s)":
                button.setToolTip("<span style=\"color:black;\">Illustrates loading a model from an SWC file, inserting  spines, and running it</span>")
            elif k[0] == "Fig2C":
                button.setToolTip("<span style=\"color:black;\">Illustrates building a panel of multiscale models to test neuronal plasticity in different contexts</span>")    
            elif k[0] == "Fig3B_Gssa":
                button.setToolTip("<span style=\"color:black;\">Loades Repressilator model into Gui with Gssa solver and runs the model</span>")
            elif k[0] == "Fig3C_Gsl":
                button.setToolTip("<span style=\"color:black;\">Loades Repressilator model into Gui with Gsl solver and runs the model</span>")
            elif k[0] == "Fig3D":
                button.setToolTip("<span style=\"color:black;\">This example implements a reaction-diffusion like system which is bistable and propagates losslessly</span>")
            elif k[0] == "Fig4B":
                button.setToolTip("<span style=\"color:black;\">This program builds a multiscale model with a few spines inserted into a simplified cellular morphology. Each spine has a signaling model in it too. The program doesn't run the model, it just displays it in 3D</span>")
            elif k[0] == "Fig4K":
                button.setToolTip("<span style=\"color:black;\">Builds a cell with spines and a propagating reaction wave</span>")
            elif k[0] == "Fig5A (20s)":
                button.setToolTip("<span style=\"color:black;\">Illustrates building a panel of multiscale models to test neuronal plasticity in different contexts</span>")
            elif k[0] == "Fig5BCD (240s)":
                button.setToolTip("<span style=\"color:black;\">Illustrates building a panel of multiscale models to test neuronal plasticity in different contexts</span>")
            elif k[0] == "Fig6A (60s)":
                button.setToolTip("<span style=\"color:black;\">This LIF network with Ca plasticity is based on: Memory Maintenance in Synapses with Calcium-Based Plasticity in the Presence of Background Activity PLOS Computational Biology, 2014</span>")
            elif k[0] == "ReducedModel (200s)":
                button.setToolTip("<span style=\"color:black;\">This is the Reduced version of LIF network with Ca plasticity model based on: Memory Maintenance in Synapses with Calcium-Based Plasticity in the Presence of Background Activity PLOS Computational Biology, 2014</span>")
            elif k[0] == "Squid":
                button.setToolTip("<span style=\"color:black;\">squid Demo</span>")
            if k[0] in ["Fig2E","Fig2D (35s)","Fig2C"]:
                layout2.addWidget(button)
            elif k[0] in ["Fig3B_Gssa","Fig3C_Gsl","Fig3D"]:
                layout3.addWidget(button)
            elif k[0] in ["Fig4B","Fig4K"]:
                layout4.addWidget(button)
            elif k[0] in ["Fig5A (20s)","Fig5BCD (240s)"]:
                layout5.addWidget(button)
            elif k[0] in ["Fig6A (60s)","ReducedModel (200s)"]:
                layout6.addWidget(button)
            elif k[0] in ["Squid"]:
                layout7.addWidget(button)

            if k[0] == "Fig3C_Gsl":
                button.clicked.connect(lambda x, script = k[1]: self.run_genesis_script(script,"gsl"))
            elif k[0] == "Fig3B_Gssa":
                button.clicked.connect(lambda x, script = k[1]: self.run_genesis_script(script,"gssa"))
            else:
                button.clicked.connect(lambda x, script = k[1]: self.run_python_script(script))        

        layout.addLayout(layout1,0,0)
        layout.addLayout(layout2,1,0)
        layout.addLayout(layout3,2,0)
        layout.addLayout(layout4,3,0)
        layout.addLayout(layout5,4,0)
        layout.addLayout(layout6,5,0)
        layout.addLayout(layout7,6,0)
        self.popup.setStyleSheet("border:1px solid rgb(0, 0, 0); ")
        self.popup.setLayout(layout)

        createKineticModelButton.clicked.connect(self.newModelDialogSlot)
        loadKineticModelButton.clicked.connect(self.loadModelDialogSlot)
        loadNeuronalModelButton.clicked.connect(self.loadModelDialogSlot)

        # Create the popup and move to the middle of destop app.
        qApp = QApplication.desktop()
        qAppScreen = qApp.screenGeometry();
        self.popup.setGeometry((qAppScreen.bottomLeft().x()+100),(qAppScreen.bottomLeft().y()-250),100,100)
        self.popup.move( qApp.availableGeometry().center() )
        self.popup.setWindowFlags( Qt.Qt.WindowStaysOnTopHint |
                Qt.Qt.X11BypassWindowManagerHint # else it wont go on top.
                )
        self.popup.show()

    def run_genesis_script(self, filepath, solver):
        if self.popup:
            self.popup.hide()
        abspath = os.path.abspath(filepath)
        directory, modulename = os.path.split(abspath)

        modelName = os.path.splitext(modulename)[0]
        ret = mload.loadFile(str(abspath),'%s' %(modelName),solver,merge=False)
        self.setPlugin("kkit", ret["model"].path)
        self.setCurrentView("run")        
        widget = self.plugin.view.getSchedulingDockWidget().widget()
        widget.runSimulation()

    def run_python_script(self, filepath):
        """ Execute a python script """
        busyCursor()
        import subprocess, shlex
        t = os.path.abspath(filepath)
        directory, filename = os.path.split(t)
        logger_.info( "Executing %s" % filepath )
        p = subprocess.Popen([ sys.executable, filename], cwd=directory)
        p.wait()
        freeCursor()

    def quit(self):
        QtGui.qApp.closeAllWindows()

    def handleException(self, t, v, s):
        """
        This handler will show warning messages for error exceptions. Show
        info at status bar for non-error exceptions. It will replace
        sys.excepthook and has the same signature (except being bound
        to this object).

            t : exception type
            v : exception value
            s: traceback object.

        """
        traceback.print_exception(t, v, s)
        title = ''.join(traceback.format_exception_only(t, v))
        trace = ''.join(traceback.format_exception(t, v, s))
        if isinstance(v, mexception.MooseInfo):
            self.statusBar().showMessage(title, 5000)
        elif isinstance(v, mexception.MooseWarning):
            QMessageBox.warning(self, title, '\n'.join((title, trace)))
        else:
            QMessageBox.critical(self, title, '\n'.join((title, trace)))

    def getPluginNames(self):
        """
        Return pluginNames attribute or create it by retrieving
        available plugin names from plugin/list.txt file.
        """
        if self.pluginNames is None:
            pluginF = os.path.join( config.MOOSE_GUI_DIR, 'plugins', 'list.txt' )
            with open( pluginF, 'r' ) as lfile:
                self.pluginNames = [line.strip() for line in lfile]
                self.pluginNames = [name for name in self.pluginNames if name]
        return self.pluginNames

    def loadPluginModule(self, name, _reload=False):
        """Load a plugin module by name.

        First check if the plugin is already loaded. If so return the
        existing one. Otherwise, search load the plugin as a python
        module from {MOOSE_GUI_DIRECTORY}/plugins directory.

        If re is True, the plugin is _reloaded.

        """
        logger_.info("Loading plugin '%s' from %s" % (name, config.MOOSE_PLUGIN_DIR))
        if (not _reload) and name in sys.modules:
            logger_.debug( "\tThis plugin is already loaded" )
            return sys.modules[name]

        fp, pathname, description = imp.find_module(name, [config.MOOSE_PLUGIN_DIR])
        try:
            module = imp.load_module(name, fp, pathname, description)
        except Exception as e:
            module = ""
            extra = traceback.format_exc()
            logger_.warn( "Could not load module %s: '%s'" % (fp, extra))

        if fp: 
            fp.close()
        return module


    def getMyDockWidgets(self):
        """Return a list of dockwidgets that belong to the top
        level. This is needed to keep them separate from those
        provided by the plugins.

        Currently we only have shell for this."""
        if not hasattr(self, 'dockWidgets') or self.dockWidgets is None:
            self.dockWidgets = {}
            dockWidget = QDockWidget('Python')
            dockWidget.setWidget(self.getShellWidget())
            self.dockWidgets[dockWidget] = True
            self.addDockWidget(Qt.Qt.BottomDockWidgetArea, dockWidget)
            dockWidget.setVisible(False)
            dockWidget = ObjectEditDockWidget('/')
            self.dockWidgets[dockWidget] = True
            self.objectEditDockWidget = dockWidget
            self.addDockWidget(Qt.Qt.RightDockWidgetArea, dockWidget)
            dockWidget.setVisible(False)
        return list(self.dockWidgets.keys())

    def getShellWidget(self):
        """
        Create an instance of shell widget. This can be either a
        QSciQScintialla widget or a PyCute widget (extends QTextArea)
        if the first is not available.
        """

        #  raise DeprecationWarning("ShellWidget is no longer supported.")
        if not hasattr(self, 'shellWidget') or self.shellWidget is None:
            self.shellWidget = get_shell_class()( 
                    code.InteractiveInterpreter()
                    , message='MOOSE version %s' % (moose._moose.__version__)
                    )
            self.shellWidget.interpreter.runsource('from moose import *')
            self.shellWidget.setVisible(False)
        return self.shellWidget

    def loadPluginClass(self, name, _reload=False):
        """Load the plugin class from a plugin module.

        A plugin module should have only one subclass of
        MoosePluginBase. Otherwise the first such class found will be
        loaded.
        """
        if name in self._loadedPlugins:
            return self._loadedPlugins[name]

        pluginModule = self.loadPluginModule(name, _reload=_reload)
        for classname, classobj in inspect.getmembers(pluginModule, inspect.isclass):
            if issubclass(classobj, mplugin.MoosePluginBase):
                self._loadedPlugins[name] = classobj
                return self._loadedPlugins[name]

        errMsg = 'No plugin found with name: %s' % name
        errMsg += ". Available: '{}'".format(', '.join(self._loadedPlugins.keys()))
        logger_.error(errMsg)
        raise IndexError(errMsg)

    def setPlugin(self, name, root='/'):
        """Set the current plugin to use.
        1. sets the `plugin` attribute.
        2. updates menus by clearing and reinstating menus including
        anything provided by the plugin.
        3. sets the current view  to the plugins editor view.

        """
        busyCursor()
        for model in self._loadedModels:
            if model[0] != root:
                self.disableModel(model[0])
        for i in range(0, len(self._loadedModels)):
            if self._loadedModels[i][0]== root:
                c = moose.Clock('/clock')
                compts = moose.wildcardFind(root+'/##[ISA=ChemCompt]')
                for simdt in defines.CHEMICAL_SIMULATION_DT_CLOCKS:
                    c.tickDt[simdt] = self._loadedModels[i][3]
                for plotdt in defines.CHEMICAL_PLOT_UPDATE_INTERVAL_CLOCKS:
                    c.tickDt[plotdt] = self._loadedModels[i][4]
        
                if compts:
                    moose.mooseAddChemSolver(self._loadedModels[i][0],"gsl")
                else:
                    c.tickDt[7] = self._loadedModels[i][3]
                    c.tickDt[8] = self._loadedModels[i][4]
                    neurons = moose.wildcardFind(root + "/model/cells/##[ISA=Neuron]")
                    for neuron in neurons:
                        solver = moose.element(neuron.path + "/hsolve")
                        solver.tick = 7
                    for x in moose.wildcardFind( root+'/data/graph#/#' ):
                        x.tick = 8
                break
        
        self.plugin = self.loadPluginClass(str(name))(str(root), self)
        moose.reinit()

        self.updateMenus()
        for action in self.pluginsMenu.actions():
            if str(action.text()) == str(name):
                action.setChecked(True)
            elif action.isChecked():
                action.setChecked(False)
        for subwin in self.mdiArea.subWindowList():
            subwin.close()

        if name != "default" :
            self.setCurrentView('editor')
            self.setCurrentView('run')

        if name == 'kkit':
            self.objectEditDockWidget.objectNameChanged.connect(
                    self.plugin.getEditorView().getCentralWidget().updateItemSlot)
            self.objectEditDockWidget.colorChanged.connect(
                    self.plugin.getEditorView().getCentralWidget().updateColorSlot)
        self.setCurrentView('editor')
        freeCursor()
        return self.plugin

    def updateExistingMenu(self, menu):
        """Check if a menu with same title
        already exists. If so, update the same and return
        True. Otherwise return False.
        """
        if not isinstance(menu, QMenu):
            return False
        for action in self.menuBar().actions():
            if menu.title() == action.text():
                # if not action.menu().isEmpty():
                #     action.menu().addSeparator()
                action.menu().addActions(menu.actions())
                return True
        return False

    def updateMenus(self):
        """Clear the menubar and reinstate the basic menus.  Go
        through the menus provided by current plugin and add those to
        menubar.

        If a menu provided by a plugin has same name as one of the
        core menus, the menu items provided by the plugin are appended
        to the existing menu after a separator.

        """
        self.menuBar().clear()
        self.getPluginsMenu()
        menus = [self.getFileMenu()
                , self.getEditMenu()
                , self.getViewMenu(),
                 self.getHelpMenu()
                 ]
        [ self.menuBar().addMenu(menu) for menu in menus ]

        for menu in self.plugin.getMenus():
            if not self.updateExistingMenu(menu):
                # bug: action was empty here.
                #if not self.menuBar().isEmpty():
                #    action.menu().addSeparator()
                self.menuBar().addMenu(menu)
        menus[0].addSeparator()
        menus[0].addAction(self.quitAction)

    def updateToolbars(self):
        for toolbar in self.toolBars:
            self.removeToolBar(toolbar)
        self.toolBars = []
        self.toolBars.extend(self.getMyToolBars())
        self.toolBars.extend(self.plugin.getToolBars())
        self.toolBars.extend(self.plugin.getCurrentView().getToolBars())
        for toolbar in self.toolBars:
            toolbar.setVisible(True)
            self.addToolBar(toolbar)

    def switchSubwindowSlot(self, window):
        """Change view based on what subwindow `window` is activated."""
        if not window:
            return
        view = str(window.windowTitle()).partition(':')[0]
        self.setCurrentView(view)

    def setCurrentView(self, view):
        """Set current view to a particular one: options are 'editor',
        'plot', 'run'. A plugin can provide more views if necessary.
        """
        self.plugin.setCurrentView(view)
        if view =='run':
            #Harsha: This will clear out object editor's objectpath and make it invisible
            #self.objectEditSlot('/',False)
            self.objectEditDockWidget.setVisible(False)

        targetView = None
        newSubWindow = True
        widget = self.plugin.getCurrentView().getCentralWidget()
        current = self.mdiArea.activeSubWindow()
        subwin = None
        for subwin in self.mdiArea.subWindowList():
            if subwin.widget() == widget:
                newSubWindow = False
                break
        if newSubWindow:
            subwin = self.mdiArea.addSubWindow(widget)
            title = widget.modelRoot+'/model'
            #subwin.setWindowTitle('%s: %s' % (view, widget.modelRoot))
            subwin.setWindowTitle('%s: %s' % (view, title))
            subwin.setSizePolicy(QSizePolicy.Minimum |
                                 QSizePolicy.Expanding,
                                 QSizePolicy.Minimum |
                                 QSizePolicy.Expanding)
            subwin.resize(600, 400)
        # Make dockwidgets from other views invisible and make those
        # from current view visible or add them if not already part of
        # main window.
        dockWidgets = set([dockWidget for dockWidget in self.findChildren(QDockWidget)])
        for dockWidget in dockWidgets:
            if dockWidget not in self.dockWidgets:
                dockWidget.setVisible(False)
        for dockWidget in self.plugin.getCurrentView().getToolPanes():
            if dockWidget not in dockWidgets:
                if view == "run":
                    if dockWidget.windowTitle() == "Scheduling":
                        self.addDockWidget(Qt.Qt.TopDockWidgetArea, dockWidget)
                else:
                    self.addDockWidget(Qt.Qt.RightDockWidgetArea, dockWidget)
            dockWidget.setVisible(True)
        subwin.setVisible(True)
        self.mdiArea.setActiveSubWindow(subwin)
        self.updateMenus()
        for menu in self.plugin.getCurrentView().getMenus():
            if not self.updateExistingMenu(menu):
                self.menuBar().addMenu(menu)
        self.updateToolbars()
        return subwin

    def getMyToolBars(self):
        self._toolBars = []
        '''
        #Harsha: removing the toolbars (plot,run,edit) from the Gui
        if not hasattr(self, 'viewToolBar'):
            self.viewToolBar = QtGui.QToolBar('View')
            #Harsha:removing plotView from the ToolBar
            for t in self.getViewActions():
                if t.text() != "&Plot view":
                    self.viewToolBar.addAction(t)
            #self.viewToolBar.addActions(self.getViewActions())
        #return [self.viewToolBar]
        '''
        return self._toolBars

    def getFileMenu(self):
        if self.fileMenu is None:
            self.fileMenu = QMenu('&File')
        else:
            self.fileMenu.clear()

        if not hasattr(self, 'newModelAction'):
            self.newModelAction = QAction('New', self)
            self.newModelAction.setShortcut("Ctrl+N")
            self.newModelAction.triggered.connect(self.newModelDialogSlot)

        self.fileMenu.addAction(self.newModelAction)
        if not hasattr(self, 'loadModelAction'):
            self.loadModelAction = QAction('L&oad model', self)
            self.loadModelAction.setShortcut("Ctrl+O")
            self.loadModelAction.triggered.connect(self.loadModelDialogSlot)

        self.fileMenu.addAction(self.loadModelAction)

        if not hasattr(self, 'Paper_2015'):
            self.menuitems = OrderedDict([
                ("Fig2C (6s)" ,     "../moose-examples/paper-2015/Fig2_elecModels/Fig2C.py"),
                ("Fig2D (35s)",     "../moose-examples/paper-2015/Fig2_elecModels/Fig2D.py"),
                ("Fig2E (5s)" ,     "../moose-examples/paper-2015/Fig2_elecModels/Fig2E.py"),
                ("Fig3B_Gssa (2s)", "../moose-examples/paper-2015/Fig3_chemModels/Fig3ABC.g"),
                ("Fig3C_Gsl (2s)",  "../moose-examples/paper-2015/Fig3_chemModels/Fig3ABC.g"),
                ("Fig3D (1s)",      "../moose-examples/paper-2015/Fig3_chemModels/Fig3D.py"),
                ("Fig4B (10s)",     "../moose-examples/paper-2015/Fig4_ReacDiff/Fig4B.py"  ),
                ("Fig4K",           "../moose-examples/paper-2015/Fig4_ReacDiff/rxdSpineSize.py"),
                ("Fig5A (20s)",     "../moose-examples/paper-2015/Fig5_CellMultiscale/Fig5A.py"),
                ("Fig5BCD (240s)" , "../moose-examples/paper-2015/Fig5_CellMultiscale/Fig5BCD.py"),
                ("Fig6A (60s)",     "../moose-examples/paper-2015/Fig6_NetMultiscale/Fig6A.py" ),
                ("ReducedModel (200s)", "../moose-examples/paper-2015/Fig6_NetMultiscale/ReducedModel.py"),
                ("Squid" ,          "../moose-examples/squid/squid_demo.py")
                ])
            self.subMenu = QMenu('Demos')
            for i in range(0,len(self.menuitems)):
                k = self.menuitems.popitem(0)
                if k[0] == "Fig2C (6s)":
                    self.Fig2Caction = QAction('Fig2C (6s)', self)
                    self.Fig2Caction.triggered.connect(lambda :self.run_python_script('../moose-examples/paper-2015/Fig2_elecModels/Fig2C.py'))
                    self.subMenu.addAction(self.Fig2Caction)
                elif k[0] == "Fig2D (35s)":
                    self.Fig2Daction = QAction('Fig2D (35s)', self)
                    self.Fig2Daction.triggered.connect(lambda :self.run_python_script('../moose-examples/paper-2015/Fig2_elecModels/Fig2D.py'))
                    self.subMenu.addAction(self.Fig2Daction)
                elif k[0] == "Fig2E (5s)":
                    self.Fig2Eaction = QAction('Fig2E (5s)', self)
                    self.Fig2Eaction.triggered.connect(lambda :self.run_python_script('../moose-examples/paper-2015/Fig2_elecModels/Fig2E.py'))
                    self.subMenu.addAction(self.Fig2Eaction)
                elif k[0] == "Fig3B_Gssa (2s)":
                    self.Fig3B_Gssaaction = QAction('Fig3B_Gssa (2s)', self)
                    self.Fig3B_Gssaaction.triggered.connect(lambda :self.run_genesis_script('../moose-examples/paper-2015/Fig3_chemModels/Fig3ABC.g',"gssa"))
                    self.subMenu.addAction(self.Fig3B_Gssaaction)
                elif k[0] == "Fig3C_Gsl (2s)":
                    self.Fig3C_Gslaction = QAction('Fig3C_Gsl (2s)', self)
                    self.Fig3C_Gslaction.triggered.connect(lambda :self.run_genesis_script('../moose-examples/paper-2015/Fig3_chemModels/Fig3ABC.g',"gsl"))
                    self.subMenu.addAction(self.Fig3C_Gslaction)
                elif k[0] == "Fig3D (1s)":
                    self.Fig3Daction = QAction('Fig3D (1s)', self)
                    self.Fig3Daction.triggered.connect(lambda :self.run_python_script('../moose-examples/paper-2015/Fig3_chemModels/Fig3D.py'))
                    self.subMenu.addAction(self.Fig3Daction)
                elif k[0] == "Fig4B (10s)":
                    self.Fig4Baction = QAction('Fig4B (10s)', self)
                    self.Fig4Baction.triggered.connect(lambda :self.run_python_script('../moose-examples/paper-2015/Fig4_ReacDiff/Fig4B.py'))
                    self.subMenu.addAction(self.Fig4Baction)
                elif k[0] == "Fig4K":
                    self.Fig4Kaction = QAction('Fig4K', self)
                    self.Fig4Kaction.triggered.connect(lambda :self.run_python_script('../moose-examples/paper-2015/Fig4_ReacDiff/rxdSpineSize.py'))
                    self.subMenu.addAction(self.Fig4Kaction)
                elif k[0] == "Fig5A (20s)":
                    self.Fig5Aaction = QAction('Fig5A (20s)', self)
                    self.Fig5Aaction.triggered.connect(lambda :self.run_python_script('../moose-examples/paper-2015/Fig5_CellMultiscale/Fig5A.py'))
                    self.subMenu.addAction(self.Fig5Aaction)
                elif k[0] == "Fig5BCD (240s)":
                    self.Fig5BCDaction = QAction('Fig5BCD (240s)', self)
                    self.Fig5BCDaction.triggered.connect(lambda :self.run_python_script('../moose-examples/paper-2015/Fig5_CellMultiscale/Fig5BCD.py'))
                    self.subMenu.addAction(self.Fig5BCDaction)
                elif k[0] == "Fig6A (60s)":
                    self.Fig6Aaction = QAction('Fig6A (60s)', self)
                    self.Fig6Aaction.triggered.connect(lambda :self.run_python_script('../moose-examples/paper-2015/Fig6_NetMultiscale/Fig6A.py'))
                    self.subMenu.addAction(self.Fig6Aaction)
                elif k[0] == "ReducedModel (200s)":
                    self.ReducedModelaction = QAction('ReducedModel (200s)', self)
                    self.ReducedModelaction.triggered.connect(lambda :self.run_python_script('../moose-examples/paper-2015/Fig6_NetMultiscale/ReducedModel.py'))
                    self.subMenu.addAction(self.ReducedModelaction)
                else:
                    self.Squidaction = QAction('Squid', self)
                    self.Squidaction.triggered.connect(lambda :self.run_python_script('../moose-examples/squid/squid_demo.py'))
                    self.subMenu.addAction(self.Squidaction)  
            self.fileMenu.addMenu(self.subMenu)

        if not hasattr(self,'loadedModels'):
            self.loadedModelAction = QAction('Recently Loaded Models',self)
            self.loadedModelAction.setCheckable(False)
            #self.fileMenu.addAction(QAction(self.loadedModelAction,checkable=True))
            if bool(self._loadedModels):
                self.fileMenu.addSeparator()
                self.fileMenu.addAction(self.loadedModelAction)
                self.loadedModelAction.setEnabled(False)
                for (model, modeltype, action,simdt,plotdt) in reversed(self._loadedModels):
                    self.fileMenu.addAction(action)
                self.fileMenu.addSeparator()

        if not hasattr(self,'connectBioModelAction'):
            self.connectBioModelAction = QAction('&Connect BioModels', self)
            self.connectBioModelAction.setShortcut("Ctrl+B")
            self.connectBioModelAction.triggered.connect(self.connectBioModel)

        self.fileMenu.addAction(self.connectBioModelAction)
        return self.fileMenu

    def getEditMenu(self):
        if self.editMenu is None:
            self.editMenu = QMenu('&Edit')
        else:
            self.editMenu.clear()
        #self.editMenu.addActions(self.getEditActions())
        return self.editMenu

    def getPluginsMenu(self):
        """Populate plugins menu if it does not exist already."""
        if (not hasattr(self, 'pluginsMenu')) or (self.pluginsMenu is None):
            self.pluginsMenu = QMenu('&Plugins')
            mapper = QtCore.QSignalMapper(self)
            pluginsGroup = QActionGroup(self)
            pluginsGroup.setExclusive(True)
            for pluginName in self.getPluginNames():
                action = QAction(pluginName, self)
                action.setObjectName(pluginName)
                action.setCheckable(True)
                mapper.setMapping(action, pluginName)
                action.triggered.connect(mapper.map)
                self.pluginsMenu.addAction(action)
                pluginsGroup.addAction(action)
            mapper.mapped.connect(self.setPlugin)
        return self.pluginsMenu

    def getHelpMenu(self):
        if self.helpMenu is None:
            self.helpMenu = QMenu('&Help')
        else:
            self.helpMenu.clear()
        self.helpMenu.addActions(self.getHelpActions())
        return self.helpMenu
    '''
    def getConnectMenu(self):
        if self.connectMenu is None:
            self.connectMenu = QMenu('&Connect')
        else:
            self.connectMenu.clear()
        self.connectMenu.addActions(self.getConnectActions())
        return self.connectMenu
    '''
    def getViewMenu(self):
        if (not hasattr(self, 'viewMenu')) or (self.viewMenu is None):
            self.viewMenu = QMenu('&View')
        else:
            self.viewMenu.clear()
        self.viewMenu.addActions(self.getViewActions())
        self.docksMenu = self.viewMenu.addMenu('&Dock widgets')
        self.docksMenu.addActions(self.getDockWidgetsToggleActions())
        self.subWindowMenu = self.viewMenu.addMenu('&Subwindows')
        self.subWindowMenu.addActions(self.getSubWindowActions())
        return self.viewMenu

    def getEditActions(self):
        return None

    def showSetModelRootDialog(self):
        root, ok = QtGui.QInputDialog.getText(self, 'Model Root', 'Enter the model root path:', text=moose.element(self.plugin.modelRoot).path)
        if not ok:
            return
        root = str(root) #convert from QString to python str
        self.plugin.setModelRoot(root)
        for subwin in self.mdiArea.subWindowList():
            if hasattr(subwin.widget(), 'modelRoot'):
                subwin.setWindowTitle(root)

    def showSetDataRootDialog(self):
        root, ok = QtGui.QInputDialog.getText(
                self, 'Data Root', 'Enter the data root path:'
                , text=moose.element(self.plugin.dataRoot).path
                )
        if not ok:
            return
        root = str(root) #convert from QString to python str
        self.plugin.setDataRoot(root)
        for subwin in self.mdiArea.subWindowList():
            if hasattr(subwin.widget(), 'dataRoot'):
                subwin.setWindowTitle(root)
        return

    def getViewActions(self):
        if (not hasattr(self, 'viewActions')) or (self.viewActions is None):
            self.editorViewAction = QAction('&Editor view', self)
            self.editorViewAction.triggered.connect(self.openEditorView)
            #self.plotViewAction = QAction('&Plot view', self)
            #self.plotViewAction.triggered.connect(self.openPlotView)
            self.runViewAction = QAction('&Run view', self)
            self.runViewAction.triggered.connect(self.openRunView)
            #self.viewActions = [self.editorViewAction, self.plotViewAction, self.runViewAction]
            self.viewActions = [self.editorViewAction, self.runViewAction]
        return self.viewActions

    def setTabbedView(self):
        self.mdiArea.setViewMode(QMdiArea.TabbedView)

    def setSubWindowView(self):
        self.mdiArea.setViewMode(QMdiArea.SubWindowView)

    def getSubWindowActions(self):
        if not hasattr(self, 'subWindowActions') or self.subWindowActions is None:
            self.tabbedViewAction = QAction('&Tabbed view', self)
            self.tabbedViewAction.triggered.connect(self.setTabbedView)
            self.subWindowViewAction = QAction('&SubWindow view', self)
            self.subWindowViewAction.triggered.connect(self.setSubWindowView)
            self.tileSubWindowsAction = QAction('Ti&le subwindows', self)
            self.tileSubWindowsAction.triggered.connect(self.mdiArea.tileSubWindows)
            self.cascadeSubWindowsAction = QAction('&Cascade subwindows', self)
            self.cascadeSubWindowsAction.triggered.connect(self.mdiArea.cascadeSubWindows)
            self.subWindowActions = [self.tabbedViewAction,
                                     self.subWindowViewAction,
                                     self.tileSubWindowsAction,
                                     self.cascadeSubWindowsAction]
        return self.subWindowActions

    def getDockWidgetsToggleActions(self):
        """Get a list of actions for toggling visibility of dock
        widgets

        """
        return [widget.toggleViewAction() for widget in self.findChildren(QDockWidget)]

    def getHelpActions(self):
        if (not hasattr(self, 'helpActions')) or (self.helpActions is None):
            self.actionAbout = QAction('About MOOSE', self)
            self.actionAbout.triggered.connect(self.showAboutMoose)
            self.actionBuiltInDocumentation = QAction('Built-in documentation', self)
            self.actionBuiltInDocumentation.triggered.connect(self.showBuiltInDocumentation)
            self.actionGuiBug = QAction('Report gui bug', self)
            self.actionGuiBug.triggered.connect(self.reportGuiBug)
            self.actionCoreBug = QAction('Report pymoose bug', self)
            self.actionCoreBug.triggered.connect(self.reportCoreBug)
            self.helpActions = [self.actionAbout, self.actionBuiltInDocumentation
                    , self.actionCoreBug,self.actionGuiBug]
        return self.helpActions


    def connectBioModel(self):
        connecttoBioModel = BioModelsClientWidget()
        if connecttoBioModel.exec_():
            pass
        filepath = connecttoBioModel.filePath
        if filepath:
            head, fileName = os.path.split(filepath)
            modelName = os.path.splitext(fileName)[0]
            pwe = moose.getCwe()
            ret = mload.loadFile(str(filepath), '/model/%s' % (modelName), merge=False)
            self.objectEditSlot('/',False)
            pluginLookup = '%s/%s' % (ret['modeltype'], ret['subtype'])
            try:
                pluginName = subtype_plugin_map['%s/%s' % (ret['modeltype'], ret['subtype'])]
            except KeyError:
                pluginName = 'default'
            self._loadedModels.append([ret['model'].path,pluginName])
            if len(self._loadedModels)>5:
                self._loadedModels.pop(0)

            if not moose.exists(ret['model'].path+'/info'):
                    moose.Annotator(ret['model'].path+'/info')

            modelAnno = moose.Annotator(ret['model'].path+'/info')
            if ret['subtype']:
                modelAnno.modeltype = ret['subtype']
            else:
                modelAnno.modeltype = ret['modeltype']
            modelAnno.dirpath = str(dialog.directory().absolutePath())
            self.loadedModelsAction(ret['model'].path,pluginName)
            self.setPlugin(pluginName, ret['model'].path)


    def showAboutMoose(self):
        about = "<h3>MOOSE simulator</h3>"
        about += '<a href="http://moose.ncbs.res.in">MOOSE Website</a>'
        about += "<p>VERSION " + moose.__version__ + " </p>"
        QMessageBox.about(self, 'About MOOSE', about )

    def showDocumentation(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(config.MOOSE_DOC_URL))

    def reportGuiBug(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(config.MOOSE_GUI_BUG_URL))

    def reportCoreBug(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(config.MOOSE_CORE_BUG_URL))

    def showBuiltInDocumentation(self):
        self.showDocumentation( )

    # openEditorView, openPlotView and openRunView are identical
    # except the view they ask from the plugin. Consider using a
    # mapper.
    def openEditorView(self):
        """Switch to the editor view of current plugin. If there is
        already a subwindow for this, make that the active
        one. Otherwise create a new one.

        """
        self.setCurrentView('editor')

    def openPlotView(self):
        self.setCurrentView('plot')

    def openRunView(self):
        self.setCurrentView('run')

    def resetAndStartSimulation(self):
        """TODO this should provide a clean scheduling through all kinds
        of simulation or default scheduling should be implemented in MOOSE
        itself. We need to define a policy for handling scheduling. It can
        be pushed to the plugin-developers who should have knowledge of
        the scheduling criteria for their domain."""
        settings = config.MooseSetting()
        try:
            simdt_kinetics = float(settings[config.KEY_KINETICS_SIMDT])
        except ValueError:
            simdt_kinetics = 0.1
        try:
            simdt_electrical = float(settings[config.KEY_ELECTRICAL_SIMDT])
        except ValueError:
            simdt_electrical = 0.25e-4
        try:
            plotdt_kinetics = float(settings[config.KEY_KINETICS_PLOTDT])
        except ValueError:
            plotdt_kinetics = 0.1
        try:
            plotdt_electrical = float(settings[config.KEY_ELECTRICAL_PLOTDT])
        except ValueError:
            plotdt_electrical = 0.25e-3
        try:
            simtime = float(settings[config.KEY_SIMTIME])
        except ValueError:
            simtime = 1.0
        moose.reinit()
        view = self.plugin.getRunView()
        moose.start(simtime)

        if view.getCentralWidget().plotAll:
            view.getCentralWidget().plotAllData()
        self.setCurrentView('run')

    def pauseSimulation(self):
        moose.stop()

    '''
    def continueSimulation(self):
        """TODO implement this somewhere else"""
        try:
            simtime = float(config.MooseSetting()[config.KEY_SIMTIME])
        except ValueError:
            simtime = 1.0
        moose.start(simtime)
    '''

    def objectEditSlot(self, mobj, visible=True):
        """Slot for switching the current object in object editor."""
        logger_.debug("objectEditSlot is called: dropped event")
        self.objectEditDockWidget.setObject(mobj)
        self.objectEditDockWidget.setVisible(visible)

    # def objectEditClearSlot(self):
    #     #clearning the views which is stored
    #     self.objectEditDockWidget.clearDict()


    def loadedModelsAction(self,modelPath,pluginName):
        for model in self._loadedModels:
            self.disableModel(model[0])

        action = QAction(modelPath[1:],self)
        action.triggered.connect(lambda : self.setPlugin(pluginName, modelPath))
        compt = moose.wildcardFind(modelPath + '/##[ISA=ChemCompt]')
        c = moose.Clock('/clock')
        self.simulationdt = c.tickDt[7]
        self.plotdt = c.tickDt[8]
        if compt:
            self.simulationdt = c.tickDt[11]
            self.plotdt = c.tickDt[16]

        self._loadedModels.append(
                [ modelPath,pluginName,action,self.simulationdt,self.plotdt ]
                )
        if len(self._loadedModels) > 5:
            self._loadedModels.pop( 0 )

    def disableModel(self, modelPath):
        compt = moose.wildcardFind(modelPath + '/##[ISA=ChemCompt]')
        if compt:
            if moose.exists(compt[0].path+'/ksolve'):
                ksolve = moose.Ksolve( compt[0].path+'/ksolve' )
                ksolve.tick = -1
            if moose.exists(compt[0].path+'/gsolve'):
                gsolve = moose.Gsolve( compt[0].path+'/gsolve' )
                gsolve.tick = -1
            if moose.exists(compt[0].path+'/dsolve'):
                dsolve = moose.Dsolve(compt[0].path+'/dsolve')
                dsolve.tick = -1
            if moose.exists(compt[0].path+'/stoich'):
                stoich = moose.Stoich( compt[0].path+'/stoich' )
                stoich.tick = -1
        
        else :
            neurons = moose.wildcardFind(modelPath + "/model/cells/##[ISA=Neuron]")
            for neuron in neurons:
                solver = moose.element(neuron.path + "/hsolve")
                solver.tick = -1
        for table in moose.wildcardFind( modelPath+'/data/graph#/#' ):
            table.tick = -1

    def loadModelDialogFunc(self,directorypassed):
        """ This is from command line the filepath and file name is passed
        """
        dialog = LoaderDialog(self,
                               self.tr('Load model from file'),directorypassed)
        
        if dialog.exec_():
            self.passtoPluginCheck(dialog)

    def loadModelDialogSlot(self):
        """Start a file dialog to choose a model file.

        Once the dialog succeeds, we should hand-over the duty of
        actual model loading to something else. Then refresh the
        views. Things to check from the user:

        1) The file type

        2) Target element

        3) Whether we should update the current window or start a new
        window.

        4) Plugin to use for displaying this model (can be automated
        by looking into the model file for a regular expression)

        """
        if self.popup:
            self.popup.close()
        activeWindow = None # This to be used later to refresh the current widget with newly loaded model
        dialog = LoaderDialog(self,
                              self.tr('Load model from file'))
        if dialog.exec_():
            self.passtoPluginCheck(dialog)

    def passtoPluginCheck(self, dialog):
        valid = False
        ret = []
        ret,pluginName = self.checkPlugin(dialog)
        valid,ret = self.dialog_check(ret)

        if valid == True:
            modelAnno = moose.Annotator(ret['model'].path+'/info')
            if ret['subtype']:
                modelAnno.modeltype = ret['subtype']
            else:
                modelAnno.modeltype = ret['modeltype']
            modelAnno.dirpath = str(dialog.directory().absolutePath())
            self.loadedModelsAction(ret['model'].path,pluginName)
            self.setPlugin(pluginName, ret['model'].path)
            
            if pluginName == 'kkit':
                self.displaymodelInfo(ret)
    
    def displaymodelInfo(self,ret):
        QtCore.QCoreApplication.sendEvent(self.plugin.getEditorView().getCentralWidget().view, QtGui.QKeyEvent(QtCore.QEvent.KeyPress, Qt.Qt.Key_A, Qt.Qt.NoModifier))
        
        noOfCompt = len(moose.wildcardFind(ret['model'].path+'/##[ISA=ChemCompt]'))
        grp = 0
        for c in moose.wildcardFind(ret['model'].path+'/##[ISA=ChemCompt]'):
            noOfGrp   = moose.wildcardFind(moose.element(c).path+'/#[TYPE=Neutral]')
            grp = grp+len(noOfGrp)

        noOfPool  = len(moose.wildcardFind(ret['model'].path+'/##[ISA=PoolBase]'))
        noOfFunc  = len(moose.wildcardFind(ret['model'].path+'/##[ISA=Function]'))
        noOfReac  = len(moose.wildcardFind(ret['model'].path+'/##[ISA=ReacBase]'))
        noOfEnz   = len(moose.wildcardFind(ret['model'].path+'/##[ISA=EnzBase]'))
        noOfStimtab  = len(moose.wildcardFind(ret['model'].path+'/##[ISA=StimulusTable]'))
        
        reply = QMessageBox.information(self,"Model Info","Model has : \n %s Compartment \t \n %s Group \t \n %s Pool  \t \n %s Function \t \n %s reaction \t \n %s Enzyme \t \n %s StimulusTable" %(noOfCompt, grp, noOfPool, noOfFunc, noOfReac, noOfEnz, noOfStimtab))
        if reply == QMessageBox.Ok:
            QApplication.restoreOverrideCursor()
            return

    def checkPlugin(self,dialog):
        fileNames = dialog.selectedFiles()
        for fileName in fileNames:
            modelName = dialog.getTargetPath()
            if '/' in modelName:
                raise mexception.ElementNameError('Model name cannot contain `/`')
            ret = mload.loadFile(str(fileName),'%s' %(modelName),merge=False)
            #ret = mload.loadFile(str(fileName), '/model/%s' % (modelName), merge=False)
            #This will clear out object editor's objectpath and make it invisible
            self.objectEditSlot('/',False)
            #if subtype is None, in case of cspace then pluginLookup = /cspace/None
            #     which will not call kkit plugin so cleaning to /cspace
            #pluginLookup = '%s/%s' % (ret['modeltype'], ret['subtype'])
            try:
                pluginName = subtype_plugin_map['%s/%s' % (ret['modeltype'], ret['subtype'])]
            except KeyError:
                pluginName = 'default'
            if ret['foundlib']:
                print ('Loaded model %s' %(ret['model']))
            return ret,pluginName

    def dialog_check(self,ret):
        valid = False
        pluginLookup = '%s/%s' % (ret['modeltype'], ret['subtype'])
        try:
            pluginName = subtype_plugin_map['%s/%s' % (ret['modeltype'], ret['subtype'])]
        except KeyError:
            pluginName = 'default'

        if pluginName == 'kkit':
            if (ret['subtype'] == 'sbml' and ret['foundlib'] == False):
                reply = QMessageBox.question(self, "python-libsbml is not found.","\n Read SBML is not possible.\n This can be installed using \n \n pip python-libsbml  or \n apt-get install python-libsbml",
                                           QMessageBox.Ok)
                if reply == QMessageBox.Ok:
                    QApplication.restoreOverrideCursor()
                    return valid, ret
            else:
                if ret['loaderror'] != "":
                    reply = QMessageBox.question(self, "Model can't be loaded", ret['loaderror']+" \n \n Do you want another file",
                                               QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        dialog = LoaderDialog(self,self.tr('Load model from file'))
                        if dialog.exec_():
                            pluginName = None
                            ret,pluginName = self.checkPlugin(dialog)
                            valid,ret = self.dialog_check(ret)
                    else:
                        QApplication.restoreOverrideCursor()
                        return valid,ret
                else:
                    valid = True
        return valid,ret

    def newModelDialogSlot(self):
        #Harsha: Create a new dialog widget for model building
        if self.popup:
            self.popup.close()
        newModelDialog = DialogWidget()
        if newModelDialog.exec_():
            modelPath = str(newModelDialog.modelPathEdit.text()).strip()
            if len(modelPath) == 0:
                raise mexception.ElementNameError('Model path cannot be empty')
            if re.search('[ /]',modelPath) is not None:
                raise mexception.ElementNameError('Model path should not containe / or whitespace')
            plugin = str(newModelDialog.getcurrentRadioButton())
            if moose.exists(modelPath+'/model'):
                moose.delete(modelPath)

            modelContainer = moose.Neutral('%s' %(modelPath))
            modelRoot = moose.Neutral('%s/%s' %(modelContainer.path,"model"))
            if not moose.exists(modelRoot.path+'/info'):
                moose.Annotator(modelRoot.path+'/info')
            
            modelAnno = moose.element(modelRoot.path+'/info')
            modelAnno.modeltype = "new_kkit"
            modelAnno.dirpath = " "
            self.loadedModelsAction(modelRoot.path,plugin)
            self.setPlugin(plugin, modelRoot.path)
            self.objectEditSlot('/', False)
